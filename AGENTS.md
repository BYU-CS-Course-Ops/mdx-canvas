# MDXCanvas Agent Guidelines

## Build and Test Commands
- Installation: `poetry install`

## Code Style Guidelines

### Language and Framework
- Python 3.10+, uses Jinja2, CanvasAPI, BeautifulSoup4, Markdown library

### Imports
- Standard library first, then third-party, then local modules
- Use explicit imports (no `from module import *`)
- Order: `import os`, `from pathlib import Path`, then `from canvasapi import Canvas`, then `from .our_logging import get_logger`

### Formatting and Naming
- Max line length 88 characters
- Functions/variables: `snake_case`, Classes: `PascalCase`, Constants: `UPPER_CASE`
- Private methods: `_underscore_prefix`
- TypedDict classes: `PascalCase` with "Info" or "Dict" suffix
- Use type hints for all function signatures: `def func(arg: str) -> bool:`

### Error Handling
- Use specific exception types (ValueError, FileNotFoundError, TypeError)
- Log with `get_logger()` from `mdxcanvas.our_logging`
- Include context: `raise ValueError(f"Expected X, got {value}")`

## Project Structure
- `mdxcanvas/` - Main code (49 files): deploy, text_processing, xml_processing, erasecanvas
- `tests/` - pytest files: test_jinja_template.py, test_post_processing.py, resource-id-tests/
- `documents/`, `demo-course/` - Documentation and examples

## Development Workflow
- Fresh demo-course deploy and backward compatibility required
- Ensure type safety before committing
- No linters configured; maintain clean code manually

## Configuration
- No .cursorrules or .github/copilot-instructions.md files
