import base64
import mimetypes
import re
import shutil
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
from ..util import relative_to_abs

logger = get_logger()


def _copy_quarto_dependencies(quarto_root: Path, temp_quarto_root: Path) -> None:
    """Copy the Quarto project files needed to render a slide deck."""
    temp_quarto_root.mkdir(parents=True, exist_ok=True)

    for config_name in ("_quarto.yaml", "_quarto.yml"):
        config = quarto_root / config_name
        if config.exists():
            shutil.copy2(config, temp_quarto_root / config_name)

    extensions = quarto_root / "_extensions"
    if extensions.exists():
        shutil.copytree(
            extensions,
            temp_quarto_root / "_extensions",
            dirs_exist_ok=True,
        )


def _copy_slide_to_temp(slide_file: Path, quarto_root: Path, temp_quarto_root: Path) -> Path:
    """Copy the target slide source into the same relative location under temp."""
    relative_slide_file = slide_file.relative_to(quarto_root)
    temp_slide_file = temp_quarto_root / relative_slide_file
    temp_slide_file.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(slide_file, temp_slide_file)
    return temp_slide_file


def _run_quarto_render(data: QuartoSlidesData, tmpdir: Path, deploy_root: Path) -> Path:
    # Copy just the target slide and Quarto project dependencies into a temp
    # project, render there, bundle the rendered HTML in place, and return the
    # temp HTML path for deployment.
    slide_file = relative_to_abs(Path(data['path']), deploy_root)
    quarto_root = relative_to_abs(Path(data['root_path']), deploy_root)
    temp_quarto_root = tmpdir.absolute()

    _copy_quarto_dependencies(quarto_root, temp_quarto_root)
    temp_slide_file = _copy_slide_to_temp(slide_file, quarto_root, temp_quarto_root)

    output_name = str(data['slides_name'])
    temp_output_file = (temp_slide_file.parent / output_name).absolute()

    cmd = [
        'quarto', 'render', temp_slide_file.name,
        '--output', output_name,
        '--log-level', 'info',
        '--no-cache'
    ]
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,  # decode to str instead of bytes
        cwd=temp_slide_file.parent
    )
    log = logger.debug
    if result.returncode != 0 or not temp_output_file.exists():
        log = logger.warning
    log(' '.join(cmd))
    log(result.stdout)
    log(result.stderr)

    result.check_returncode()  # raises CalledProcessError if non-zero
    if not temp_output_file.exists():
        raise FileNotFoundError('Missing quarto render output file: ' + str(temp_output_file))

    html = temp_output_file.read_text()
    html = _bundle_js(html, temp_output_file.parent)
    html = _inline_css(html, temp_output_file.parent)
    html = _inline_assets(html, temp_output_file.parent)
    temp_output_file.write_text(html)

    return temp_output_file


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


def _build_slides(data: QuartoSlidesData, tmpdir: Path, deploy_root: Path) -> FileData:
    output_file = _run_quarto_render(data, tmpdir, deploy_root)

    return FileData(
        path=(p := str(output_file)),
        checksum_paths=[p],
        canvas_folder=data.get('canvas_folder'),
        lock_at=data.get('lock_at'),
        unlock_at=data.get('unlock_at')
    )


def deploy_quarto_slides(course: Course, data: QuartoSlidesData, deploy_root: Path) -> tuple[FileInfo, None]:
    with TemporaryDirectory() as tmpdir:
        filedata = _build_slides(data, Path(tmpdir), deploy_root)

        return deploy_file(course, filedata, deploy_root)
