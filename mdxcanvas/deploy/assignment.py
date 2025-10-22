from canvasapi.assignment import Assignment
from canvasapi.course import Course

from .util import get_canvas_object, update_group_name_to_id
from ..resources import CanvasObjectInfo


def get_assignment(course: Course, name: str) -> Assignment:
    return get_canvas_object(course.get_assignments, 'name', name)


def deploy_assignment(course: Course, assignment_info: dict) -> tuple[CanvasObjectInfo, None]:
    assignment_id = assignment_info["canvas_id"]

    update_group_name_to_id(course, assignment_info)

    # TODO - update group_category (name) to group_category_id
    #  Is this necessary to support?

    # Remove canvas_id before sending to Canvas API
    update_data = assignment_info.copy()
    update_data.pop('canvas_id', None)

    if assignment_id:
        canvas_assignment = course.get_assignment(assignment_id)
        canvas_assignment.edit(assignment=update_data)
    else:
        canvas_assignment = course.create_assignment(assignment=update_data)

    assignment_object_info: CanvasObjectInfo = {
        'id': canvas_assignment.id,
        'uri': None,
        'url': canvas_assignment.html_url if hasattr(canvas_assignment, 'html_url') else None
    }

    return assignment_object_info, None


def lookup_assignment(course: Course, assignment_name: str) -> Assignment:
    return get_assignment(course, assignment_name)
