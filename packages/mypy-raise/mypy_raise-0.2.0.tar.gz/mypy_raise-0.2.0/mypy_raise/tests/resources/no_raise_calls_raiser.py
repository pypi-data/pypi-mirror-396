from mypy_raise import raising


@raising(exceptions=[])
def safe():
    pass


@raising(exceptions=[ValueError])
def raiser():
    raise ValueError('Error')


@raising(exceptions=[])  # ERROR: calls raiser which raises ValueError
def caller():
    raiser()
