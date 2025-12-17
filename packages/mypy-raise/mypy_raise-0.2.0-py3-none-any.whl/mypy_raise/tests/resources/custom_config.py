from mypy_raise import raising


# This is a third-party function that we'll configure in mypy.ini
def third_party_function(x: int) -> int:
    """A third-party function that raises CustomError (configured in mypy.ini)."""
    # In reality, this would be from an external library
    # We'll configure it to raise CustomError via mypy.ini
    return x * 2


# Function that calls the third-party function
@raising(exceptions=[])
def calls_third_party():
    """Should detect CustomError from third_party_function (via config)."""
    return third_party_function(5)
