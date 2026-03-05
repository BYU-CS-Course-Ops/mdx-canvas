import base64
import hashlib
import html
import io
import tempfile
import time
import os
from pathlib import Path

import requests
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from mdxcanvas.util import to_relative_posix

from ..our_logging import get_logger
from ..processing_context import get_current_file_str
from ..resources import ResourceManager, CanvasResource, FileData

logger = get_logger()

MERMAID_INK_URL = 'https://mermaid.ink/img/'


def _content_hash(source: str) -> str:
    """Generate a short hash of the mermaid source."""
    return hashlib.sha256(source.encode()).hexdigest()[:16]


def _trim_whitespace(image_path: Path, padding: int = 10) -> None:
    """
    Trim extraneous whitespace from a PNG image.

    Crops the image to its non-transparent bounding box,
    keeping a small padding around the content.
    """
    with Image.open(image_path) as img:
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # getbbox() returns the bounding box of non-zero (non-transparent) pixels
        bbox = img.getbbox()
        if bbox is None:
            return  # Image is completely transparent/blank

        left = max(0, bbox[0] - padding)
        top = max(0, bbox[1] - padding)
        right = min(img.width, bbox[2] + padding)
        bottom = min(img.height, bbox[3] + padding)

        cropped = img.crop((left, top, right, bottom))
        # Use explicit parameters for cross-platform deterministic output:
        # - compress_level=9: fixed compression level (default varies by platform)
        # - pnginfo with empty PngInfo: strips metadata (timestamps, software, etc.)
        cropped.save(image_path, compress_level=9, pnginfo=PngInfo())


def render_mermaid_to_png(source: str, output_dir: Path) -> Path:
    """
    Render mermaid source code to a trimmed, high-resolution PNG file.

    Uses the mermaid.ink web service to render the diagram, then trims
    extraneous whitespace from the resulting image.

    Results are cached by content hash so identical diagrams
    are only rendered once.

    :param source: The mermaid diagram source code
    :param output_dir: Directory to store rendered PNG files
    :returns: Path to the generated PNG file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    content_hash = _content_hash(source)
    output_path = output_dir / f'mermaid-{content_hash}.png'

    # Encode the mermaid source as URL-safe base64
    base64_string = base64.urlsafe_b64encode(source.encode('utf-8')).decode('ascii')

    # Fetch the rendered image from mermaid.ink at 3x scale for high DPI
    url = f'{MERMAID_INK_URL}{base64_string}?type=png&width=1920&scale=3'
    response = requests.get(url, timeout=60, headers={'User-Agent': f'mdxcanvas-mermaid-renderer/1.0'})

    if response.status_code != 200:
        raise RuntimeError(
            f'mermaid.ink returned status {response.status_code} '
            f'for diagram (hash {content_hash})'
        )

    # Load the image from the response bytes and save as PNG
    img = Image.open(io.BytesIO(response.content))
    img.save(output_path, compress_level=9, pnginfo=PngInfo())

    # Trim extraneous whitespace from the rendered image
    _trim_whitespace(output_path)
    # Reset file modification time to 1980-01-01 for deterministic output
    mtime = time.mktime((1980, 1, 1, 0, 0, 0, 0, 1, -1))
    os.utime(output_path, (mtime, mtime))

    logger.debug(f'Generated mermaid diagram: {output_path.name}')
    return output_path


def make_mermaid_fence_format(resources: ResourceManager):
    """
    Create a custom fence formatter for pymdownx.superfences.

    Renders mermaid code blocks as PNG images with whitespace trimmed.
    When a ResourceManager is provided, the image is registered as a
    Canvas file resource so it will be uploaded and referenced correctly.

    :param resources: ResourceManager to register the image for upload
    :returns: A fence formatter function for use with pymdownx.superfences
    """

    mermaid_dir = Path(tempfile.mkdtemp(prefix='mdxcanvas-mermaid-'))

    def mermaid_fence_format(source, language, css_class, options, md, **kwargs):
        # Unescape HTML entities that may have been introduced
        # by the markdown preprocessing step (e.g. < -> &lt;)
        clean_source = html.unescape(source)

        try:
            output_path = render_mermaid_to_png(clean_source, mermaid_dir)
        except Exception as e:
            logger.exception(f'Failed to render mermaid diagram: {e}')
            raise e

        # Build extra attributes from {: .class #id key="value" } syntax
        classes = kwargs.get('classes', [])
        id_value = kwargs.get('id_value', '')
        attrs = dict(kwargs.get('attrs', {}))

        if css_class and css_class not in classes:
            classes.insert(0, css_class)

        attr_parts = []
        if classes:
            attr_parts.append(f'class="{" ".join(classes)}"')
        if id_value:
            attr_parts.append(f'id="{id_value}"')
        if 'alt' not in attrs:
            attrs['alt'] = 'Mermaid Diagram'
        for key, value in attrs.items():
            attr_parts.append(f'{key}="{value}"')

        extra_attrs = (' ' + ' '.join(attr_parts)) if attr_parts else ''

        file = CanvasResource(
            type='file',
            id=output_path.name,
            data=FileData(
                path=str(output_path),
                checksum_paths=[],
                canvas_folder=attrs.get('canvas_folder'),
                lock_at=attrs.get('lock_at'),
                unlock_at=attrs.get('unlock_at'),
            ),
            content_path=get_current_file_str()
        )
        resource_key = resources.add_resource_get_field(file, 'uri')
        return f'<img src="{resource_key}/preview"{extra_attrs} />'

    return mermaid_fence_format
