import sys
from io import StringIO
from pathlib import Path
from unittest import TestCase

from mypy.api import run as mypy_api_run


class TestMypyRaisePlugin(TestCase):
    def run_mypy(self, resource_file: str) -> str:
        """Run mypy on a resource file using default config and return stdout."""
        return self.run_mypy_with_config(resource_file, 'mypy.ini')

    def run_mypy_with_config(self, resource_file: str, config_file: str) -> str:
        """Run mypy on a resource file with a custom config file and return stdout."""
        resource_path = Path(__file__).resolve().parent / 'resources' / resource_file
        config_path = Path(__file__).resolve().parent / 'resources' / config_file

        capture = StringIO()
        old_stdout = sys.stdout
        sys.stdout = capture

        try:
            stdout, stderr, exit_status = mypy_api_run(
                [
                    '--config-file',
                    str(config_path),
                    '--no-error-summary',
                    '--hide-error-context',
                    '--no-incremental',
                    str(resource_path),
                ]
            )
            combined_stdout = stdout + capture.getvalue()
            return combined_stdout
        finally:
            sys.stdout = old_stdout

    def test_safe_function(self) -> None:
        output = self.run_mypy('safe_function.py')
        # mypy.api returns empty string when there are no issues
        self.assertEqual(output.strip(), '')

    def test_explicit_raise_in_safe_function(self) -> None:
        output = self.run_mypy('explicit_raise_in_safe_function.py')
        self.assertIn('may raise', output)
        self.assertIn('not declared', output)

    def test_call_unsafe_function(self) -> None:
        output = self.run_mypy('call_unsafe_function.py')
        # Since 'unknown' is not decorated, we can't track its exceptions
        # The current implementation doesn't report this as an error
        # because we only track decorated functions
        self.assertEqual(output.strip(), '')

    def test_call_safe_function(self) -> None:
        output = self.run_mypy('call_safe_function.py')
        self.assertEqual(output.strip(), '')

    def test_call_explicit_raiser(self) -> None:
        output = self.run_mypy('call_explicit_raiser.py')
        self.assertIn('may raise', output)
        self.assertIn('not declared', output)

    def test_no_raise_calls_raiser(self) -> None:
        """Test function with no exceptions calling a raiser."""
        output = self.run_mypy('no_raise_calls_raiser.py')
        self.assertIn('may raise', output)
        self.assertIn('not declared', output)

    def test_indirect_exception_propagation(self) -> None:
        """Test exception propagation through multiple call levels."""
        output = self.run_mypy('indirect_exception_propagation.py')
        self.assertIn('may raise', output)
        self.assertIn('not declared', output)

    def test_stdlib_exception(self) -> None:
        """Test calling stdlib function that raises exceptions."""
        output = self.run_mypy('stdlib_exception.py')
        # Should detect exceptions from open()
        self.assertIn('may raise', output)
        self.assertIn('not declared', output)

    def test_correct_exception_declaration(self) -> None:
        """Test function correctly declaring all exceptions."""
        output = self.run_mypy('correct_exception_declaration.py')
        self.assertEqual(output.strip(), '')

    def test_missing_exception_declaration(self) -> None:
        """Test function missing exception in declaration."""
        output = self.run_mypy('missing_exception_declaration.py')
        self.assertIn('may raise', output)
        self.assertIn('not declared', output)

    def test_bare_raise(self) -> None:
        """Test bare raise statement handling."""
        output = self.run_mypy('bare_raise.py')
        # Bare raise should be tracked as 'Unknown' exception
        self.assertIn('may raise', output)

    def test_chained_attributes(self) -> None:
        """Test chained attribute resolution (os.path.join)."""
        output = self.run_mypy('chained_attributes.py')
        # os.path.join doesn't raise exceptions
        self.assertEqual(output.strip(), '')

    def test_module_exception(self) -> None:
        """Test module.Exception format exception name."""
        output = self.run_mypy('module_exception.py')
        # Should correctly parse builtins.ValueError
        self.assertEqual(output.strip(), '')

    def test_none_tracking(self) -> None:
        """Test exceptions=None case (not tracked)."""
        output = self.run_mypy('none_tracking.py')
        # Functions with exceptions=None should not be tracked
        self.assertEqual(output.strip(), '')

    def test_async_functions(self) -> None:
        """Test @raising decorator on async functions."""
        output = self.run_mypy('async_functions.py')
        # Should detect ValueError from async_method call
        self.assertIn('may raise', output)
        self.assertIn('ValueError', output)

    def test_property_methods(self) -> None:
        """Test @raising decorator on property methods."""
        output = self.run_mypy('property_methods.py')
        # Should detect ValueError from property access
        self.assertIn('may raise', output)
        self.assertIn('ValueError', output)

    def test_classmethod_functions(self) -> None:
        """Test @raising decorator on class methods."""
        output = self.run_mypy('classmethod_functions.py')
        # Should detect ValueError from classmethod call
        self.assertIn('may raise', output)
        self.assertIn('ValueError', output)

    def test_staticmethod_functions(self) -> None:
        """Test @raising decorator on static methods."""
        output = self.run_mypy('staticmethod_functions.py')
        # Should detect TypeError from staticmethod call
        self.assertIn('may raise', output)
        self.assertIn('TypeError', output)

    def test_instance_methods(self) -> None:
        """Test @raising decorator on instance methods."""
        output = self.run_mypy('instance_methods.py')
        # Should detect ValueError and TypeError from instance method calls
        self.assertIn('may raise', output)
        self.assertIn('ValueError', output)

    def test_custom_config(self) -> None:
        """Test custom exception configuration via mypy.ini."""
        output = self.run_mypy_with_config('custom_config.py', 'test_mypy.ini')
        # Should detect CustomError and ValueError from third_party_function (configured in mypy.ini)
        self.assertIn('may raise', output)
        self.assertIn('CustomError', output)
        self.assertIn('ValueError', output)

    def test_exception_caught(self) -> None:
        """Test that exceptions caught in try-except don't propagate."""
        output = self.run_mypy('exception_caught.py')
        # Functions without @raising decorator are not tracked
        # So there should be no errors even though risky_function raises ValueError
        self.assertEqual(output.strip(), '')

    def test_try_except_handling(self) -> None:
        """Test handling of exceptions within try-except blocks."""
        output = self.run_mypy('try_except_handling.py')

        # Should detect TypeError not caught in multiple_exceptions_caught
        self.assertIn("Function 'multiple_exceptions_caught' may raise 'TypeError'", output)

        # Should detect incorrect exception caught in wrong_exception_caught
        self.assertIn("Function 'wrong_exception_caught' may raise 'ValueError'", output)

        # Should NOT report ValueError for handles_exception (it's caught)
        self.assertNotIn("Function 'handles_exception' may raise", output)

        # Should NOT report exceptions for tuple_exception_handler
        self.assertNotIn("Function 'tuple_exception_handler' may raise", output)

    def test_exception_hierarchy(self) -> None:
        """Test invalid exception hierarchy handling (current reproduction)."""
        output = self.run_mypy('exception_hierarchy.py')

        # These SHOULD PASS if hierarchy is working, but currently they FAIL
        # because we only check strict equality.

        # handles_value_error_with_base catches Exception, raises ValueError
        # Once fixed, this assertion should be assertNotIn
        self.assertNotIn("Function 'handles_value_error_with_base' may raise 'ValueError'", output)

        # handles_file_error_with_oserror catches OSError, raises FileNotFoundError
        self.assertNotIn("Function 'handles_file_error_with_oserror' may raise 'FileNotFoundError'", output)

        # handles_key_error_with_lookup catches LookupError, raises KeyError
        self.assertNotIn("Function 'handles_key_error_with_lookup' may raise 'KeyError'", output)

    def test_strict_mode(self) -> None:
        """Test strict mode requires @raising decorator."""
        output = self.run_mypy_with_config('strict_mode.py', 'strict_mypy.ini')
        self.assertIn("Function 'undecorated_function' missing @raising decorator", output)
        self.assertIn("Function 'another_undecorated' missing @raising decorator", output)

    def test_declaration_hierarchy(self) -> None:
        """Test declaration with base exception covers subclasses."""
        output = self.run_mypy('declaration_hierarchy.py')
        # Expectation: NO errors because catching Exception should cover ValueError
        # Currently fails (contains errors)
        self.assertNotIn('may raise', output)

    def test_multiline_config(self) -> None:
        """Test parsing of multiline known_exceptions config."""
        output = self.run_mypy_with_config('multiline_config.py', 'multiline_mypy.ini')
        # third_party_lib.process is configured to raise ValueError
        self.assertIn("Function 'use_multiline_config' may raise 'ValueError'", output)
        self.assertIn('Raised by:', output)
        self.assertIn("'third_party_lib.process' raises 'ValueError'", output)
