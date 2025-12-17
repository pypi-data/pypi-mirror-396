from mypy_raise import raising


@raising(exceptions=[])
def safe():
    pass


@raising(exceptions=[])
def safe_call():
    safe()
