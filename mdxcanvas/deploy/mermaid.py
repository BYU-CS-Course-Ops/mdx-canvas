import os
import subprocess
import sys
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import quote

from canvasapi.course import Course
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from playwright.sync_api import Error as PWError
from playwright.sync_api import sync_playwright

from .file import deploy_file
from ..our_logging import get_logger
from ..resources import FileData, FileInfo, MermaidData, StrLike
from ..util import relative_to_abs, to_relative_posix

logger = get_logger()


def _build_template(background: str = "transparent", theme: str = "default", svg_padding: int = 10) -> str:
    return f"""
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
        html, body {{
            margin: 0; padding: 0; background: {background};
        }}
        #container {{
            display: inline-block;
            margin: {svg_padding}px;
        }}
        /* Ensure the SVG isn't clipped by layout */
        svg {{ display: block; }}
        </style>
        <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
        // Initialize Mermaid but DON'T autostart on <pre> blocks; we'll call render() manually.
        mermaid.initialize({{
            startOnLoad: false,
            theme: "{theme}"
        }});
        window.renderMermaid = async (code) => {{
            // Unique id for this render
            const id = "m" + Math.random().toString(36).slice(2);
            const container = document.querySelector('#container');
            // Render returns {{ svg, bindFunctions }}
            const res = await mermaid.render(id, code);
            container.innerHTML = res.svg;
            // Some diagrams bind interactivity; keep it safe for static export
            if (res.bindFunctions) res.bindFunctions(container);
            return id;
        }};
        </script>
    </head>
    <body>
        <div id="container"></div>
    </body>
    </html>
    """


def _trim_whitespace(output_path: Path, padding: int = 10) -> None:
    """
    Trim extraneous whitespace from a PNG image.

    Crops the image to its non-transparent bounding box,
    keeping a small padding around the content.
    """
    with Image.open(output_path) as img:
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
        cropped.save(output_path, compress_level=9, pnginfo=PngInfo())


def _ensure_pw_chromium():
    """Ensure that Playwright Chromium is installed."""
    try:
        with sync_playwright() as p:
            # Try launching to verify presence
            browser = p.chromium.launch()  # will fail if not installed
            browser.close()
    except PWError:
        # Use hermetic install under site-packages
        os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "0")
        logger.info("Installing Playwright Chromium (one time)...")
        # Run the official installer
        cmd = [sys.executable, "-m", "playwright", "install", "chromium", "--with-deps"]
        subprocess.check_call(cmd)


def render_mermaid_to_png(id: StrLike, source: str, output_dir: Path) -> Path:
    """
    Render mermaid source code to a trimmed, high-resolution PNG file.

    Uses mermaid-cli (mmdc) to render the diagram locally, then trims
    extraneous whitespace from the resulting image.

    :param id: Resource identifier for the diagram
    :param source: The mermaid diagram source code
    :param output_dir: Directory to store rendered PNG files
    :returns: Path to the generated PNG file
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    _ensure_pw_chromium()

    output_path = output_dir / f'{id}.png'

    # Render mermaid diagram to PNG using local mermaid-cli
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            device_scale_factor=6,  # High-resolution rendering for Retina displays
        )
        page = context.new_page()

        template = _build_template()

        # Load our HTML shell from a data URL
        page.goto("data:text/html;charset=utf-8," + quote(template, safe=''))

        # Render the Mermaid code into #container, wait for SVG to appear
        page.evaluate("code => window.renderMermaid(code)", source)
        svg_locator = page.locator("#container svg")
        svg_locator.wait_for(state="visible")

        svg_locator.screenshot(
            path=str(output_path),
            scale='device',
            omit_background=True
        )

        browser.close()

    # Trim extraneous whitespace from the rendered image
    _trim_whitespace(output_path)

    # Reset file modification time to 1980-01-01 for deterministic output
    mtime = time.mktime((1980, 1, 1, 0, 0, 0, 0, 1, -1))
    os.utime(output_path, (mtime, mtime))

    logger.debug(f'Generated mermaid diagram: {output_path.name}')
    return output_path


def deploy_mermaid(
    course: Course, data: MermaidData, deploy_root: Path
) -> tuple[FileInfo, None]:
    """
    Deploy a mermaid diagram as a PNG image file to Canvas.

    If data contains a 'path', the mermaid source is read from that file.
    Otherwise, the 'source' field is used directly.

    The diagram is rendered to PNG using mermaid-cli (mmdc), then uploaded
    to Canvas as a file resource.

    :param course: Canvas course object
    :param data: MermaidData containing diagram source and metadata
    :param deploy_root: Root directory for resolving relative paths
    :returns: Tuple of (FileInfo, None)
    """
    # Determine source
    path = data.get('path')
    if path:
        mermaid_file = relative_to_abs(Path(path), deploy_root)
        source = mermaid_file.read_text(encoding='utf-8')
    else:
        source = data['source']

    # Render mermaid to PNG in temporary directory
    with TemporaryDirectory() as tmpdir:
        output_path = render_mermaid_to_png(data['id'], source, Path(tmpdir))

        # Create FileData for the rendered PNG
        file_data = FileData(
            path=(p := to_relative_posix(output_path, deploy_root)),
            checksum_paths=[p],
            canvas_folder=data.get('canvas_folder'),
            lock_at=data.get('lock_at'),
            unlock_at=data.get('unlock_at')
        )

        # Upload the file to Canvas
        file_info, _ = deploy_file(course, file_data, deploy_root)

    logger.debug(f"Deployed mermaid diagram: {file_info['title']}")
    return file_info, None
