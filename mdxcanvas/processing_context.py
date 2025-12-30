from pathlib import Path
from contextvars import ContextVar
from typing import Optional

# Create a context variable to store the file stack
# Each execution context gets its own isolated copy
_file_stack: ContextVar[list[Path] | None] = ContextVar('file_stack', default=None)


class FileContext:
    """Context manager for tracking file processing stack.

    Usage:
        with FileContext(Path("homework-1.canvas.md")):
            # Process the file
            # Any errors will show this file in the context
    """

    def __init__(self, file_path: Path):
        self.file_path = file_path.resolve()  # Store absolute path
        self.token = None  # Will store the reset token

    def __enter__(self):
        # Get the current stack (or create empty list if first time)
        current_stack = _file_stack.get(None)
        if current_stack is None:
            current_stack = []

        # Create a NEW list with the new file added
        new_stack = current_stack + [self.file_path]

        # Set the context variable and save the token for reset
        self.token = _file_stack.set(new_stack)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset to the previous value using the token
        # This happens even if an exception occurred
        _file_stack.reset(self.token)
        # Return None to propagate exceptions normally


def get_current_file() -> Optional[Path]:
    """Get the current file being processed (top of stack)."""
    stack = _file_stack.get(None)
    if stack and len(stack) > 0:
        return stack[-1]
    return None


def get_file_stack() -> list[Path]:
    """Get the full file processing stack."""
    stack = _file_stack.get(None)
    return stack if stack is not None else []


def get_file_context() -> str:
    """Get a formatted string of the file context for error messages.

    Returns:
        - Empty string if no file context
        - "in /path/to/file.md" if single file
        - "in /path/to/file.xml (included from b.md, included from a.md)" if multiple files
    """
    stack = get_file_stack()

    if not stack:
        return ""

    if len(stack) == 1:
        # Just the main file
        return f"in {stack[0]}"

    # Multiple files - show the chain
    current_file = stack[-1]
    include_chain = stack[:-1]

    # Build the "included from" chain (reversed to show outer → inner)
    chain_str = ", included from ".join(str(f) for f in reversed(include_chain))

    return f"in {current_file} (included from {chain_str})"
