from mypy_raise import raising


@raising(exceptions=[])  # ERROR: open() can raise FileNotFoundError, PermissionError, OSError, etc.
def read_file():
    with open('file.txt') as f:
        return f.read()
