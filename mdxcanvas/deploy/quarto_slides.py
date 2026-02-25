import base64
import mimetypes
import re
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.parse import urlparse

from canvasapi.course import Course

from .file import deploy_file
from ..our_logging import get_logger
from ..resources import FileData
from ..resources import FileInfo
from ..resources import QuartoSlidesData

logger = get_logger()


def _run_quarto_render(data: QuartoSlidesData, tmpdir: Path) -> Path:
    path_parent_name = Path(data['path']).parent.name

    output_file = (tmpdir / path_parent_name / data['slides_name']).absolute()
    logger.warning(str(tmpdir))
    cmd = [
        'quarto', 'render', data['path'],
        '--output-dir', str(tmpdir),
        '--output', str(output_file.name),
        '--log-level', 'info'
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # decode to str instead of bytes
        cwd=Path(data['path']).parent
    )
    log = logger.debug
    if result.returncode != 0 or not output_file.exists():
        log = logger.warning
    log(' '.join(cmd))
    log(result.stdout)
    log(result.stderr)

    result.check_returncode()  # raises CalledProcessError if non-zero
    if not output_file.exists():
        raise FileNotFoundError('Missing quarto render output file: ' + str(output_file))

    return output_file


def _is_external(url: str) -> bool:
    if url.startswith("data:"):
        return True
    parsed = urlparse(url)
    return bool(parsed.scheme) and parsed.scheme not in ("", "file")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _bundle_js(html: str, base_dir: Path) -> str:
    """Bundle RevealJS dependencies into the HTML so it functions as a standalone file"""
    src_attr_pattern = re.compile(
        r"""\bsrc\s*=\s*(?:"([^"]+)"|'([^']+)'|([^\s"'=<>`]+))""",
        re.IGNORECASE,
    )

    def repl(match: re.Match[str]) -> str:
        attrs = match.group(1)
        src_match = src_attr_pattern.search(attrs)
        if not src_match:
            return match.group(0)
        src = next(group for group in src_match.groups() if group is not None)
        if _is_external(src):
            return match.group(0)
        asset = (base_dir / src).resolve()
        if not asset.exists():
            return match.group(0)
        js = _read_text(asset)
        return f"<script>\n{js}\n</script>"

    pattern = re.compile(r"<script\b([^>]*)>\s*</script>", flags=re.IGNORECASE)
    return pattern.sub(repl, html)


def _inline_css(html: str, base_dir: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        href = match.group(1)
        if _is_external(href):
            return match.group(0)
        asset = (base_dir / href).resolve()
        if not asset.exists():
            return match.group(0)
        css = _read_text(asset)
        return f"<style>\n{css}\n</style>"

    pattern = re.compile(r"<link\s+[^>]*rel=\"stylesheet\"[^>]*href=\"([^\"]+)\"[^>]*>")
    return pattern.sub(repl, html)


def _inline_assets(html: str, base_dir: Path) -> str:
    def repl(match: re.Match[str]) -> str:
        attr = match.group(1)
        url = match.group(2)
        if _is_external(url):
            return match.group(0)
        asset = (base_dir / url).resolve()
        if not asset.exists():
            return match.group(0)
        mime, _ = mimetypes.guess_type(asset.name)
        mime = mime or "application/octet-stream"
        data = base64.b64encode(asset.read_bytes()).decode("ascii")
        return f"{attr}=\"data:{mime};base64,{data}\""

    pattern = re.compile(r"\b(src|href)=\"([^\"]+)\"")
    return pattern.sub(repl, html)


def _build_slides(data: QuartoSlidesData, tmpdir: Path) -> FileData:
    output_file = _run_quarto_render(data, tmpdir)
    html = output_file.read_text()
    html = _bundle_js(html, output_file.parent)
    html = _inline_css(html, output_file.parent)
    html = _inline_assets(html, output_file.parent)
    output_file.write_text(html)

    return FileData(
        path=(p := str(output_file)),
        checksum_paths=[p],
        canvas_folder=data.get('canvas_folder'),
        lock_at=data.get('lock_at'),
        unlock_at=data.get('unlock_at')
    )


def deploy_quarto_slides(course: Course, data: QuartoSlidesData) -> tuple[FileInfo, None]:
    with TemporaryDirectory() as tmpdir:
        filedata = _build_slides(data, Path(tmpdir))

        return deploy_file(course, filedata)
