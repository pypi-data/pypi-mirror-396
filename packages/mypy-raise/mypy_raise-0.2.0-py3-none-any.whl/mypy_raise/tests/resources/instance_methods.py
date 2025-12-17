from mypy_raise import raising


class MyClass:
    def __init__(self):
        self._value = 0

    @raising(exceptions=[ValueError])
    def risky_method(self, x: int) -> int:
        """Instance method that may raise ValueError."""
        if x < 0:
            raise ValueError('Negative value')
        return x * 2

    @raising(exceptions=[])
    def safe_method(self, x: int) -> int:
        """Instance method that raises no exceptions."""
        return x * 2 if x >= 0 else -x * 2

    @raising(exceptions=[TypeError])
    def another_risky_method(self, data: str) -> str:
        """Instance method that may raise TypeError."""
        if not isinstance(data, str):
            raise TypeError('Must be string')
        return data.upper()


# Function calling instance method that raises
@raising(exceptions=[])
def call_risky_method():
    """Should detect ValueError from instance method."""
    obj = MyClass()
    return obj.risky_method(5)


# Function calling multiple instance methods
@raising(exceptions=[])
def call_multiple_methods():
    """Should detect both ValueError and TypeError."""
    obj = MyClass()
    obj.risky_method(10)
    obj.another_risky_method('hello')
