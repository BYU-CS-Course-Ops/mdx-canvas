import logging
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo

from canvasapi.course import Course

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
    with ZipFile(path_to_zip, "w") as zipf:
        for zip_name, file in files.items():
            write_file(file, zip_name.lstrip('/'), zipf)


def make_zip_info(zip_name):
    """
    Ensures that the zip file stays consistent between runs.
    """
    zinfo = ZipInfo(
        zip_name,
        # For consistency, set the time to 1980
        date_time=(1980, 1, 1, 0, 0, 0)
    )
    return zinfo


def write_file(file: str, zip_name: str, zipf: ZipFile):
    zinfo = make_zip_info(zip_name)
    try:
        with open(file) as f:
            zipf.writestr(zinfo, f.read())
    except UnicodeDecodeError as _:
        logger.debug(f'File {file} encountered a decode error during zip {zipf.filename} creation.')
        with open(file, 'rb') as f:
            zipf.writestr(zinfo, f.read())


def deploy_zip(course: Course, zipdata: ZipFileData) -> tuple[FileInfo, None]:
    with TemporaryDirectory() as tmpdir:
        path_to_zip = str(Path(tmpdir) / zipdata['zip_file_name'])
        zip_folder(path_to_zip, zipdata['zip_contents'])

        file = FileData(
            path=str(path_to_zip),
            checksum_paths=[],
            canvas_folder=zipdata['canvas_folder'],
            lock_at=None,  # TODO - wire this up
            unlock_at=None,
        )

        return deploy_file(course, file)

