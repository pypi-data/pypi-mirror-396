from mypy_raise import raising


@raising(exceptions=[ValueError, TypeError])
def process(x):
    if not isinstance(x, int):
        raise TypeError('Must be an integer')
    if x < 0:
        raise ValueError('Must be non-negative')
    return x * 2
