from mypy_raise.raising.stdlib_exceptions import is_subtype
from mypy_raise.raising.types import (
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
    # ...existing code...
    actual_exceptions: ExceptionPropagationMap = {}

    exception_sources: dict[FuncName, dict[FuncName, ExceptionSet]] = {}

    for func_name in function_exceptions.keys():
        actual_exceptions[func_name] = set()
        exception_sources[func_name] = {}

        if func_name in explicit_raises:
            for lineno, exc_name in explicit_raises[func_name]:
                actual_exceptions[func_name].add(exc_name)

    max_iterations = 100
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

                if called_func in function_exceptions:
                    called_exceptions = actual_exceptions.get(called_func, set()).copy()
                    if not called_exceptions and '.' in called_func:
                        method_name = called_func.split('.')[-1]
                        called_exceptions = actual_exceptions.get(method_name, set()).copy()

                elif called_func in stdlib_exceptions:
                    called_exceptions = stdlib_exceptions[called_func].copy()

                elif f'builtins.{called_func}' in stdlib_exceptions:
                    called_exceptions = stdlib_exceptions[f'builtins.{called_func}'].copy()

                elif '.' in called_func:
                    method_name = called_func.split('.')[-1]
                    if method_name in function_exceptions:
                        if method_name in actual_exceptions:
                            called_exceptions = actual_exceptions[method_name].copy()

                if called_exceptions:
                    if called_func not in exception_sources[func_name]:
                        exception_sources[func_name][called_func] = set()
                    exception_sources[func_name][called_func].update(called_exceptions)

                    before_size = len(actual_exceptions[func_name])
                    actual_exceptions[func_name].update(called_exceptions)
                    if len(actual_exceptions[func_name]) > before_size:
                        changed = True

    for func_name in function_exceptions.keys():
        if func_name in caught_exceptions:
            caught = caught_exceptions[func_name]

            if func_name in actual_exceptions:
                to_remove = set()
                for exc in actual_exceptions[func_name]:
                    for caught_exc in caught:
                        if is_subtype(exc, caught_exc):
                            to_remove.add(exc)
                            break
                actual_exceptions[func_name] -= to_remove

            if func_name in exception_sources:
                for called_func in list(exception_sources[func_name].keys()):
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
    undeclared: dict[FuncName, ExceptionSet] = {}

    for func_name, declared in function_exceptions.items():
        if func_name in actual_exceptions:
            actual = actual_exceptions[func_name]
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
