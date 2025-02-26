from canvasapi.assignment import Assignment
from canvasapi.course import Course

from .util import get_canvas_object, update_group_name_to_id


def get_assignment(course: Course, name: str) -> Assignment:
    return get_canvas_object(course.get_assignments, 'name', name)


def deploy_assignment(course: Course, assignment_info: dict) -> tuple[Assignment, str|None]:
    name = assignment_info["name"]

    update_group_name_to_id(course, assignment_info)

    # TODO - update group_category (name) to group_category_id
    #  Is this necessary to support?

    if canvas_assignment := get_assignment(course, name):
        canvas_assignment.edit(assignment=assignment_info)
    else:
        canvas_assignment = course.create_assignment(assignment=assignment_info)

    return canvas_assignment, None


def lookup_assignment(course: Course, assignment_name: str) -> Assignment:
    return get_assignment(course, assignment_name)
