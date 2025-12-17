import ast

from mypy_raise.raising.types import (
    CallGraph,
    ExceptionSet,
    ExplicitRaises,
    FuncName,
    FunctionExceptionsMap,
    LineNo,
)


class RaisingVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        # func_name -> set of declared exception names
        self.__function_exceptions: FunctionExceptionsMap = {}
        # func_name -> lineno where decorator is
        self.__function_linenos: dict[FuncName, LineNo] = {}
        # func_name -> list of (lineno, called_func_name)
        self.__calls: CallGraph = {}
        # func_name -> list of (lineno, exception_name) for explicit raises
        self.__explicit_raises: ExplicitRaises = {}
        # func_name -> set of exception names caught in try-except blocks
        self.__caught_exceptions: FunctionExceptionsMap = {}

        self.__current_function: FuncName | None = None

    @property
    def function_exceptions(self) -> FunctionExceptionsMap:
        """Map of function names to their declared exceptions."""
        return self.__function_exceptions

    @property
    def function_linenos(self) -> dict[FuncName, LineNo]:
        """Map of function names to their decorator line numbers."""
        return self.__function_linenos

    @property
    def calls(self) -> CallGraph:
        return self.__calls

    @property
    def explicit_raises(self) -> ExplicitRaises:
        return self.__explicit_raises

    @property
    def caught_exceptions(self) -> FunctionExceptionsMap:
        """Map of function names to exceptions they catch in try-except blocks."""
        return self.__caught_exceptions

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function_def(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function_def(node)

    def _process_function_def(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        """Process both regular and async function definitions."""
        previous_function = self.__current_function
        self.__current_function = node.name

        # Check for @raising decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                # Check if it's the @raising decorator
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'raising':
                    # Extract the exceptions parameter
                    exceptions_arg = None
                    for keyword in decorator.keywords:
                        if keyword.arg == 'exceptions':
                            exceptions_arg = keyword.value
                            break

                    if exceptions_arg is not None:
                        # Parse the exceptions list
                        if isinstance(exceptions_arg, ast.Constant) and exceptions_arg.value is None:
                            # exceptions=None means don't track this function
                            pass
                        elif isinstance(exceptions_arg, ast.List):
                            # Extract exception names from the list
                            exception_names: ExceptionSet = set()
                            for elt in exceptions_arg.elts:
                                exc_name = self.__extract_exception_name(elt)
                                if exc_name:
                                    exception_names.add(exc_name)

                            self.__function_exceptions[node.name] = exception_names
                            self.__function_linenos[node.name] = decorator.lineno

        # Only visit the body to avoid treating decorators as calls inside the function
        for item in node.body:
            self.visit(item)

        self.__current_function = previous_function

    def __extract_exception_name(self, node: ast.AST) -> str | None:
        """Extract exception name from AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            # Handle module.Exception format
            parts = []
            current: ast.AST = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            parts.reverse()
            return '.'.join(parts)
        return None

    def visit_Try(self, node: ast.Try) -> None:
        """Track exceptions caught in try-except blocks."""
        if self.__current_function:
            for handler in node.handlers:
                # handler.type can be None (bare except), Name, or Tuple
                if handler.type:
                    if isinstance(handler.type, ast.Name):
                        # Single exception: except ValueError:
                        exc_name = handler.type.id
                        if self.__current_function not in self.__caught_exceptions:
                            self.__caught_exceptions[self.__current_function] = set()
                        self.__caught_exceptions[self.__current_function].add(exc_name)
                    elif isinstance(handler.type, ast.Tuple):
                        # Multiple exceptions: except (ValueError, TypeError):
                        for elt in handler.type.elts:
                            caught_exc = self.__extract_exception_name(elt)
                            if caught_exc:
                                if self.__current_function not in self.__caught_exceptions:
                                    self.__caught_exceptions[self.__current_function] = set()
                                self.__caught_exceptions[self.__current_function].add(caught_exc)

        # Continue visiting child nodes
        self.generic_visit(node)

    def visit_Raise(self, node: ast.Raise) -> None:
        if self.__current_function:
            exc_name = 'Unknown'
            if isinstance(node.exc, ast.Call) and isinstance(node.exc.func, ast.Name):
                exc_name = node.exc.func.id
            elif isinstance(node.exc, ast.Name):
                exc_name = node.exc.id
            elif node.exc is None:
                # Bare raise statement
                exc_name = 'Unknown'

            if self.__current_function not in self.__explicit_raises:
                self.__explicit_raises[self.__current_function] = []
            self.__explicit_raises[self.__current_function].append((node.lineno, exc_name))

    def visit_Call(self, node: ast.Call) -> None:
        if self.__current_function:
            func_name = ''
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            # Handle simple module.func calls (e.g. os.path.join)
            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                func_name = f'{node.func.value.id}.{node.func.attr}'
            # Handle chained attributes (e.g. os.path.join)
            elif isinstance(node.func, ast.Attribute):
                func_name = self.__resolve_attribute(node.func)

            if func_name:
                if self.__current_function not in self.__calls:
                    self.__calls[self.__current_function] = []
                self.__calls[self.__current_function].append((node.lineno, func_name))

    def __resolve_attribute(self, node: ast.Attribute) -> str:
        """Resolve chained attribute access to a string."""
        parts = []
        current: ast.AST = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
        return '.'.join(reversed(parts))
