from mypy_raise import raising


@raising(exceptions=[ValueError])
def risky_function(x: int) -> int:
    """Function that raises ValueError."""
    if x < 0:
        raise ValueError('Negative value')
    return x * 2


# Test 1: Exception is caught - should pass
@raising(exceptions=[])
def handles_exception(x: int) -> int:
    """Catches ValueError, so it doesn't propagate."""
    try:
        return risky_function(x)
    except ValueError:
        return 0


# Test 2: Wrong exception caught - should fail
@raising(exceptions=[])
def wrong_exception_caught(x: int) -> int:
    """Catches TypeError but risky_function raises ValueError."""
    try:
        return risky_function(x)
    except TypeError:  # Wrong exception type!
        return 0


# Test 3: Multiple exceptions caught
@raising(exceptions=[])
def multiple_exceptions_caught(x: int, y: str) -> int:
    """Catches ValueError but not TypeError."""
    try:
        result = risky_function(x)
        if not y.isdigit():
            raise TypeError('Not a digit')
        return result
    except ValueError:  # Caught
        return 0
    # TypeError not caught - should be flagged


# Test 4: Tuple of exceptions
@raising(exceptions=[])
def tuple_exception_handler(x: int) -> int:
    """Catches both ValueError and TypeError."""
    try:
        return risky_function(x)
    except (ValueError, TypeError):
        return 0
