from mypy_raise import raising


# Test decorator with None (should not be tracked)
@raising(exceptions=None)
def not_tracked():
    raise ValueError("This won't be tracked")


# Test calling not_tracked function
@raising(exceptions=[])
def calls_not_tracked():
    not_tracked()  # Should not report error since not_tracked isn't tracked
