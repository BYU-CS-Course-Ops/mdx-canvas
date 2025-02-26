import logging
import re
from pathlib import Path
from zipfile import ZipFile, ZipInfo

from .file import deploy_file, lookup_file
from ..our_logging import get_logger
from ..resources import ZipFileData, FileData

logger = get_logger()


def zip_folder(
        folder_path: Path,
        path_to_zip: Path,
        additional_files: list[Path] | None,
        exclude: re.Pattern = None,
        priority_folder: Path = None
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


def get_files(folder_path: Path, exclude: re.Pattern | None, prefix) -> dict[str, Path]:
    if not folder_path.exists():
        raise FileNotFoundError(folder_path)

    files = {}
    for file in folder_path.glob('*'):
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


def write_file(file: Path, zip_name: str, zipf: ZipFile):
    zinfo = make_zip_info(zip_name)
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
        canvas_folder=zipdata['canvas_folder']
    )

    return file


deploy_zip = deploy_file
lookup_zip = lookup_file
