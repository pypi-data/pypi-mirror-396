from mypy_raise import raising


@raising(exceptions=[Exception])
def raise_value_error() -> None:
    raise ValueError('Oops')


@raising(exceptions=[LookupError])
def raise_key_error() -> None:
    raise KeyError('Oops')


@raising(exceptions=[OSError])
def raise_file_not_found_error() -> None:
    raise FileNotFoundError('Oops')
