from canvasapi.course import Course

from .util import update_group_name_to_id
from ..resources import AssignmentInfo

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
        'url': canvas_assignment.html_url,
    }

    return assignment_object_info, None


def deploy_shell_assignment(course: Course, assignment_info: dict) -> tuple[AssignmentInfo, None]:
    shell_assignment_info = assignment_info.copy()
    shell_assignment_info['description'] = "<p>This is a shell assignment created to break a dependency cycle. The full content will be deployed later.</p>"

    return deploy_assignment(course, shell_assignment_info)
