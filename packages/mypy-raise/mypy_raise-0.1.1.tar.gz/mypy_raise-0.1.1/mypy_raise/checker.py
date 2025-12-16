from mypy_raise.stdlib_exceptions import is_subtype
from mypy_raise.types import (
    CallGraph,
    ExceptionPropagationMap,
    ExceptionSet,
    ExplicitRaises,
    FuncName,
    FunctionExceptionsMap,
)


def compute_exception_propagation(
    call_graph: CallGraph,
    function_exceptions: FunctionExceptionsMap,
    explicit_raises: ExplicitRaises,
    stdlib_exceptions: FunctionExceptionsMap,
    caught_exceptions: FunctionExceptionsMap,
) -> tuple[ExceptionPropagationMap, dict[FuncName, dict[FuncName, ExceptionSet]]]:
    """
    Compute which exceptions each function can raise by analyzing the call graph.

    This function traverses the call graph to determine all exceptions that can be
    raised by each function, including:
    1. Exceptions explicitly raised in the function
    2. Exceptions from called functions
    3. Exceptions from standard library functions

    Args:
        call_graph: Map of function -> list of (lineno, called_function)
        function_exceptions: Map of function -> declared exceptions
        explicit_raises: Map of function -> list of (lineno, exception)
        stdlib_exceptions: Map of stdlib function -> exceptions it raises

    Returns:
        Tuple of:
        - ExceptionPropagationMap: Map of function -> all exceptions it can raise
        - Dict mapping function -> dict of (called_func -> exceptions from that call)
    """
    # Build a map of function -> all exceptions it can actually raise
    actual_exceptions: ExceptionPropagationMap = {}

    # Track which functions contribute which exceptions (for error messages)
    exception_sources: dict[FuncName, dict[FuncName, ExceptionSet]] = {}

    # First pass: collect explicit raises for all functions
    for func_name in function_exceptions.keys():
        actual_exceptions[func_name] = set()
        exception_sources[func_name] = {}

        # Add explicitly raised exceptions
        if func_name in explicit_raises:
            for lineno, exc_name in explicit_raises[func_name]:
                actual_exceptions[func_name].add(exc_name)

    # Iteratively propagate exceptions through the call graph
    # We need multiple passes because of indirect calls
    max_iterations = 100  # Prevent infinite loops
    changed = True
    iteration = 0

    while changed and iteration < max_iterations:
        changed = False
        iteration += 1

        for func_name in function_exceptions.keys():
            if func_name not in call_graph:
                continue

            for lineno, called_func in call_graph[func_name]:
                called_exceptions: ExceptionSet = set()

                # Check if it's a decorated function
                # Check if it's a decorated function
                if called_func in function_exceptions:
                    # Get exceptions from the called function
                    if called_func in actual_exceptions:
                        called_exceptions = actual_exceptions[called_func].copy()

                # Check if it's a stdlib function (or configured custom exception)
                elif called_func in stdlib_exceptions:
                    called_exceptions = stdlib_exceptions[called_func].copy()

                # Also check with 'builtins.' prefix
                elif f'builtins.{called_func}' in stdlib_exceptions:
                    called_exceptions = stdlib_exceptions[f'builtins.{called_func}'].copy()

                # Try stripping class prefix for method calls (e.g., MyClass.method -> method)
                # Only do this if we haven't found it yet
                elif '.' in called_func:
                    method_name = called_func.split('.')[-1]
                    if method_name in function_exceptions:
                        if method_name in actual_exceptions:
                            called_exceptions = actual_exceptions[method_name].copy()

                # If we found exceptions from this call
                if called_exceptions:
                    # Track the source of these exceptions
                    if called_func not in exception_sources[func_name]:
                        exception_sources[func_name][called_func] = set()
                    exception_sources[func_name][called_func].update(called_exceptions)

                    # Add to actual exceptions
                    before_size = len(actual_exceptions[func_name])
                    actual_exceptions[func_name].update(called_exceptions)
                    if len(actual_exceptions[func_name]) > before_size:
                        changed = True

    # Subtract caught exceptions - they don't propagate
    for func_name in function_exceptions.keys():
        if func_name in caught_exceptions:
            # We must remove exceptions that are subtypes of any caught exception
            caught = caught_exceptions[func_name]

            # Filter actual_exceptions
            if func_name in actual_exceptions:
                to_remove = set()
                for exc in actual_exceptions[func_name]:
                    for caught_exc in caught:
                        if is_subtype(exc, caught_exc):
                            to_remove.add(exc)
                            break
                actual_exceptions[func_name] -= to_remove

            # Filter exception sources
            if func_name in exception_sources:
                for called_func in list(exception_sources[func_name].keys()):
                    # Identify exceptions to remove from this source
                    source_excs = exception_sources[func_name][called_func]
                    to_remove_source = set()

                    for exc in source_excs:
                        for caught_exc in caught:
                            if is_subtype(exc, caught_exc):
                                to_remove_source.add(exc)
                                break

                    exception_sources[func_name][called_func] -= to_remove_source

                    if not exception_sources[func_name][called_func]:
                        del exception_sources[func_name][called_func]

    return actual_exceptions, exception_sources


def find_undeclared_exceptions(
    function_exceptions: FunctionExceptionsMap,
    actual_exceptions: ExceptionPropagationMap,
) -> dict[FuncName, ExceptionSet]:
    """
    Find exceptions that are raised but not declared in the decorator.

    Args:
        function_exceptions: Map of function -> declared exceptions
        actual_exceptions: Map of function -> all exceptions it can raise

    Returns:
        Map of function -> undeclared exceptions
    """
    undeclared: dict[FuncName, ExceptionSet] = {}

    for func_name, declared in function_exceptions.items():
        if func_name in actual_exceptions:
            actual = actual_exceptions[func_name]
            # Instead of strict set difference, we check if each actual exception
            # is a subtype of any declared exception.
            missing = set()
            for exc in actual:
                is_handled = False
                for declared_exc in declared:
                    if is_subtype(exc, declared_exc):
                        is_handled = True
                        break
                if not is_handled:
                    missing.add(exc)

            if missing:
                undeclared[func_name] = missing

    return undeclared
