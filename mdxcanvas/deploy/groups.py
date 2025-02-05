from canvasapi.course import Course
from canvasapi.assignment import AssignmentGroup
from ..our_logging import get_logger
logger = get_logger()


def get_groups(course: Course) -> list[AssignmentGroup]:
    return course.get_assignment_groups()


def get_group(course: Course, group_name: str) -> AssignmentGroup | None:
    for group in get_groups(course):
        if group.name == group_name:
            return group
    return None


def create_group(course: Course, group_name: str) -> AssignmentGroup:
    return course.create_assignment_group(name=group_name)


def update_group(group: AssignmentGroup, **kwargs) -> AssignmentGroup:
    return group.edit(**kwargs)


def initialize_group_weights(course: Course, group_weights: dict):
    course.update(course={'apply_assignment_group_weights': True})
    for group in group_weights:
        if (canvas_group := get_group(course, group)) is None:
            logger.info(f'Creating group: {group}')
            canvas_group = create_group(course, group)

        # Check if the groups weight needs to be updated
        if canvas_group.group_weight != group_weights[group]:
            logger.info(f'Updating group weight: {group}')
            update_group(canvas_group, group_weight=group_weights[group])

