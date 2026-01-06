from canvasapi.assignment import Assignment
from canvasapi.course import Course

from ..resources import OverrideInfo

# def deploy_quiz_override(course: Course, quiz_id: int, override_info: dict)-> tuple[AssignmentOverride, str | None]:
#     override_set = course.get_quiz_overrides(**{"quiz_assignment_overrides[][quiz_ids][]": quiz_id})[0]
#
#     if override_set:
#         for override in override_set.overrides:
#             override.edit(**override_info)
#     else:
#         quiz = course.get_quiz(quiz_id)
#         override_set = quiz.create_override(**override_info)
#
#     return override_set, None


def deploy_override(course: Course, override_info: dict) -> tuple[OverrideInfo, None]:
    rtype = override_info.get('rtype')

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
