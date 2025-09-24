from bs4 import Tag
from typing import TypedDict, List

from .attributes import Attribute, parse_settings, parse_int
from ..resources import ResourceManager, CanvasResource, get_key


class AssignmentGroupRules(TypedDict, total=False):
    drop_lowest: int
    drop_highest: int
    never_drop: List[int]


def _parse_never_drop_assignments(tag: Tag) -> List[int]:
    never_drop_attr = tag.get('never_drop')
    if not never_drop_attr:
        return []

    never_drop_ids = []
    assignment_names = [name.strip() for name in never_drop_attr.split('|')]

    for assignment_name in assignment_names:
        if assignment_name:
            try:
                assignment_id = get_key('assignment', assignment_name, 'id')
                never_drop_ids.append(assignment_id)
            except Exception as e:
                continue

    return never_drop_ids


def _extract_rules_from_group_data(group_data: dict) -> dict:
    rules: AssignmentGroupRules = {}

    if 'drop_lowest' in group_data and group_data['drop_lowest'] is not None:
        rules['drop_lowest'] = group_data.pop('drop_lowest')

    if 'drop_highest' in group_data and group_data['drop_highest'] is not None:
        rules['drop_highest'] = group_data.pop('drop_highest')

    if 'never_drop' in group_data and group_data['never_drop']:
        rules['never_drop'] = group_data.pop('never_drop')

    if rules:
        group_data['rules'] = rules

    return group_data


class AssignmentGroupTagProcessor:
    """
    Processes <assignment-groups> tags and converts them to Canvas assignment group resources.

    Usage:
        <assignment-groups>
            <group name="Group 1" weight="25" drop_lowest="5" />
            <group name="Group 2" weight="75" drop_highest="3" never_drop="assign1|assign2" />
        </assignment-groups>
    """

    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager

    def __call__(self, group_tag: Tag) -> None:
        self._parse_assignment_group(group_tag)

    def _parse_assignment_group(self, tag: Tag) -> None:
        """
        Parse a single assignment group tag and add it to the resource manager.

        Args:
            tag: The assignment group tag to parse
        """
        never_drop_ids = _parse_never_drop_assignments(tag)

        attribute_fields = [
            Attribute('name', required=True),
            Attribute('weight', new_name='group_weight', parser=parse_int),
            Attribute('drop_lowest', parser=parse_int),
            Attribute('drop_highest', parser=parse_int)
            # TODO: Find additional attributes to support
        ]

        group_data = parse_settings(tag, attribute_fields)
        group_data['never_drop'] = never_drop_ids
        group_data = _extract_rules_from_group_data(group_data)

        assignment_group = CanvasResource(
            type='assignment_group',
            name=group_data['name'],
            data=group_data
        )

        self._resources.add_resource(assignment_group)
