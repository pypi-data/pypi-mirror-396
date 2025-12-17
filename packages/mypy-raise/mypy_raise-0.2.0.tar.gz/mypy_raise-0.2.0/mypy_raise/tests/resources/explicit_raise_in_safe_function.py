from mypy_raise import raising


@raising(exceptions=[])
def unsafe():
    raise ValueError('Oops')
