import ast
import configparser
import fnmatch
import os
import sys
import traceback

from mypy.nodes import MypyFile
from mypy.options import Options
from mypy.plugin import Plugin

from mypy_raise.raising.checker import (
    compute_exception_propagation,
    find_undeclared_exceptions,
)
from mypy_raise.raising.stdlib_exceptions import get_stdlib_exceptions
from mypy_raise.raising.visitor import RaisingVisitor


class RaisingPlugin(Plugin):
    def __init__(self, options: Options):
        super().__init__(options)
        self.__checked_files: set[str] = set()
        self.__stdlib_exceptions = get_stdlib_exceptions()
        self.__strict_mode = False
        self.__ignore_functions: list[str] = []
        self.__ignore_files: list[str] = []
        self.__load_config(options)

    def __load_config(self, options: Options):
        """Load configuration from mypy.ini."""
        if not options.config_file:
            return

        config = configparser.ConfigParser()
        try:
            config.read(options.config_file)
            if config.has_section('mypy-raise'):
                # Load strict mode
                self.__strict_mode = config.getboolean('mypy-raise', 'strict', fallback=False)

                # Load ignore patterns
                ignore_funcs = config.get('mypy-raise', 'ignore_functions', fallback='')
                self.__ignore_functions = [p.strip() for p in ignore_funcs.split(',') if p.strip()]

                ignore_files = config.get('mypy-raise', 'ignore_files', fallback='')
                self.__ignore_files = [p.strip() for p in ignore_files.split(',') if p.strip()]

                # Load custom exceptions (existing logic)
                self._load_custom_exceptions(config)
        except (OSError, configparser.Error):
            pass

    def _load_custom_exceptions(self, config):
        """Extract custom exception mappings from config."""
        for key, value in config['mypy-raise'].items():
            if key.startswith('exceptions_'):
                # Format: exceptions_function_name = Exception1,Exception2
                func_name = key[11:]  # Remove 'exceptions_' prefix
                exceptions = {exc.strip() for exc in value.split(',') if exc.strip()}
                self.__stdlib_exceptions[func_name] = exceptions

        # Load multiline known_exceptions
        if 'known_exceptions' in config['mypy-raise']:
            raw_data = config.get('mypy-raise', 'known_exceptions')
            # Split by lines
            lines = [line.strip() for line in raw_data.split('\n') if line.strip()]
            for line in lines:
                if ':' in line:
                    func_name, exceptions_str = line.split(':', 1)
                    func_name = func_name.strip()
                    exceptions = {exc.strip() for exc in exceptions_str.split(',') if exc.strip()}
                    self.__stdlib_exceptions[func_name] = exceptions

    def get_additional_deps(self, file: MypyFile) -> list[tuple[int, str, int]]:
        if file.fullname in self.__checked_files:
            return []

        if file.fullname.startswith(('builtins', 'typing', 'sys', 'os', 'abc', 'enum', 'mypy.', '_')):
            return []

        self.__checked_files.add(file.fullname)

        try:
            if not file.path:
                return []

            # If file.path is a directory (mypy may pass packages), skip
            if os.path.isdir(file.path):
                return []

            # Check ignore patterns for file
            for pattern in self.__ignore_files:
                if fnmatch.fnmatch(file.path, pattern):
                    return []

            with open(file.path, 'r', encoding='utf-8') as f:
                source = f.read()

            tree = ast.parse(source, filename=file.path)
            visitor = RaisingVisitor()
            visitor.visit(tree)

            # Extract @raising decorator declarations via AST and merge
            declared_by_decorator, decorator_linenos = self._extract_raising_decorators(tree)
            for func_name, excs in declared_by_decorator.items():
                # If decorator explicitly set exceptions=None, do not track this function
                if excs is None:
                    # remove any existing tracking for both qualified and unqualified names
                    if func_name in visitor.function_exceptions:
                        visitor.function_exceptions.pop(func_name, None)
                    if '.' in func_name:
                        short = func_name.split('.', 1)[1]
                        visitor.function_exceptions.pop(short, None)
                    # also remove lineno entries
                    visitor.function_linenos.pop(func_name, None)
                    if '.' in func_name:
                        visitor.function_linenos.pop(short, None)
                    continue

                # Ensure we have a set to update
                if func_name not in visitor.function_exceptions:
                    visitor.function_exceptions[func_name] = set()
                visitor.function_exceptions[func_name].update(excs)
                # Also add unqualified name for methods so calls recorded as Class.method or method match
                if '.' in func_name:
                    short = func_name.split('.', 1)[1]
                    if short not in visitor.function_exceptions:
                        visitor.function_exceptions[short] = set()
                    visitor.function_exceptions[short].update(excs)

                # Merge line numbers for both variants
                if func_name not in visitor.function_linenos:
                    visitor.function_linenos[func_name] = decorator_linenos.get(func_name, 1)
                if '.' in func_name:
                    short = func_name.split('.', 1)[1]
                    if short not in visitor.function_linenos:
                        visitor.function_linenos[short] = decorator_linenos.get(func_name, 1)

            if not visitor.function_exceptions and not self.__strict_mode:
                # No decorated functions to check, and not in strict mode
                return []

            # Strict Mode: Check for undecorated functions
            if self.__strict_mode:
                self._check_strict_mode(file.path, visitor, tree)

            # Compute exception propagation
            actual_exceptions, exception_sources = compute_exception_propagation(
                call_graph=visitor.calls,
                function_exceptions=visitor.function_exceptions,
                explicit_raises=visitor.explicit_raises,
                stdlib_exceptions=self.__stdlib_exceptions,
                caught_exceptions=visitor.caught_exceptions,
            )

            # Find undeclared exceptions
            undeclared = find_undeclared_exceptions(
                function_exceptions=visitor.function_exceptions,
                actual_exceptions=actual_exceptions,
            )

            # Report errors
            for func_name, missing_exceptions in undeclared.items():
                if self._should_ignore_function(func_name):
                    continue

                lineno = visitor.function_linenos.get(func_name, 1)

                # Build detailed error message
                if missing_exceptions:
                    msg = self._format_error_message(
                        file_path=file.path,
                        lineno=lineno,
                        func_name=func_name,
                        missing_exceptions=missing_exceptions,
                        sources=exception_sources.get(func_name, {}),
                    )

                    sys.stdout.write(msg)
                    sys.stdout.flush()

        except Exception as exc:
            print(exc, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

        return []

    def _check_strict_mode(self, file_path: str, visitor: RaisingVisitor, tree: ast.Module) -> None:
        """Check for functions missing @raising decorator in strict mode."""
        all_functions = self._find_all_functions(tree)
        decorated_functions = set(visitor.function_exceptions.keys())
        undecorated = all_functions - decorated_functions

        for func_name in undecorated:
            # Skip ignored functions
            if self._should_ignore_function(func_name):
                continue

            # Report at file level (line 1 approximate location)
            lineno = 1

            msg = f'{file_path}:{lineno}: error: '
            msg += f"Function '{func_name}' missing @raising decorator (strict mode)\n"
            sys.stdout.write(msg)
            sys.stdout.flush()

    def _find_all_functions(self, tree: ast.Module) -> set[str]:
        """Find all function definitions in the file."""
        functions = set()
        for defn in tree.body:
            if isinstance(defn, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.add(defn.name)
            elif isinstance(defn, ast.ClassDef):
                for item in defn.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        functions.add(f'{defn.name}.{item.name}')
        return functions

    def _should_ignore_function(self, func_name: str) -> bool:
        """Check if function matches ignore patterns."""
        for pattern in self.__ignore_functions:
            if fnmatch.fnmatch(func_name, pattern):
                return True
        return False

    def _format_error_message(
        self,
        file_path: str,
        lineno: int,
        func_name: str,
        missing_exceptions: set[str],
        sources: dict[str, set[str]],
    ) -> str:
        """Format enhanced error message with context and hints."""
        exc_list = ', '.join(f"'{exc}'" for exc in sorted(missing_exceptions))

        msg = f'{file_path}:{lineno}: error: '
        msg += f"Function '{func_name}' may raise {exc_list} but these are not declared.\n"

        # Add hint
        exc_hint = ', '.join(sorted(missing_exceptions))
        hint_text = f'  💡 Hint: Add to decorator: @raising(exceptions=[{exc_hint}])'
        msg += f'{hint_text}\n'

        # Add source information
        if sources:
            msg += '  📍 Raised by:\n'
            relevant_sources = []
            for called_func, excs in sources.items():
                relevant = excs & missing_exceptions
                if relevant:
                    exc_names = ', '.join(f"'{e}'" for e in sorted(relevant))
                    relevant_sources.append(f"'{called_func}' raises {exc_names}")

            # Sort sources for deterministic output
            for source in sorted(relevant_sources):
                msg += f'     - {source}\n'

        return msg

    def _decorator_is_raising(self, dec: ast.expr) -> bool:
        """Return True if the decorator expression represents `raising` (call or name/attr)."""
        if isinstance(dec, ast.Call):
            func = dec.func
        else:
            func = dec
        if isinstance(func, ast.Name):
            return func.id == 'raising'
        if isinstance(func, ast.Attribute):
            return func.attr == 'raising'
        return False

    def _extract_exceptions_from_expr(self, expr: ast.expr) -> set[str] | None:
        """Extract exception names from an expression used in decorator args.

        Return None when the decorator explicitly uses `exceptions=None` (meaning don't track).
        Otherwise return a set of exception names (possibly empty for []).
        """
        exceptions: set[str] = set()
        # Handle explicit None: exceptions=None => don't track
        if isinstance(expr, ast.Constant) and expr.value is None:
            return None
        if isinstance(expr, (ast.List, ast.Tuple, ast.Set)):
            for el in expr.elts:
                if isinstance(el, ast.Constant):
                    # Constants (strings/numbers) - represent exception by their value
                    if el.value is not None:
                        exceptions.add(str(el.value))
                elif isinstance(el, ast.Name):
                    exceptions.add(el.id)
                elif isinstance(el, ast.Attribute):
                    exceptions.add(el.attr)
        elif isinstance(expr, ast.Constant):
            # Single constant (string or number)
            if expr.value is not None:
                exceptions.add(str(expr.value))
        elif isinstance(expr, ast.Name):
            exceptions.add(expr.id)
        elif isinstance(expr, ast.Attribute):
            exceptions.add(expr.attr)
        return exceptions

    def _extract_raising_decorators(self, tree: ast.Module) -> tuple[dict[str, set[str] | None], dict[str, int]]:
        """
        Walk the AST and find functions/methods decorated with @raising(...).
        Returns a tuple of (mapping func_name -> set[exceptions] or None, mapping func_name -> lineno).
        """
        declared: dict[str, set[str] | None] = {}
        linenos: dict[str, int] = {}

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Determine qualified name (ClassName.func if inside class)
                qual_name = node.name
                class_name = self._find_enclosing_class_name(tree, node)
                if class_name:
                    qual_name = f'{class_name}.{node.name}'

                for dec in node.decorator_list:
                    if self._decorator_is_raising(dec):
                        exceptions: set[str] | None = set()
                        if isinstance(dec, ast.Call):
                            # look for keyword 'exceptions' or first positional arg
                            found = False
                            for kw in dec.keywords:
                                if kw.arg == 'exceptions':
                                    exceptions = self._extract_exceptions_from_expr(kw.value)
                                    found = True
                                    break
                            if not found and dec.args:
                                exceptions = self._extract_exceptions_from_expr(dec.args[0])
                        # If decorator was plain @raising without args, keep empty set (handled elsewhere)
                        declared[qual_name] = exceptions
                        linenos[qual_name] = getattr(node, 'lineno', 1)

            # Also handle methods inside classes explicitly (covered above because ast.walk sees them)
        return declared, linenos

    def _find_enclosing_class_name(self, tree: ast.Module, node: ast.AST) -> str | None:
        """Find the immediate enclosing class name for a function node, if any."""
        # Walk tree and find a ClassDef that contains the function node in its body
        for defn in tree.body:
            if isinstance(defn, ast.ClassDef):
                for item in defn.body:
                    if item is node:
                        return defn.name
        # For nested classes or deeper nesting, fallback to scanning all ClassDefs
        for classnode in [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]:
            for item in classnode.body:
                if item is node:
                    return classnode.name
        return None


def plugin(version: str) -> type[RaisingPlugin]:
    return RaisingPlugin
