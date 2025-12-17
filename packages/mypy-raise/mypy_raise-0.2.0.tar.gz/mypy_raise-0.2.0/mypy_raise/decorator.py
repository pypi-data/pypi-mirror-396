from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar('T', bound=Callable[..., Any])


def raising(exceptions: list[type[BaseException]] | None = None) -> Callable[[T], T]:
    """
    Decorator to mark a function with the exceptions it may raise.

    Args:
        exceptions: List of exception types this function may raise.
                   Empty list [] means the function raises no exceptions.
                   None means exceptions are not tracked (default).

    Example:
        @raising(exceptions=[])  # Function raises no exceptions
        def safe_function():
            pass

        @raising(exceptions=[ValueError, TypeError])  # Function may raise these
        def risky_function(x):
            if not isinstance(x, int):
                raise TypeError
            if x < 0:
                raise ValueError

        @raising(exceptions=[FileNotFoundError, PermissionError, OSError])
        def read_config(filename):
            # Must declare exceptions from stdlib functions like open()
            with open(filename) as f:
                return f.read()
    """

    def decorator(func: T) -> T:
        return func

    return decorator
