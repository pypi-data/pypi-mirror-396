from mypy_raise import raising


# Test exception name extraction
@raising(exceptions=[ValueError])
def raise_value_error():
    raise ValueError('Error')
