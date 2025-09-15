from bs4 import Tag
from canvasapi.course import Course
from canvasapi.assignment import AssignmentGroup

from .attributes import Attribute, parse_bool, parse_settings, parse_int
from ..resources import ResourceManager, get_key, CanvasResource

class AssignmentGroupsTagProcessor:
    """
    Processes <assignment-groups> tags.

    Usage:
        <assignment-groups>
            <group name="Group 1" weight="25" drop="5" />
            <group name="Group 2" weight="75" drop="3" />
        </assignment-groups>
    """
    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager

    def __call__(self, assignment_groups_tag: Tag):
        for group_tag in assignment_groups_tag.find_all('group'):
            self._parse_assignment_group(group_tag)

    def _parse_assignment_group(self, tag: Tag):
        fields = [
            Attribute('name', required=True),
            Attribute('weight', parser=parse_int),
            Attribute('drop', 0, parse_int),
            Attribute('keep', None, parse_int),
            Attribute('position', None, parse_int),
            Attribute('group_category'),
            Attribute('rules', {}, parser=parse_settings),  # Additional rules can be added here
            Attribute('published', False, parse_bool)
        ]

        group_data = parse_settings(tag, fields)

        group_name = group_data.pop('name')

        assignment_group = CanvasResource(
            type='assignment_group',
            name=group_name,
            data=group_data
        )
        self._resources.add_resource(assignment_group)

        # Optionally, link the group to a course if specified


