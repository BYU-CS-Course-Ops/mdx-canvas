from canvasapi.assignment import Assignment, AssignmentOverride
from canvasapi.course import Course

from mdxcanvas.resources import OverrideInfo
from ..resources import OverrideInfo


def get_override(course: Course, assignment_id: int, override_id: int) -> AssignmentOverride | None:
    if assignment := course.get_assignment(assignment_id):
        return assignment.get_override(override_id)

    return None


def _get_assignment(course: Course, override_info: dict) -> Assignment:
    rtype = override_info.get('rtype')

    # Not necessarily needed, as it never occurs in practice, but just to be safe.
    # Only assignments and quizzes parse overrides.
    if rtype not in ['assignment', 'quiz']:
        raise ValueError(f"Invalid override rtype: {rtype}. Must be 'assignment' or 'quiz'.")

    assignment_id = int(override_info.get('assignment_id'))

    if rtype == 'quiz':
        # Quizzes are unique in that they have two IDs: the quiz ID and the assignment ID.
        # To get and modify a quizzes override, we need the assignment ID which we do not track directly.
        # This step gets the quiz object to retrieve the assignment ID.

        quiz = course.get_quiz(assignment_id)
        assignment_id = quiz.assignment_id

    return course.get_assignment(assignment_id)


def deploy_override(course: Course, override_info: dict) -> OverrideInfo:
    assignment: Assignment = _get_assignment(course, override_info)

    if cid := override_info.get('canvas_id'):
        override = assignment.get_override(cid)
        override.edit(assignment_override=override_info)
    else:
        override = assignment.create_override(assignment_override=override_info)

    override_object_info: OverrideInfo = {
        'id': override.id,
        'assignment_id': assignment.id
    }

    return override_object_info
