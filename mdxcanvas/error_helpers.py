from pathlib import Path
from bs4 import Tag
from .processing_context import get_current_file


def get_tag_source_file(tag: Tag) -> Path | None:
    if tag and (source := tag.get('data-source')):
        return Path(source)

    for parent in tag.parents:
        if source := parent.get('data-source'):
            return Path(source)

    return None


def get_file_path(tag: Tag) -> Path:
    if source := get_tag_source_file(tag):
        return source

    if current := get_current_file():
        return current

    raise ValueError("No file context available")


def format_tag(tag: Tag, max_length: int = 80) -> str:
    if not tag:
        return "<unknown tag>"

    tag_name = tag.name
    attrs = tag.attrs or {}

    if not attrs:
        return f"<{tag_name}>"

    # Build attribute strings
    attr_strs = [f'{k}="{" ".join(str(v) for v in val) if isinstance(val, list) else val}"' for k, val in attrs.items()]
    attrs_formatted = ' '.join(attr_strs)
    has_children = bool(tag.contents)

    # Build full tag
    full_tag = f"<{tag_name} {attrs_formatted}>" if has_children else f"<{tag_name} {attrs_formatted} />"

    if len(full_tag) <= max_length:
        return full_tag

    # Truncate if too long (show first few attributes, then indicate more, thanks to Claude)
    shown_attrs = []
    for attr_str in attr_strs[:3]:
        shown_attrs.append(attr_str)
        if len(f"<{tag_name} {' '.join(shown_attrs)} ...>") > max_length - 15:
            shown_attrs.pop()
            break

    remaining = len(attr_strs) - len(shown_attrs)
    if shown_attrs:
        return f"<{tag_name} {' '.join(shown_attrs)} ... +{remaining} more>"
    return f"<{tag_name}> ({len(attr_strs)} attributes)"


def validate_required_attribute(tag: Tag, attr_name: str, tag_display_name: str | None = None) -> str:
    if not (value := tag.get(attr_name)):
        display_name = tag_display_name if tag_display_name else tag.name
        raise ValueError(f'Required field "{attr_name}" missing from {display_name} tag {format_tag(tag)}\n  in {get_file_path(tag)}')
    return value
