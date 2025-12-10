from canvasapi.course import Course

from .util import update_group_name_to_id
from ..resources import AssignmentInfo


def create_assignment_shell(assignment_data: dict) -> dict:
    """Create minimal assignment shell for cycle resolution"""
    return {
        'name': assignment_data.get('name', 'Placeholder'),
        'description': '<p>Loading...</p>',
        'points_possible': assignment_data.get('points_possible', 0),
        'submission_types': ['none'],
        'published': False,
        'canvas_id': assignment_data.get('canvas_id')
    }


def deploy_assignment(course: Course, assignment_info: dict) -> tuple[AssignmentInfo, None]:
    assignment_id = assignment_info["canvas_id"]

    update_group_name_to_id(course, assignment_info)

    # TODO - update group_category (name) to group_category_id
    #  Is this necessary to support?

    if assignment_id:
        canvas_assignment = course.get_assignment(assignment_id)
        canvas_assignment.edit(assignment=assignment_info)
    else:
        canvas_assignment = course.create_assignment(assignment=assignment_info)

    assignment_object_info: AssignmentInfo = {
        'id': canvas_assignment.id,
        'uri': canvas_assignment.html_url if hasattr(canvas_assignment, 'html_url') else None,
        'url': canvas_assignment.html_url if hasattr(canvas_assignment, 'html_url') else None
    }

    return assignment_object_info, None
