import hashlib
from pathlib import Path

from bs4.element import Tag

from mdxcanvas.util import retrieve_contents

from ..error_helpers import format_tag, get_file_path
from ..processing_context import get_current_file_str
from ..resources import MermaidData, ResourceManager, CanvasResource


def _content_hash(source: str) -> str:
    """Generate a short hash of the mermaid source."""
    return hashlib.sha256(source.encode()).hexdigest()[:8]


def make_mermaid_preprocessor(parent: Path, resources: ResourceManager):
    def process_mermaid(tag: Tag):
        path_attr = tag.get('path')
        inline_source = retrieve_contents(tag)

        # Validation: must have either inline source OR path attribute (not both)
        if path_attr and inline_source:
            raise ValueError(
                f"Mermaid tag cannot have both 'path' attribute and inline content @"
                + f" {format_tag(tag)}\n  in {get_file_path(tag)}"
            )

        if not path_attr and not inline_source:
            raise ValueError(
                f"Mermaid tag must have either 'path' attribute or inline diagram source @"
                + f" {format_tag(tag)}\n  in {get_file_path(tag)}"
            )

        # Determine source
        source = ""

        if path_attr:
            # External file reference
            path_str = str(path_attr)
            mermaid_file = (parent / path_str).resolve().absolute()

            if not mermaid_file.exists():
                raise ValueError(
                    f"Mermaid file not found @ {format_tag(tag)}"
                    + f"\n  File path: {mermaid_file}\n  in {get_file_path(tag)}"
                )

            source = mermaid_file.read_text(encoding='utf-8')
        else:
            # Inline diagram source
            source = inline_source

        # Generate resource ID from content hash
        resource_id: str = tag.get('name', f"mermaid-{_content_hash(source)}")  # pyright: ignore[reportAssignmentType]

        # Create MermaidData
        data = MermaidData(
            id=resource_id,
            source=source,
            canvas_folder=tag.get('canvas_folder'),
            lock_at=tag.get('lock_at'),
            unlock_at=tag.get('unlock_at'),
            alt=tag.get('alt'),
            css_class=tag.get('class'),
        )

        # Register resource
        file = CanvasResource(
            type='mermaid',
            id=resource_id,
            data=data,
            content_path=get_current_file_str()
        )

        resource_key = resources.add_resource_get_field(file, 'uri')

        # Create new img tag to replace mermaid tag
        img_tag = Tag(name='img')
        img_tag['src'] = f"{resource_key}/preview"

        # Pass through img attributes
        if alt_value := data.get('alt'):
            img_tag['alt'] = alt_value
        if class_value := data.get('css_class'):
            img_tag['class'] = class_value
        if id_value := data.get('id'):
            img_tag['id'] = id_value

        tag.replace_with(img_tag)

    return process_mermaid
