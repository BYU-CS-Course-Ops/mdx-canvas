import logging
import re
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile, ZipInfo

from canvasapi.course import Course

from ..resources import ZipFileData, FileData
from .file import deploy_file, lookup_file


def zip_folder(
        folder_path: Path,
        path_to_zip: Path,
        exclude: re.Pattern = None,
        priority_fld: Path = None
):
    """
    Zips a folder, excluding files that match the exclude pattern.
    Items from the priority folder are added to the zip if they are not in the standard folder.
    Items in the priority folder take precedence over items in the standard folder.
    """
    with ZipFile(path_to_zip, "w") as zipf:
        for item in folder_path.glob("*"):
            write_item_to_zip(item, zipf, exclude, priority_fld=priority_fld)


def write_item_to_zip(item: Path, zipf: ZipFile, exclude: re.Pattern = None, prefix='', priority_fld: Path = None):
    if exclude and exclude.match(item.name):
        logging.debug(f"Excluding file {item.name}")
        return
    if item.is_dir():
        write_directory(item, zipf, exclude, prefix, priority_fld / item.name)
    else:
        write_file(item, zipf, prefix, priority_fld)


def write_directory(folder: Path, zipf: ZipFile, exclude: re.Pattern = None, prefix='',
                    priority_fld: Path = None):
    prefix = prefix + folder.name + '/'

    # Get all items in the folder
    paths = list(folder.glob("*"))

    # Add items from priority folder that are not in the folder
    item_names = {i.name for i in folder.glob("*")}
    if priority_fld:
        for item in priority_fld.glob("*"):
            if item.name not in item_names:
                paths.append(item)
                logging.debug(f"Using additional file {item.name}")

    for path in paths:
        write_item_to_zip(path, zipf, exclude, prefix, priority_fld)


def set_time_1980(file, prefix=''):
    """
    Ensures that the zip file stays consistent between runs.
    """
    zinfo = ZipInfo(
        prefix + file.name,
        date_time=(1980, 1, 1, 0, 0, 0)
    )
    return zinfo


def write_file(file: Path, zipf: ZipFile, prefix='', priority_fld: Path = None):
    # Use the file from the priority folder if it exists
    if priority_fld and (priority_file := priority_fld / file.name).exists():
        file = priority_file
        logging.debug(f"Prioritizing file {file.name}")

    # For consistency, set the time to 1980
    zinfo = set_time_1980(file, prefix)
    try:
        with open(file) as f:
            zipf.writestr(zinfo, f.read())
    except UnicodeDecodeError as _:
        with open(file, 'rb') as f:
            zipf.writestr(zinfo, f.read())


def predeploy_zip(zipdata: ZipFileData, tmpdir: Path) -> FileData:
    target_folder = Path(zipdata['content_folder'])
    pf = zipdata['priority_folder']
    priority_folder = Path(pf) if pf is not None else None
    if priority_folder is not None and not priority_folder.exists():
        raise FileNotFoundError(priority_folder)

    exclude = re.compile(zipdata['exclude_pattern']) if zipdata['exclude_pattern'] is not None else None

    path_to_zip = tmpdir / zipdata['zip_file_name']
    zip_folder(target_folder, path_to_zip, exclude, priority_folder)

    file = FileData(
        path=str(path_to_zip),
        canvas_folder=zipdata['canvas_folder']
    )

    return file


deploy_zip = deploy_file
lookup_zip = lookup_file
