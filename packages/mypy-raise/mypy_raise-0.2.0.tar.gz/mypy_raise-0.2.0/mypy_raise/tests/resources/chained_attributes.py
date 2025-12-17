import os.path

from mypy_raise import raising


# Test chained attribute resolution
@raising(exceptions=[])
def use_os_path():
    # os.path.join should be resolved correctly
    return os.path.join('a', 'b')
