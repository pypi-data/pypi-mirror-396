from mypy_raise import raising


class MyClass:
    @raising(exceptions=[ValueError])
    async def async_method(self, x: int):
        """Async method that raises ValueError."""
        if x < 0:
            raise ValueError('Negative value')
        return x * 2

    @raising(exceptions=[])
    async def safe_async_method(self, x: int):
        """Async method that raises no exceptions."""
        return x * 2


# Standalone async function
@raising(exceptions=[TypeError])
async def async_function(data: str):
    """Async function that raises TypeError."""
    if not isinstance(data, str):
        raise TypeError('Must be string')
    return data.upper()


# Async function calling another async that raises
@raising(exceptions=[])
async def calls_async_raiser():
    """Should detect ValueError from async_method."""
    obj = MyClass()
    return await obj.async_method(5)
