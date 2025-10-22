from canvasapi.course import Course
from canvasapi.assignment import AssignmentGroup

from .util import get_canvas_object
from ..resources import CanvasObjectInfo


def _get_group(course: Course, name: str) -> AssignmentGroup:
    return get_canvas_object(course.get_assignment_groups, 'name', name)


def _create_group(course: Course, group_name: str) -> AssignmentGroup:
    return course.create_assignment_group(name=group_name)


def _update_group(group: AssignmentGroup, **kwargs) -> AssignmentGroup:
    return group.edit(**kwargs)


def deploy_group(course: Course, group_data: dict) -> tuple[CanvasObjectInfo, None]:
    group_id = group_data["canvas_id"]

    if group_id:
        group = course.get_assignment_group(group_id)
    else:
        group = _create_group(course, group_data['name'])

    # Remove fields that shouldn't be sent to Canvas API
    update_data = group_data.copy()
    update_data.pop('canvas_id', None)
    _update_group(group, **update_data)

    group_object_info: CanvasObjectInfo = {
        'id': group.id,
        'uri': None,
        'url': group.html_url if hasattr(group, 'html_url') else None
    }

    return group_object_info, None


lookup_group = _get_group
