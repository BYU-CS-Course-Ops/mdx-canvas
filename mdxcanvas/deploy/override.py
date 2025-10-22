from canvasapi.assignment import AssignmentOverride
from canvasapi.course import Course

from ..resources import CanvasObjectInfo

def deploy_assignment_override(course: Course, assignment_id: int, override_info: dict)-> tuple[CanvasObjectInfo, None]:
    assignment = course.get_assignment(assignment_id)
    has_override = getattr(assignment, 'has_overrides', False)

    if has_override:
        overrides = assignment.get_overrides()
        override = overrides[0]
        override.edit(assignment_override=override_info)
    else:
        override = assignment.create_override(assignment_override=override_info)

    override_object_info: CanvasObjectInfo = {
        'id': override.id,
        'uri': None,
        'url': override.html_url if hasattr(override, 'html_url') else None
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


def deploy_override(course: Course, override_info: dict) -> tuple[CanvasObjectInfo, None]:
    canvas_id = int(override_info["assignment_id"])
    rtype = override_info["rtype"]

    if rtype == 'quiz':
        # deploy_quiz_override(course, canvas_id, override_info)
        raise TypeError("Override type 'quiz' not currently supported for assignment overrides")

    elif rtype == 'assignment':
        return deploy_assignment_override(course, canvas_id, override_info)

    else:
        raise TypeError(f"{rtype} does not support override")