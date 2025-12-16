from canvasapi.assignment import Assignment
from canvasapi.course import Course

from ..resources import OverrideInfo

def deploy_assignment_override(course: Course, assignment_id: int, override_info: dict)-> tuple[OverrideInfo, None]:
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
    canvas_id = int(override_info["assignment_id"])
    rtype = override_info["rtype"]

    if rtype == 'quiz':
        # deploy_quiz_override(course, canvas_id, override_info)
        raise TypeError("Override type 'quiz' not currently supported for assignment overrides")

    elif rtype == 'assignment':
        return deploy_assignment_override(course, canvas_id, override_info)

    else:
        # TODO: Try to support Quiz overrides
        raise TypeError(f"{rtype} does not support override")