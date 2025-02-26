from canvasapi.assignment import Assignment, AssignmentOverride
from canvasapi.course import Course

from .assignment import get_assignment
from .util import get_canvas_object


def get_override(assignment: Assignment, section_id: int) -> AssignmentOverride:
    return get_canvas_object(assignment.get_overrides, 'course_section_id', section_id)


def get_assignment_and_section(course: Course, name: str) -> tuple[Assignment, int]:
    assignment_name, section_id = name.split('|')
    assignment = get_assignment(course, assignment_name)
    return assignment, int(section_id)


def deploy_override(course: Course, override_info: dict) -> tuple[AssignmentOverride, str | None]:
    name = override_info["name"]

    # Convert assignment name to assignment_id
    assignment, section_id = get_assignment_and_section(course, name)

    if override := get_override(assignment, section_id):
        override.edit(assignment_override=override_info)
    else:
        override = assignment.create_override(assignment_override=override_info)

    return override, None


def lookup_override(course: Course, override_name: str) -> AssignmentOverride:
    assignment, section_id = get_assignment_and_section(course, override_name)
    return get_override(assignment, section_id)
