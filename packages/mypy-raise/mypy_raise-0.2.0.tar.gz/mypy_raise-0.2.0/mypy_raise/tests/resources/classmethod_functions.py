from mypy_raise import raising


class MyClass:
    @classmethod
    @raising(exceptions=[ValueError])
    def risky_classmethod(cls, x: int) -> int:
        """Class method that may raise ValueError."""
        if x < 0:
            raise ValueError('Negative value')
        return x * 2

    @classmethod
    @raising(exceptions=[])
    def safe_classmethod(cls, x: int) -> int:
        """Class method that raises no exceptions."""
        return x * 2 if x >= 0 else -x * 2


# Function calling class method that raises
@raising(exceptions=[])
def call_risky_classmethod():
    """Should detect ValueError from class method."""
    return MyClass.risky_classmethod(5)
