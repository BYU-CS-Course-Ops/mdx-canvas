from canvasapi.course import Course
from canvasapi.assignment import AssignmentGroup

from .util import get_canvas_object


def _get_group(course: Course, name: str) -> AssignmentGroup:
    return get_canvas_object(course.get_assignment_groups, 'name', name)


def _create_group(course: Course, group_name: str) -> AssignmentGroup:
    return course.create_assignment_group(name=group_name)


def _update_group(group: AssignmentGroup, **kwargs) -> AssignmentGroup:
    return group.edit(**kwargs)


def deploy_group(course: Course, group_data: dict) -> tuple[AssignmentGroup, str | None]:
    if not (group := _get_group(course, group_data['name'])):
        group = _create_group(course, group_data['name'])

    group_data.pop('name', None)
    _update_group(group, **group_data)

    return group, None


lookup_group = _get_group
