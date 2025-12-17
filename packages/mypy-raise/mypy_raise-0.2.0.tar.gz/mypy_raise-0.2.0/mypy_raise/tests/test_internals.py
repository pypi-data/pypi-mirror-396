import unittest
from unittest.mock import patch

from mypy_raise.decorator import raising
from mypy_raise.raising.stdlib_exceptions import _resolve_exception, is_subtype


class TestInternals(unittest.TestCase):

    # helper for decorator.py
    def test_decorator_execution(self) -> None:
        """Test that the decorator actually returns the function at runtime."""

        @raising(exceptions=[ValueError])
        def func(x):
            return x + 1

        self.assertEqual(func(1), 2)

        @raising()
        def func2():
            pass

        self.assertIsNone(func2())

    # helper for stdlib_exceptions.py
    def test_resolve_exception_errors(self) -> None:
        # invalid module
        self.assertIsNone(_resolve_exception('nonexistentmodule.Error'))
        # valid module, invalid class
        self.assertIsNone(_resolve_exception('json.NonExistentError'))

    def test_is_subtype_errors(self) -> None:
        # Force an error during is_subtype resolution by mocking _resolve_exception
        # or passing something that breaks logic if possible.
        # However, checking the code, is_subtype handles exceptions generically.
        # Let's try to mock _resolve_exception to raise an error

        with patch('mypy_raise.raising.stdlib_exceptions._resolve_exception', side_effect=ValueError('Boom')):
            self.assertFalse(is_subtype('ValueError', 'Exception'))
