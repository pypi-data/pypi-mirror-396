from mypy_raise import raising


def risky_operation():
    pass


# Test bare raise statement
@raising(exceptions=[])
def handle_error():
    try:
        risky_operation()
    except Exception:
        raise  # Bare raise - should be tracked
