from mypy_raise import raising


@raising(exceptions=[ValueError])
def risky_function(x: int) -> int:
    """Function that raises ValueError."""
    if x < 0:
        raise ValueError('Negative value')
    return x * 2


# Function that catches the exception - NO @raising decorator
# This function is not tracked by the plugin
def handles_exception(x: int) -> int:
    """Function that catches ValueError, so it doesn't propagate."""
    try:
        return risky_function(x)
    except ValueError:
        # Exception is caught and handled
        return 0


# Another untracked function that calls the handler
def calls_handler() -> int:
    """Calls handles_exception which catches all exceptions."""
    return handles_exception(-5)
