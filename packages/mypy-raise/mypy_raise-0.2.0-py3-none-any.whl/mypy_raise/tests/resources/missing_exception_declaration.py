from mypy_raise import raising


@raising(exceptions=[ValueError])  # ERROR: also raises TypeError but it's not declared
def process(x):
    if not isinstance(x, int):
        raise TypeError('Must be an integer')  # Not declared!
    if x < 0:
        raise ValueError('Must be non-negative')
    return x * 2
