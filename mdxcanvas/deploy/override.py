from canvasapi.assignment import Assignment
from canvasapi.course import Course

from ..resources import OverrideInfo


def deploy_override(course: Course, override_info: dict) -> tuple[OverrideInfo, None]:
    rtype = override_info.get('rtype')

    # Not necessarily needed, as it never occurs in practice, but just to be safe.
    # Only assignments and quizzes parse overrides.
    if rtype not in ['assignment', 'quiz']:
        raise ValueError(f"Invalid override rtype: {rtype}. Must be 'assignment' or 'quiz'.")

    assignment_id = int(override_info.get('assignment_id'))

    if rtype == 'quiz':
        quiz = course.get_quiz(assignment_id)
        assignment_id = quiz.assignment_id

    assignment: Assignment = course.get_assignment(assignment_id)

    if cid := override_info.get('canvas_id'):
        override = assignment.get_override(cid)
        override.edit(assignment_override=override_info)
    else:
        override = assignment.create_override(assignment_override=override_info)

    override_object_info: OverrideInfo = {
        'id': override.id,
    }

    return override_object_info, None
