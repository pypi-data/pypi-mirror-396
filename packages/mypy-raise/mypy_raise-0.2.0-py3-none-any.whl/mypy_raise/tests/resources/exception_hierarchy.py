from mypy_raise import raising


# Helper functions raising specific exceptions
@raising(exceptions=[ValueError])
def raises_value_error() -> None:
    raise ValueError('Value error')


@raising(exceptions=[FileNotFoundError])
def raises_file_not_found() -> None:
    raise FileNotFoundError('File not found')


@raising(exceptions=[KeyError])
def raises_key_error() -> None:
    raise KeyError('Key error')


# Test 1: Catching Exception (base of ValueError) - Should pass
@raising(exceptions=[])
def handles_value_error_with_base() -> None:
    try:
        raises_value_error()
    except Exception:
        pass


# Test 2: Catching OSError (base of FileNotFoundError) - Should pass
@raising(exceptions=[])
def handles_file_error_with_oserror() -> None:
    try:
        raises_file_not_found()
    except OSError:
        pass


# Test 3: Catching LookupError (base of KeyError) - Should pass
@raising(exceptions=[])
def handles_key_error_with_lookup() -> None:
    try:
        raises_key_error()
    except LookupError:
        pass


# Test 4: Catching un-related exception - Should fail
@raising(exceptions=[])
def handles_wrong_exception() -> None:
    try:
        raises_value_error()
    except TypeError:
        pass
