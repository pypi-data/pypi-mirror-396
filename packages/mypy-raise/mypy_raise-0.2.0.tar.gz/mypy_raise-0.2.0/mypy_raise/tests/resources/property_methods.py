from mypy_raise import raising


class MyClass:
    def __init__(self):
        self._value = 0

    @property
    @raising(exceptions=[ValueError])
    def risky_property(self) -> int:
        """Property that may raise ValueError."""
        if self._value < 0:
            raise ValueError('Negative value')
        return self._value

    @property
    @raising(exceptions=[])
    def safe_property(self) -> int:
        """Property that raises no exceptions."""
        return abs(self._value)

    @risky_property.setter
    @raising(exceptions=[TypeError])
    def risky_property(self, value: int):
        """Property setter that may raise TypeError."""
        if not isinstance(value, int):
            raise TypeError('Must be int')
        self._value = value


# Function using property that raises
@raising(exceptions=[])
def use_risky_property():
    """Should detect ValueError from property access."""
    obj = MyClass()
    return obj.risky_property
