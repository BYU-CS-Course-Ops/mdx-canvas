from pathlib import Path
from typing import Optional

from bs4 import Tag

from ..processing_context import get_file_context, get_current_file


def get_tag_source_file(tag: Tag) -> Optional[Path]:
    """
    Gets the source file for a tag by checking for data-source attribute.

    When files are included via <include> tags, the content gets wrapped in
    <div data-source="filename.md">. This function walks up the parent chain
    to find the actual source file.

    Args:
        tag: BeautifulSoup Tag object

    Returns:
        Path to the source file if found, otherwise None

    Example:
        # Tag is inside <div data-source="homework.md">
        source = get_tag_source_file(tag)  # Returns Path("homework.md")
    """
    # Check the tag itself
    if tag and hasattr(tag, 'get'):
        source = tag.get('data-source')
        if source:
            return Path(source)

    # Walk up parent chain looking for data-source
    if hasattr(tag, 'parents'):
        for parent in tag.parents:
            if hasattr(parent, 'get'):
                source = parent.get('data-source')
                if source:
                    return Path(source)

    return None


def get_file_location_for_error(tag: Tag) -> str:
    """
    Gets the best file location string for error messages.

    Prioritizes the tag's actual source file (from data-source attribute)
    over the current file context. Falls back to context if no source found.

    Args:
        tag: BeautifulSoup Tag object

    Returns:
        Formatted file location string like "in /path/to/file.md"
    """
    # First try to get the actual source file from the tag
    source_file = get_tag_source_file(tag)
    if source_file:
        return f"in {source_file}"

    # Fall back to current file context
    file_context = get_file_context()
    if file_context:
        return file_context

    # Last resort: try to get current file being processed
    current_file = get_current_file()
    if current_file:
        return f"in {current_file}"

    return ""


def format_tag_for_error(tag: Tag, max_length: int = 80) -> str:
    """
    Formats a BeautifulSoup tag for error messages with smart truncation.

    Args:
        tag: BeautifulSoup Tag object
        max_length: Maximum length before truncating (default: 80)

    Returns:
        Formatted tag string, truncated if too long

    Examples:
        <img src="image.png" />
        <file path="doc.pdf" canvas_folder="resources" unlock_at="2024-01-15" />
        <page title="Introduction" published="true">
        <assignment assignment_group="Final" ... +5 more>
    """
    if not tag or not hasattr(tag, 'name'):
        return "<unknown tag>"

    tag_name = tag.name
    attrs = tag.attrs if hasattr(tag, 'attrs') else {}

    if not attrs:
        return f"<{tag_name}>"

    # Format attributes as key="value" pairs
    attr_strs = []
    for key, value in attrs.items():
        # Handle different value types
        if isinstance(value, list):
            value_str = ' '.join(str(v) for v in value)
        else:
            value_str = str(value)
        attr_strs.append(f'{key}="{value_str}"')

    attrs_formatted = ' '.join(attr_strs)

    # Check if tag has children (not self-closing)
    has_children = tag.contents if hasattr(tag, 'contents') else []

    # Build full tag
    if has_children:
        full_tag = f"<{tag_name} {attrs_formatted}>"
    else:
        full_tag = f"<{tag_name} {attrs_formatted} />"

    # Return as-is if short enough
    if len(full_tag) <= max_length:
        return full_tag

    # Truncate: show tag name + first 2-3 attributes + count
    shown_attrs = []
    for attr_str in attr_strs[:3]:  # Max 3 attributes shown
        shown_attrs.append(attr_str)
        test_str = f"<{tag_name} {' '.join(shown_attrs)} ...>"
        if len(test_str) > max_length - 15:  # Reserve space for count
            shown_attrs.pop()
            break

    remaining = len(attr_strs) - len(shown_attrs)
    if shown_attrs:
        shown = ' '.join(shown_attrs)
        return f"<{tag_name} {shown} ... +{remaining} more>"
    else:
        return f"<{tag_name}> ({len(attr_strs)} attributes)"


def format_required_field_error(
    tag: Tag,
    field_name: str,
    tag_display_name: Optional[str] = None
) -> str:
    """
    Creates a standardized error message for missing required fields.

    Args:
        tag: BeautifulSoup Tag object
        field_name: Name of the required field that's missing
        tag_display_name: Optional name to use instead of tag.name

    Returns:
        Formatted error message with tag details, tag path, and file context

    Example:
        Required field "path" missing from tag <file canvas_folder="resources" />
        @ module(Week1).page(Syllabus) in /path/to/file.md
    """
    formatted_tag = format_tag_for_error(tag)
    file_location = get_file_location_for_error(tag)

    display_name = tag_display_name or tag.name if tag else "tag"

    error_msg = f'Required field "{field_name}" missing from {display_name} tag {formatted_tag}'

    if file_location:
        error_msg += f'\n  {file_location}'


    return error_msg


def format_validation_error(tag: Tag, message: str) -> str:
    """
    Generic validation error formatter that includes tag details and file context.

    Args:
        tag: BeautifulSoup Tag object
        message: Custom error message describing what went wrong

    Returns:
        Formatted error message with custom message, formatted tag, and file context

    Example:
        Image file not found @ <img src="missing.png" /> in /path/to/file.md
    """
    formatted_tag = format_tag_for_error(tag)
    file_location = get_file_location_for_error(tag)

    error_msg = f'{message} @ {formatted_tag}'

    if file_location:
        error_msg += f' {file_location}'

    return error_msg


def validate_required_attribute(
    tag: Tag,
    attr_name: str,
    tag_display_name: Optional[str] = None
) -> str:
    """
    Validates that an attribute exists on a tag and returns its value.
    Raises a formatted error if the attribute is missing.

    Args:
        tag: BeautifulSoup Tag object
        attr_name: Name of the required attribute
        tag_display_name: Optional name to use instead of tag.name in error

    Returns:
        The attribute value if present

    Raises:
        ValueError: If the attribute is missing or empty

    Example:
        path = validate_required_attribute(tag, 'path', 'file')
    """
    value = tag.get(attr_name)

    if not value:
        raise ValueError(format_required_field_error(tag, attr_name, tag_display_name))

    return value


def validate_file_exists(tag: Tag, file_path: Path, attr_name: str) -> None:
    """
    Validates that a file path exists.
    Raises a formatted error with file path and tag details if not found.

    Args:
        tag: BeautifulSoup Tag object
        file_path: Path object to check
        attr_name: Name of the attribute that contained the path

    Raises:
        ValueError: If the file doesn't exist

    Example:
        validate_file_exists(tag, resolved_path, 'src')
    """
    if not file_path.exists():
        formatted_tag = format_tag_for_error(tag)
        file_location = get_file_location_for_error(tag)

        error_msg = f'File not found @ {formatted_tag}\n  File path: {file_path}'

        if file_location:
            error_msg += f'\n  {file_location}'

        raise ValueError(error_msg)
