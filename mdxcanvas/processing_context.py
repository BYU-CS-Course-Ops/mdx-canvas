from pathlib import Path
from contextvars import ContextVar

_file_stack: ContextVar[list[Path] | None] = ContextVar('file_stack', default=None)


class FileContext:
    """Tracks current file being processed for error reporting."""

    def __init__(self, file_path: Path):
        self.file_path = file_path.resolve()
        self.reset_token = None

    def __enter__(self):
        current = _file_stack.get(None) or []
        self.reset_token = _file_stack.set(current + [self.file_path])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _file_stack.reset(self.reset_token)


def get_current_file() -> Path | None:
    """Returns the file currently being processed."""
    files = _file_stack.get(None)
    return files[-1] if files else None


def get_file_stack() -> list[Path]:
    """Returns the complete file processing chain."""
    return _file_stack.get(None) or []
