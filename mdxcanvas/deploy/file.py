import logging

from canvasapi.course import Course
from canvasapi.file import File
from canvasapi.folder import Folder

from .util import get_canvas_object
from ..resources import FileData

DEFAULT_CANVAS_FOLDER = 'deployed_files'


def get_file(course: Course, name: str) -> File:
    return get_canvas_object(course.get_files, 'display_name', name)


def get_canvas_folder(course: Course, folder_name: str, parent_folder_path="") -> Folder:
    """
    Retrieves an object representing a digital folder in Canvas.
    If the folder does not exist, it is created.
    """
    folder = get_canvas_object(course.get_folders, 'name', folder_name)
    if folder is not None:
        return folder

    logging.debug(f"Creating folder: {folder_name}")
    return course.create_folder(name=folder_name, parent_folder_path=parent_folder_path, hidden=True)


def deploy_file(course: Course, data: FileData):
    canvas_folder = data.get('canvas_folder') or DEFAULT_CANVAS_FOLDER
    folder = get_canvas_folder(course, canvas_folder)
    file_id = folder.upload(data['path'])[1]['id']
    return course.get_file(file_id)


def lookup_file(course: Course, name: str):
    # TODO - do we need to search against the folder also?
    # If so, include the folder in the name (e.g. /unit1/stuff/file.txt)
    # and parse it out here
    return get_file(course, name)
