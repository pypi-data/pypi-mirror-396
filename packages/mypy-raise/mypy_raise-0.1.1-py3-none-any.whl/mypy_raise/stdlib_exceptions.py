import builtins
import importlib


def get_stdlib_exceptions() -> dict[str, set[str]]:
    """Return a dictionary of standard library functions that raise exceptions."""
    return {
        # Built-in functions
        'builtins.abs': set(),
        'builtins.all': set(),
        'builtins.any': set(),
        'builtins.ascii': set(),
        'builtins.bin': set(),
        'builtins.bool': set(),
        'builtins.bytearray': set(),
        'builtins.bytes': set(),
        'builtins.callable': set(),
        'builtins.chr': {'ValueError'},
        'builtins.classmethod': set(),
        'builtins.compile': {'SyntaxError', 'ValueError'},
        'builtins.complex': {'ValueError'},
        'builtins.delattr': {'AttributeError'},
        'builtins.dict': {'ValueError'},
        'builtins.divmod': {'ZeroDivisionError'},
        'builtins.enumerate': set(),
        'builtins.eval': {'SyntaxError', 'TypeError', 'ValueError'},  # Evaluates code
        'builtins.exec': {'SyntaxError', 'TypeError', 'ValueError'},  # Executes code
        'builtins.filter': set(),
        'builtins.float': {'ValueError'},
        'builtins.format': {'ValueError'},
        'builtins.frozenset': set(),
        'builtins.getattr': {'AttributeError'},
        'builtins.globals': set(),
        'builtins.hasattr': set(),
        'builtins.hash': set(),
        'builtins.help': set(),
        'builtins.hex': set(),
        'builtins.id': set(),
        'builtins.input': {'EOFError'},  # Can raise EOFError
        'builtins.int': {'ValueError', 'TypeError'},
        'builtins.isinstance': {'TypeError'},
        'builtins.issubclass': {'TypeError'},
        'builtins.iter': {'TypeError'},
        'builtins.len': {'TypeError'},
        'builtins.list': set(),
        'builtins.locals': set(),
        'builtins.map': set(),
        'builtins.max': {'ValueError'},
        'builtins.memoryview': {'TypeError'},
        'builtins.min': {'ValueError'},
        'builtins.next': {'StopIteration'},
        'builtins.object': set(),
        'builtins.oct': set(),
        'builtins.open': {
            'FileNotFoundError',
            'PermissionError',
            'IsADirectoryError',
            'OSError',
        },
        'builtins.ord': {'TypeError'},
        'builtins.pow': {'TypeError', 'ValueError'},
        'builtins.print': {'OSError'},  # Can fail on write
        'builtins.property': set(),
        'builtins.range': {'ValueError', 'TypeError'},
        'builtins.repr': set(),
        'builtins.reversed': {'TypeError'},
        'builtins.round': {'TypeError'},
        'builtins.set': set(),
        'builtins.setattr': {'AttributeError'},
        'builtins.slice': {'TypeError'},
        'builtins.sorted': {'TypeError'},
        'builtins.staticmethod': set(),
        'builtins.str': set(),
        'builtins.sum': {'TypeError'},
        'builtins.super': {'RuntimeError'},  # If used incorrectly
        'builtins.tuple': set(),
        'builtins.type': {'TypeError'},
        'builtins.vars': {'TypeError'},
        'builtins.zip': set(),
        'builtins.__import__': {'ImportError', 'ValueError'},
        # Dict methods
        'builtins.dict.clear': set(),
        'builtins.dict.copy': set(),
        'builtins.dict.fromkeys': set(),
        'builtins.dict.get': set(),
        'builtins.dict.items': set(),
        'builtins.dict.keys': set(),
        'builtins.dict.pop': {'KeyError'},
        'builtins.dict.popitem': {'KeyError'},
        'builtins.dict.setdefault': set(),
        'builtins.dict.update': {'TypeError'},
        'builtins.dict.values': set(),
        # List methods
        'builtins.list.append': set(),
        'builtins.list.clear': set(),
        'builtins.list.copy': set(),
        'builtins.list.count': set(),
        'builtins.list.extend': set(),
        'builtins.list.index': {'ValueError'},
        'builtins.list.insert': set(),
        'builtins.list.pop': {'IndexError'},
        'builtins.list.remove': {'ValueError'},
        'builtins.list.reverse': set(),
        'builtins.list.sort': {'TypeError'},
        # Set methods
        'builtins.set.add': set(),
        'builtins.set.clear': set(),
        'builtins.set.copy': set(),
        'builtins.set.difference': set(),
        'builtins.set.difference_update': set(),
        'builtins.set.discard': set(),
        'builtins.set.intersection': set(),
        'builtins.set.intersection_update': set(),
        'builtins.set.isdisjoint': set(),
        'builtins.set.issubset': set(),
        'builtins.set.issuperset': set(),
        'builtins.set.pop': {'KeyError'},
        'builtins.set.remove': {'KeyError'},
        'builtins.set.symmetric_difference': set(),
        'builtins.set.symmetric_difference_update': set(),
        'builtins.set.union': set(),
        'builtins.set.update': set(),
        # String methods
        'builtins.str.capitalize': set(),
        'builtins.str.casefold': set(),
        'builtins.str.center': set(),
        'builtins.str.count': set(),
        'builtins.str.encode': {'UnicodeEncodeError'},
        'builtins.str.endswith': set(),
        'builtins.str.expandtabs': set(),
        'builtins.str.find': set(),
        'builtins.str.format': {'ValueError'},
        'builtins.str.format_map': {'ValueError'},
        'builtins.str.index': {'ValueError'},
        'builtins.str.isalnum': set(),
        'builtins.str.isalpha': set(),
        'builtins.str.isascii': set(),
        'builtins.str.isdecimal': set(),
        'builtins.str.isdigit': set(),
        'builtins.str.isidentifier': set(),
        'builtins.str.islower': set(),
        'builtins.str.isnumeric': set(),
        'builtins.str.isprintable': set(),
        'builtins.str.isspace': set(),
        'builtins.str.istitle': set(),
        'builtins.str.isupper': set(),
        'builtins.str.join': {'TypeError'},
        'builtins.str.ljust': set(),
        'builtins.str.lower': set(),
        'builtins.str.lstrip': set(),
        'builtins.str.maketrans': {'ValueError'},
        'builtins.str.partition': set(),
        'builtins.str.replace': set(),
        'builtins.str.rfind': set(),
        'builtins.str.rindex': {'ValueError'},
        'builtins.str.rjust': set(),
        'builtins.str.rpartition': set(),
        'builtins.str.rsplit': set(),
        'builtins.str.rstrip': set(),
        'builtins.str.split': set(),
        'builtins.str.splitlines': set(),
        'builtins.str.startswith': set(),
        'builtins.str.strip': set(),
        'builtins.str.swapcase': set(),
        'builtins.str.title': set(),
        'builtins.str.translate': set(),
        'builtins.str.upper': set(),
        'builtins.str.zfill': set(),
        # os module (file operations)
        'os.getcwd': {'OSError'},
        'os.chdir': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.listdir': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.mkdir': {'FileExistsError', 'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.makedirs': {'FileExistsError', 'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.remove': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.rmdir': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.rename': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.replace': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.link': {'FileNotFoundError', 'PermissionError', 'OSError'},
        'os.chmod': {'FileNotFoundError", "PermissionError', 'OSError'},
        'os.read': {'OSError'},
        'os.write': {'OSError'},
        # json module
        'json.dumps': {'TypeError', 'ValueError'},
        'json.loads': {'json.JSONDecodeError', 'TypeError'},
        'json.dump': {'TypeError', 'ValueError', 'OSError'},
        'json.load': {'json.JSONDecodeError', 'TypeError', 'OSError'},
    }


def _resolve_exception(name: str) -> type | None:
    """Resolve an exception name to its class."""
    # Try builtins first
    if hasattr(builtins, name):
        return getattr(builtins, name)

    # Handle dotted names (e.g. module.Error)
    if '.' in name:
        try:
            module_name, cls_name = name.rsplit('.', 1)
            module = importlib.import_module(module_name)
            return getattr(module, cls_name)
        except (ImportError, AttributeError):
            pass

    return None


def is_subtype(exc_name: str, base_name: str) -> bool:
    """
    Check if exc_name is a subtype of base_name using dynamic reflection.

    Resolves exception names to classes and uses issubclass().
    Returns False if resolution fails.
    """
    if exc_name == base_name:
        return True

    try:
        exc_cls = _resolve_exception(exc_name)
        base_cls = _resolve_exception(base_name)

        if exc_cls and base_cls:
            # Check if they are actually classes before calling issubclass
            if isinstance(exc_cls, type) and isinstance(base_cls, type):
                return issubclass(exc_cls, base_cls)
    except Exception:
        # Fail safe on any reflection error
        pass

    return False
