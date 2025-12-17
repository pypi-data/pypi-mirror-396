from mypy_raise import raising


def unknown():
    pass


@raising(exceptions=[])
def unsafe_call():
    unknown()
