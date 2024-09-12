import hashlib
import json

from canvasapi.course import Course
from canvasapi.file import File

from .syllabus import SyllabusObj


def update_group_name_to_id(course: Course, data: dict):
    if 'assignment_group' in data:
        data['assignment_group_id'] = _get_group_id(course, data['assignment_group'])


def _get_group_id(course: Course, group_name: str) -> int:
    for group in course.get_assignment_groups():
        if group.name == group_name:
            return group.id

    # Group not found - create it
    # TODO - make assignment_group it's own resource
    #  in which case we would throw an error heres
    return course.create_assignment_group(name=group_name).id


def get_canvas_object(course_getter, attr_name, attr):
    objects = course_getter()
    for obj in objects:
        if obj.__getattribute__(attr_name) == attr:
            return obj
    return None


def get_canvas_uri(canvas_obj):
    if hasattr(canvas_obj, 'html_url'):
        html_url: str = canvas_obj.html_url[len('https://'):]
        domain_end_pos = html_url.find('/')
        return html_url[domain_end_pos:]

    elif isinstance(canvas_obj, File):
        return f'/files/{canvas_obj.id}'

    elif isinstance(canvas_obj, SyllabusObj):
        return canvas_obj.uri

    else:
        raise NotImplementedError(type(canvas_obj))


class ResourceNotFoundException(Exception):
    pass
