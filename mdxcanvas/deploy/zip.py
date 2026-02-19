import logging
import os
import re
import stat
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED
from typing import Optional

from .file import deploy_file
from ..our_logging import get_logger
from ..resources import ZipFileData, FileData

logger = get_logger()


def zip_folder(
        folder_path: Path,
        path_to_zip: Path,
        additional_files: Optional[list[Path]],
        exclude: Optional[re.Pattern[str]] = None,
        priority_folder: Optional[Path] = None
):
    """
    Zips a folder, excluding files that match the exclude pattern.
    Items from the standard folder are added to the zip if they are not in the priority folder.
    Items in the priority folder take precedence over items in the standard folder.
    """
    exclude = re.compile(exclude) if exclude else None
    folder_path = folder_path.resolve().absolute()
    logger.debug(f'Zipping {folder_path} to {path_to_zip}')

    priority_files = get_files(priority_folder, exclude, '') if priority_folder else {}
    files = get_files(folder_path, exclude, '')
    if additional_files:
        files.update(get_additional_files(additional_files))

    for zip_name, file in files.items():
        if zip_name not in priority_files:
            priority_files[zip_name] = file
        else:
            logger.debug(f'Preferring {priority_files[zip_name]} over {file}')

    if logger.isEnabledFor(logging.DEBUG):
        file_str = ', '.join(priority_files.keys())
        logger.debug(f'Files for {path_to_zip}: {file_str}')

    write_files(priority_files, path_to_zip)


def get_files(folder_path: Path, exclude: Optional[re.Pattern], prefix) -> dict[str, Path]:
    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    files = {}
    # Sort files for consistent ordering across platforms
    for file in sorted(folder_path.glob('*'), key=lambda p: p.name):
        if exclude and exclude.search(file.name):
            logger.debug(f'Excluding {file} from zip')
            continue

        if file.is_dir():
            files.update(get_files(file, exclude, prefix + '/' + file.name))
        else:
            files[prefix + '/' + file.name] = file.absolute()

    return files


def get_additional_files(additional_files: list[Path]) -> dict[str, Path]:
    files = {}
    for file in additional_files:
        if file.is_dir():
            files.update(get_files(file, None, f'/{file.name}'))
        else:
            files[f'/{file.name}'] = file

    return files


def write_files(files: dict[str, Path], path_to_zip: Path):
    # Store only and sort to ensure idempotent zip creation across platforms and runs
    with ZipFile(path_to_zip, "w", ZIP_STORED) as zipf:
        # Sort files by name for consistent ordering across platforms
        for zip_name in sorted(files.keys()):
            file = files[zip_name]
            write_file(file, zip_name.lstrip('/'), zipf)


def make_zip_info(zip_name, file_path: Path):
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
    zinfo.compress_type = ZIP_STORED

    # Set file permissions in external_attr (Unix format in high 16 bits)
    file_stat = file_path.stat()

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


def write_file(file: Path, zip_name: str, zipf: ZipFile):
    zinfo = make_zip_info(zip_name, file)
    try:
        with open(file) as f:
            zipf.writestr(zinfo, f.read())
    except UnicodeDecodeError as _:
        logger.debug(f'File {file} encountered a decode error during zip {zipf.filename} creation.')
        with open(file, 'rb') as f:
            zipf.writestr(zinfo, f.read())


def predeploy_zip(zipdata: ZipFileData, tmpdir: Path) -> FileData:
    target_folder = Path(zipdata['content_folder'])

    additional_files = [Path(file) for file in zipdata.get('additional_files') or []]

    pf = zipdata['priority_folder']
    priority_folder = Path(pf) if pf is not None else None
    if priority_folder is not None and not priority_folder.exists():
        raise FileNotFoundError(priority_folder)

    exclude = re.compile(zipdata['exclude_pattern']) if zipdata['exclude_pattern'] is not None else None

    path_to_zip = tmpdir / zipdata['zip_file_name']
    zip_folder(target_folder, path_to_zip, additional_files, exclude, priority_folder)

    file = FileData(
        path=str(path_to_zip),
        canvas_folder=zipdata['canvas_folder'],
        lock_at=None,
        unlock_at=None
    )

    return file


deploy_zip = deploy_file
