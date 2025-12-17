from mypy_raise import raising


class MyClass:
    @staticmethod
    @raising(exceptions=[TypeError])
    def risky_staticmethod(x: str) -> str:
        """Static method that may raise TypeError."""
        if not isinstance(x, str):
            raise TypeError('Must be string')
        return x.upper()

    @staticmethod
    @raising(exceptions=[])
    def safe_staticmethod(x: int) -> int:
        """Static method that raises no exceptions."""
        return x * 2


# Function calling static method that raises
@raising(exceptions=[])
def call_risky_staticmethod():
    """Should detect TypeError from static method."""
    return MyClass.risky_staticmethod('hello')
