from canvasapi.assignment import Assignment
from canvasapi.course import Course

from .util import get_canvas_uri, get_canvas_object


def get_assignment(course: Course, name: str) -> Assignment:
    return get_canvas_object(course.get_assignments, 'name', name)


def deploy_assignment(course: Course, assignment_info: dict) -> str:
    name = assignment_info["name"]

    if canvas_assignment := get_assignment(course, name):
        canvas_assignment.edit(assignment=assignment_info)
    else:
        course.create_assignment(assignment=assignment_info)

    return get_canvas_uri(canvas_assignment)


def lookup_assignment(course: Course, assignment_name: str) -> str:
    return get_canvas_uri(get_assignment(course, assignment_name))
