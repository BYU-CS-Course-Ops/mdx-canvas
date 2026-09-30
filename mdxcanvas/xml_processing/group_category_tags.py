from bs4.element import Tag

from .attributes import Attribute, parse_settings, parse_int
from ..resources import ResourceManager, CanvasResource
from ..processing_context import get_current_file_str


class GroupCategoryTagProcessor:
    """
    Processes <group-category> tags into Canvas group category resources.

    A category is how students are teamed up for a kind of work; the groups
    inside it, and their membership, are managed in Canvas rather than declared
    here, because membership changes with enrolment.

    Usage:
        <group-category id="teams" name="Project Teams" self_signup="enabled"
                        group_limit="4" />

    An assignment joins one by id:

        <assignment id="a1" title="Project" group_category="teams" />
    """

    def __init__(self, resource_manager: ResourceManager):
        self._resources = resource_manager

    def __call__(self, category_tag: Tag) -> None:
        attribute_fields = [
            Attribute('id', required=True),
            Attribute('name', required=True),
            # 'enabled' or 'restricted'; restricted confines sign-up to a section.
            Attribute('self_signup'),
            Attribute('group_limit', parser=parse_int),
            # 'first' or 'random'. Canvas rejects it without self_signup.
            Attribute('auto_leader'),
        ]

        category_data = parse_settings(category_tag, attribute_fields)

        self._resources.add_resource(CanvasResource(
            type='group_category',
            id=category_data.pop('id'),
            data=category_data,
            content_path=get_current_file_str()
        ))
