import sys


class Colors:
    """ANSI color codes for terminal output."""

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

    @staticmethod
    def is_tty() -> bool:
        """Check if output is to a terminal."""
        return sys.stdout.isatty()

    @classmethod
    def error(cls, text: str) -> str:
        """Format error text in red."""
        if cls.is_tty():
            return f'{cls.RED}{text}{cls.RESET}'
        return text

    @classmethod
    def success(cls, text: str) -> str:
        """Format success text in green."""
        if cls.is_tty():
            return f'{cls.GREEN}{text}{cls.RESET}'
        return text

    @classmethod
    def hint(cls, text: str) -> str:
        """Format hint text in yellow."""
        if cls.is_tty():
            return f'{cls.YELLOW}{text}{cls.RESET}'
        return text
