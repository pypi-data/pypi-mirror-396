import ast
import atexit
import configparser
import fnmatch
import sys

from mypy.nodes import MypyFile
from mypy.options import Options
from mypy.plugin import Plugin

from mypy_raise.checker import compute_exception_propagation, find_undeclared_exceptions
from mypy_raise.colors import Colors
from mypy_raise.stats import STATS
from mypy_raise.stdlib_exceptions import get_stdlib_exceptions
from mypy_raise.visitor import RaisingVisitor


def print_stats():
    """Print analysis statistics at exit."""
    if STATS.files_checked > 0:
        sys.stdout.write(STATS.format_summary() + '\n')
        sys.stdout.flush()


atexit.register(print_stats)


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
        STATS.files_checked += 1

        try:
            if not file.path:
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

            if not visitor.function_exceptions and not self.__strict_mode:
                # No decorated functions to check, and not in strict mode
                return []

            # Count functions analyzed
            STATS.functions_checked += len(visitor.function_exceptions)

            # Count caught exceptions
            for excs in visitor.caught_exceptions.values():
                STATS.exceptions_caught += len(excs)

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
                    STATS.violations_found += 1
                    msg = self._format_error_message(
                        file_path=file.path,
                        lineno=lineno,
                        func_name=func_name,
                        missing_exceptions=missing_exceptions,
                        sources=exception_sources.get(func_name, {}),
                    )

                    sys.stdout.write(msg)
                    sys.stdout.flush()

        except Exception:
            pass

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

            msg = f"{file_path}:{lineno}: {Colors.error('error')}: "
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

        msg = f"{file_path}:{lineno}: {Colors.error('error')}: "
        msg += f"Function '{func_name}' may raise {exc_list} but these are not declared.\n"

        # Add hint
        exc_hint = ', '.join(sorted(missing_exceptions))
        hint_text = f'  💡 Hint: Add to decorator: @raising(exceptions=[{exc_hint}])'
        msg += f'{Colors.hint(hint_text)}\n'

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


def plugin(version: str) -> type[RaisingPlugin]:
    return RaisingPlugin
