from canvasapi.course import Course

from ..resources import AssignmentGroupInfo


def deploy_group(course: Course, group_data: dict) -> tuple[AssignmentGroupInfo, None]:
    group_id = group_data["canvas_id"]

    if group_id:
        group = course.get_assignment_group(group_id)
    else:
        group = course.create_assignment_group(name=group_data["name"])

    group.edit(**group_data)

    group_object_info: AssignmentGroupInfo = {
        'id': group.id
    }

    return group_object_info, None
