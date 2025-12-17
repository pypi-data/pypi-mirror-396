# mypy-raise

A mypy plugin that enforces exception declarations in function signatures, ensuring functions explicitly declare all exceptions they may raise.

![test](https://github.com/diegojromerolopez/mypy-raise/actions/workflows/test.yml/badge.svg)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/diegojromerolopez/mypy-raise/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/mypy-raise.svg)](https://pypi.python.org/pypi/mypy-raise/)
[![PyPI version mypy-raise](https://badge.fury.io/py/mypy-raise.svg)](https://pypi.python.org/pypi/mypy-raise/)
[![PyPI status](https://img.shields.io/pypi/status/mypy-raise.svg)](https://pypi.python.org/pypi/mypy-raise/)
[![PyPI download month](https://img.shields.io/pypi/dm/mypy-raise.svg)](https://pypi.python.org/pypi/mypy-raise/)

## Overview

`mypy-raise` helps you write more reliable Python code by tracking exception propagation through your codebase. Similar to how `mypy-pure` tracks function purity, `mypy-raise` ensures that functions declare all exceptions they might raise, including those from called functions and standard library operations.

## Features

- ✅ **Exception Propagation Analysis** - Tracks exceptions through function call chains
- ✅ **Standard Library Support** - Knows about 100+ stdlib functions and their exceptions
- ✅ **Try-Except Analysis** - Smartly handles caught exceptions
- ✅ **Rich Error Messages** - Hints, source locations, and colored output
- ✅ **Strict Mode** - Enforce exception declarations across the codebase
- ✅ **Statistics** - Summary of analysis results and compliance rate
- ✅ **Configurable** - Extend exception mappings and ignore patterns via `mypy.ini`
- ✅ **Zero Runtime Overhead** - Pure static analysis, no runtime cost
- ✅ **Comprehensive Coverage** - High test coverage with verified correctness

## Installation

```bash
pip install mypy-raise
```

## Quick Start

### 1. Add the plugin to your `mypy.ini` or `pyproject.toml`:

**mypy.ini:**
```ini
[mypy]
plugins = mypy_raise.plugin
```

**pyproject.toml:**
```toml
[tool.mypy]
plugins = ["mypy_raise.plugin"]
```

### 2. Decorate your functions with `@raising`:

```python
from mypy_raise import raising

@raising(exceptions=[])  # Declares this function raises no exceptions
def safe_calculation(x: int, y: int) -> int:
    return x + y

@raising(exceptions=[ValueError, TypeError])  # Declares possible exceptions
def risky_operation(x: str) -> int:
    if not x.isdigit():
        raise ValueError("Not a number")
    return int(x)
```

### 3. Run mypy:

```bash
mypy your_code.py
```

## Examples

### ✅ Correct Usage

```python
from mypy_raise import raising

@raising(exceptions=[])
def add(a: int, b: int) -> int:
    """Pure calculation - no exceptions."""
    return a + b

@raising(exceptions=[ValueError, TypeError])
def parse_number(s: str) -> int:
    """Correctly declares all exceptions."""
    if not isinstance(s, str):
        raise TypeError("Must be a string")
    if not s.isdigit():
        raise ValueError("Not a number")
    return int(s)

@raising(exceptions=[FileNotFoundError, PermissionError, OSError])
def read_config(filename: str) -> str:
    """Declares exceptions from stdlib function open()."""
    with open(filename) as f:
        return f.read()
```

### ❌ Detected Violations

```python
from mypy_raise import raising

@raising(exceptions=[])
def unsafe_read(filename: str) -> str:
    # Error: Function 'unsafe_read' may raise 'FileNotFoundError', 'PermissionError', 'OSError'
    # but these are not declared. Raised by: 'builtins.open' raises ...
    with open(filename) as f:
        return f.read()

@raising(exceptions=[ValueError])
def incomplete_declaration(x: str) -> int:
    # Error: Function 'incomplete_declaration' may raise 'TypeError'
    # but these are not declared.
    if not isinstance(x, str):
        raise TypeError("Must be a string")  # Not declared!
    return int(x)

@raising(exceptions=[])
def calls_unsafe(x: str) -> int:
    # Error: Function 'calls_unsafe' may raise 'ValueError', 'TypeError'
    # but these are not declared. Raised by: 'parse_number' raises ...
    return parse_number(x)
```

## Advanced Usage

### Configuration

#### Strict Mode

Enforce that ALL functions must have the `@raising` decorator. Useful for gradual adoption or ensuring complete coverage.

`mypy.ini`:
```ini
[mypy-raise]
strict = true
```

#### Ignore Patterns

Exclude specific files or functions from analysis.

`mypy.ini`:
```ini
[mypy-raise]
# Comma-separated glob patterns
ignore_functions = test_*, _private_*, *deprecated*
ignore_files = tests/*, *_test.py, legacy/*.py
```

#### Custom Exceptions

Add custom exception mappings in `mypy.ini`:

```ini
[mypy-raise]
exceptions_my_function = CustomError,AnotherError
exceptions_third_party_lib.function = SomeException
```

Alternatively, you can use the cleaner multiline syntax with `known_exceptions`:

```ini
[mypy-raise]
known_exceptions =
    my_function: CustomError, AnotherError
    third_party_lib.function: SomeException
    requests.get: requests.RequestException, ValueError
```

### Exception Hierarchy

`mypy-raise` understands exception inheritance for both `try-except` blocks and `@raising` declarations.

**Polymorphic Declarations:**
You can declare a base exception to cover any subclass raised by the function.

```python
@raising(exceptions=[Exception])  # Covers ValueError because it inherits from Exception
def generic_raiser():
    raise ValueError("Something went wrong")

@raising(exceptions=[OSError])    # Covers FileNotFoundError
def file_op():
    raise FileNotFoundError("File missing")
```

**Smart Catching:**
Catching a base exception correctly handles raised subclasses.

```python
@raising(exceptions=[])  # No exceptions raised out of this function
def safe_handler():
    try:
        raise ValueError("Oops")
    except Exception:     # Correctly identifies that ValueError is handled
        pass
```

### Exception Propagation

The plugin automatically tracks exception propagation through multiple call levels:

```python
@raising(exceptions=[ValueError])
def level3():
    raise ValueError("Error at level 3")

@raising(exceptions=[ValueError])
def level2():
    level3()  # Propagates ValueError

@raising(exceptions=[])
def level1():
    # Error: Indirectly raises ValueError through level2 -> level3
    level2()
```

### Standard Library Support

The plugin includes comprehensive exception mappings for 100+ standard library functions:

```python
@raising(exceptions=[FileNotFoundError, PermissionError, OSError])
def use_open(path: str):
    return open(path).read()

@raising(exceptions=[ValueError, TypeError])
def use_int(s: str):
    return int(s)

@raising(exceptions=[KeyError])
def use_dict_getitem(d: dict, key: str):
    return d[key]

@raising(exceptions=[])  # dict.get never raises
def use_dict_get(d: dict, key: str):
    return d.get(key)
```

## Supported Function Types

- ✅ Regular functions
- ✅ Methods
- ✅ Class methods (`@classmethod`)
- ✅ Static methods (`@staticmethod`)
- ✅ Async functions
- ✅ Nested functions

## Limitations

mypy-raise performs **static analysis** and has some limitations:

### What it CAN detect:
- ✅ Direct exception raises
- ✅ Exceptions from decorated functions
- ✅ Exceptions from standard library functions
- ✅ Indirect exception propagation through call chains

### What it CANNOT detect:
- ❌ Exceptions from undecorated functions
- ❌ Exceptions from third-party libraries (unless configured)
- ❌ Dynamic raises (e.g., `raise getattr(module, exc_name)`)
- ❌ Exceptions from `eval()`, `exec()`, etc.

**Recommendation**: Use mypy-raise as a helpful guard rail for critical code paths. Combine it with comprehensive testing.

## Development

```bash
# Clone the repository
git clone https://github.com/diegojromerolopez/mypy-raise.git
cd mypy-raise

# Install dependencies with uv
pip install uv
uv sync --all-groups

# Run tests
uv run python -m unittest discover -s tests

# Run mypy
uv run mypy mypy_raise/

# Check coverage
uv run coverage run --source=mypy_raise -m unittest discover -s tests
uv run coverage report
```

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This project was inspired by [mypy-pure](https://github.com/diegojromerolopez/mypy-pure) and created with the assistance of AI tools (Claude Sonnet 4.5 and Antigravity/Gemini 3 Pro).

## Related Projects

- [mypy](https://github.com/python/mypy) - Optional static typing for Python.
- [mypy-pure](https://github.com/diegojromerolopez/mypy-pure) - Enforce function purity.
- [mypy-plugins-examples](https://github.com/diegojromerolopez/mypy-plugins-examples) - A project that contains some examples for my mypy-pure and mypy-raise plugins.

---

**Made with ❤️ for the Python community**
