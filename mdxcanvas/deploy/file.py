from canvasapi.course import Course
from canvasapi.file import File
from canvasapi.folder import Folder
from pathlib import Path

from mdxcanvas.util import relative_to_abs

from .util import get_canvas_object
from ..resources import FileData, FileInfo, StrLike
from ..our_logging import get_logger

logger = get_logger()

DEFAULT_CANVAS_FOLDER = 'deployed_files'


# Keeping for Checksums retrieval
def get_file(course: Course, name: str) -> File | None:
    return get_canvas_object(course.get_files, 'display_name', name)


def get_canvas_folder(course: Course, folder_name: StrLike, parent_folder_path="") -> Folder:
    """
    Retrieves an object representing a digital folder in Canvas.
    If the folder does not exist, it is created.
    """
    if folder := get_canvas_object(course.get_folders, 'name', folder_name):
        return folder

    logger.debug(f"Creating folder: {folder_name}")
    return course.create_folder(name=folder_name, parent_folder_path=parent_folder_path, hidden=True)


def deploy_file(course: Course, data: FileData, deploy_root: Path) -> tuple[FileInfo, None]:
    lock_at = data.get('lock_at')
    unlock_at = data.get('unlock_at')

    canvas_folder = data.get('canvas_folder') or DEFAULT_CANVAS_FOLDER
    folder = get_canvas_folder(course, canvas_folder)
    file_path = relative_to_abs(Path(data['path']), deploy_root)
    file_id = folder.upload(file_path)[1]['id']
    file = course.get_file(file_id)

    # Update the file with lock_at and unlock_at if provided
    if lock_at or unlock_at:
        file.update(lock_at=lock_at, unlock_at=unlock_at)

    file_object_info: FileInfo = {
        'id': file.id,
        'title': file.display_name,
        'uri': f'/files/{file.id}',
        'url': f'{course.canvas._Canvas__requester.original_url}/courses/{course.id}/files/{file.id}/download'
    }

    return file_object_info, None
