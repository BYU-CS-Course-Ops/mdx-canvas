import hashlib
import html
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, cast

from PIL import Image

from ..our_logging import get_logger
from ..processing_context import get_current_file_str
from ..resources import ResourceManager, CanvasResource, FileData

logger = get_logger()

_MERMAID_OUTPUT_DIR = Path(tempfile.gettempdir()) / 'mdxcanvas-mermaid'


def _content_hash(source: str) -> str:
    """Generate a short hash of the mermaid source for caching."""
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
        cropped.save(image_path)


def _find_mmdc() -> str:
    """Find the mmdc executable."""
    if shutil.which('mmdc'):
        return 'mmdc'

    raise FileNotFoundError(
        'Mermaid CLI (mmdc) not found. Install it with:\n'
        '  npm install -g @mermaid-js/mermaid-cli'
    )


def render_mermaid_to_png(source: str) -> Path:
    """
    Render mermaid source code to a trimmed PNG file.

    Uses mmdc (mermaid CLI) to render the diagram, then trims
    extraneous whitespace from the resulting image.

    Results are cached by content hash so identical diagrams
    are only rendered once.

    :param source: The mermaid diagram source code
    :returns: Path to the generated PNG file
    """
    _MERMAID_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    content_hash = _content_hash(source)
    output_path = _MERMAID_OUTPUT_DIR / f'mermaid-{content_hash}.png'

    # # Return cached result if available
    # if output_path.exists():
    #     logger.debug(f'Using cached mermaid diagram: {output_path}')
    #     return output_path

    # Write mermaid source to a temp file
    _, temp_path = tempfile.mkstemp(suffix='.mmd')
    input_file = Path(temp_path)
    input_file.write_text(source)

    try:
        mmdc = _find_mmdc()

        result = subprocess.run(
            [
                mmdc,
                '-i', str(input_file),
                '-o', str(output_path),
                '-b', 'transparent',
                '-s', '4',  # 4x scale for high DPI
            ],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            raise RuntimeError(
                f'Mermaid CLI (mmdc) failed:\n{result.stderr.strip()}'
            )

        if not output_path.exists():
            raise RuntimeError(
                f'Mermaid CLI did not produce output file. '
                f'stderr: {result.stderr.strip()}'
            )

        # Trim extraneous whitespace from the rendered image
        _trim_whitespace(output_path)

        logger.debug(f'Generated mermaid diagram: {output_path.name}')
        return output_path

    except subprocess.TimeoutExpired:
        raise RuntimeError('Mermaid CLI (mmdc) timed out after 60 seconds')

    finally:
        input_file.unlink(missing_ok=True)


def make_mermaid_fence_format(resources: ResourceManager):
    """
    Create a custom fence formatter for pymdownx.superfences.

    Renders mermaid code blocks as PNG images with whitespace trimmed.
    When a ResourceManager is provided, the image is registered as a
    Canvas file resource so it will be uploaded and referenced correctly.

    :param resources: ResourceManager to register the image for upload
    :returns: A fence formatter function for use with pymdownx.superfences
    """
    def mermaid_fence_format(source, language, css_class, options, md, **kwargs):
        # Unescape HTML entities that may have been introduced
        # by the markdown preprocessing step (e.g. < -> &lt;)
        clean_source = html.unescape(source)

        output_path = render_mermaid_to_png(clean_source)

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

        if resources is not None:
            file = CanvasResource(
                type='file',
                id=output_path.name,
                data=cast(dict, FileData(
                    path=str(output_path),
                )),
                content_path=get_current_file_str()
            )
            resource_key = cast(str, resources.add_resource(file, 'uri'))
            return f'<img src="{resource_key}/preview"{extra_attrs} />'

        return f'<img src="{output_path}"{extra_attrs} />'

    return mermaid_fence_format
