import logging
import os
import stat
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

from canvasapi.course import Course

from mdxcanvas.util import to_relative_posix

from .file import deploy_file
from ..our_logging import get_logger
from ..resources import ZipFileData, FileData, FileInfo

logger = get_logger()


def zip_folder(
        path_to_zip: str,
        priority_files: dict[str, str]
):
    """
    Zips a folder, excluding files that match the exclude pattern.
    Items from the standard folder are added to the zip if they are not in the priority folder.
    Items in the priority folder take precedence over items in the standard folder.
    """

    if logger.isEnabledFor(logging.DEBUG):
        file_str = ', '.join(priority_files.keys())
        logger.debug(f'Files for {path_to_zip}: {file_str}')

    write_files(priority_files, path_to_zip)


def write_files(files: dict[str, str], path_to_zip: str):
    """
    Write files to a zip archive in a deterministic manner.

    This function creates a zip file with the provided files, ensuring idempotent
    zip creation across platforms and runs. Files are sorted before being added to
    the zip archive to guarantee consistent output regardless of the input order.

    Note: Compression may cause slight variations in output zip files on different
    platforms with different zlib versions, even with identical input and compression
    levels. If consistency issues arise, consider using ZIP_STORED (uncompressed)
    instead of ZIP_DEFLATED.
    """
    with ZipFile(path_to_zip, "w", ZIP_DEFLATED, compresslevel=9) as zipf:
        for zip_name in sorted(files.keys()):
            file = files[zip_name]
            write_file(file, zip_name.lstrip('/'), zipf)


def make_zip_info(zip_name, file_path: str):
    """
    Ensures that the zip file stays consistent between runs and across platforms.
    Preserves original file permissions, detecting executability cross-platform.
    """
    zinfo = ZipInfo(
        zip_name,
        # For consistency, set the time to 1980
        date_time=(1980, 1, 1, 0, 0, 0)
    )
    # Set compression type explicitly
    zinfo.compress_type = ZIP_DEFLATED

    # Set file permissions in external_attr (Unix format in high 16 bits)
    file_stat = Path(file_path).stat()

    if os.name == 'nt':  # Windows
        # On Windows, st_mode doesn't contain Unix permission bits
        # Check if the file is executable and set appropriate Unix permissions
        is_executable = os.access(file_path, os.X_OK)
        if is_executable:
            # Executable file: rwxr-xr-x
            zinfo.external_attr = (stat.S_IFREG | 0o755) << 16
        else:
            # Regular file: rw-r--r--
            zinfo.external_attr = (stat.S_IFREG | 0o644) << 16
    else:  # Unix-like systems (Linux, macOS, etc.)
        # Preserve original file permissions
        zinfo.external_attr = file_stat.st_mode << 16

    return zinfo


def write_file(file: str, zip_name: str, zipf: ZipFile):
    zinfo = make_zip_info(zip_name, file)
    try:
        with open(file) as f:
            zipf.writestr(zinfo, f.read())
    except UnicodeDecodeError as _:
        logger.debug(f'File {file} encountered a decode error during zip {zipf.filename} creation.')
        with open(file, 'rb') as f:
            zipf.writestr(zinfo, f.read())


def deploy_zip(course: Course, zipdata: ZipFileData, deploy_root: Path) -> tuple[FileInfo, None]:
    with TemporaryDirectory() as tmpdir:
        path_to_zip = str(Path(tmpdir) / zipdata['zip_file_name']) # pyright: ignore[reportOperatorIssue]
        zip_folder(path_to_zip, zipdata['zip_contents'])

        file = FileData(
            path=to_relative_posix(Path(path_to_zip), deploy_root),
            checksum_paths=[],
            canvas_folder=zipdata['canvas_folder'],
            lock_at=None,  # TODO - wire this up
            unlock_at=None,
        )

        return deploy_file(course, file, deploy_root)
