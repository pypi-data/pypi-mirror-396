from mypy_raise import raising


@raising(exceptions=[])
def safe():
    pass
