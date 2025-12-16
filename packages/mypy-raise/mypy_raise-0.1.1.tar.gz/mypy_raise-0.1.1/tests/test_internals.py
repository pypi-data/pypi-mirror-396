
import unittest
from unittest.mock import patch, MagicMock
from mypy_raise.decorator import raising
from mypy_raise.stats import AnalysisStats
from mypy_raise.colors import Colors
from mypy_raise.stdlib_exceptions import _resolve_exception, is_subtype

class TestInternals(unittest.TestCase):
    
    # helper for decorator.py
    def test_decorator_execution(self):
        """Test that the decorator actually returns the function at runtime."""
        @raising(exceptions=[ValueError])
        def func(x):
            return x + 1
        
        self.assertEqual(func(1), 2)
        
        @raising()
        def func2():
            pass
        self.assertIsNone(func2())

    # helper for stats.py
    def test_stats(self):
        stats = AnalysisStats()
        
        # Test default/empty
        self.assertEqual(stats.compliance_rate(), 100.0)
        
        # Test summary format
        summary = stats.format_summary()
        self.assertIn("Compliance rate: 100.0%", summary)
        
        # Test with data
        stats.functions_checked = 10
        stats.violations_found = 2
        self.assertEqual(stats.compliance_rate(), 80.0)
        summary = stats.format_summary()
        self.assertIn("Compliance rate: 80.0%", summary)

    # helper for stdlib_exceptions.py
    def test_resolve_exception_errors(self):
        # invalid module
        self.assertIsNone(_resolve_exception("nonexistentmodule.Error"))
        # valid module, invalid class
        self.assertIsNone(_resolve_exception("json.NonExistentError"))
    
    def test_is_subtype_errors(self):
        # Force an error during is_subtype resolution by mocking _resolve_exception
        # or passing something that breaks logic if possible.
        # However, checking the code, is_subtype handles exceptions generically.
        # Let's try to mock _resolve_exception to raise an error
        
        with patch('mypy_raise.stdlib_exceptions._resolve_exception', side_effect=ValueError("Boom")):
            self.assertFalse(is_subtype("ValueError", "Exception"))

    # helper for colors.py
    @patch('sys.stdout')
    def test_colors_tty(self, mock_stdout):
        # FORCE TTY
        mock_stdout.isatty.return_value = True
        
        self.assertIn('\033[91m', Colors.error("text"))
        self.assertIn('\033[92m', Colors.success("text"))
        self.assertIn('\033[93m', Colors.hint("text"))
        
        # FORCE NO TTY
        mock_stdout.isatty.return_value = False
        self.assertEqual(Colors.error("text"), "text")
        self.assertEqual(Colors.success("text"), "text")
        self.assertEqual(Colors.hint("text"), "text")

    # helper for visitor.py
    def test_visitor_extract_exception_name(self):
        import ast
        from mypy_raise.visitor import RaisingVisitor
        
        visitor = RaisingVisitor()
        
        # Test Name
        node = ast.Name(id='ValueError', ctx=ast.Load())
        # Access private method using name mangling
        self.assertEqual(visitor._RaisingVisitor__extract_exception_name(node), 'ValueError')
        
        # Test Attribute (e.g. os.error)
        node = ast.Attribute(
            value=ast.Name(id='os', ctx=ast.Load()),
            attr='error',
            ctx=ast.Load()
        )
        self.assertEqual(visitor._RaisingVisitor__extract_exception_name(node), 'os.error')
        
        # Test deep Attribute (e.g. a.b.c)
        node = ast.Attribute(
            value=ast.Attribute(
                value=ast.Name(id='a', ctx=ast.Load()),
                attr='b',
                ctx=ast.Load()
            ),
            attr='c',
            ctx=ast.Load()
        )
        self.assertEqual(visitor._RaisingVisitor__extract_exception_name(node), 'a.b.c')
