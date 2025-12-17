from mypy_raise import raising


@raising(exceptions=[ValueError])
def raiser():
    raise ValueError


@raising(exceptions=[])
def unsafe_call():
    raiser()
