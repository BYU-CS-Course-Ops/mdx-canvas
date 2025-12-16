from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_date, parse_int
from ..resources import ResourceManager, CanvasResource, get_key


def parse_override_tag(override_tag: Tag, parent_type: str, parent_rid: str, resources: ResourceManager):
    """
    Parse an <override> tag that is a child of an assignment or quiz tag.

    Args:
        override_tag: The <override> BeautifulSoup Tag to parse
        parent_type: The type of the parent tag ('assignment' or 'quiz')
        parent_rid: The resource ID (name/title) of the parent assignment or quiz
        resources: The ResourceManager to add the override resource to
    """
    fields = [
        Attribute('available_from', parser=parse_date, new_name='unlock_at'),
        Attribute('available_to', parser=parse_date, new_name='lock_at'),
        Attribute('due_at', parser=parse_date),
        Attribute('late_due', parser=parse_date),
        Attribute('section_id', new_name='course_section_id', required=True, parser=parse_int),
    ]

    settings = {
        "type": "override",
        "assignment_rid": parent_rid,
        "assignment_id": get_key(parent_type, parent_rid, 'id'),
        "rtype": parent_type,
    }

    settings.update(parse_settings(override_tag, fields))

    # Create unique name for this override: parent_rid|section_id
    override_rid = f"{parent_rid}|{settings['course_section_id']}"

    override_resource = CanvasResource(
        type='override',
        id=override_rid,
        data=settings
    )
    resources.add_resource(override_resource)


def parse_overrides_container(overrides_tag: Tag, parent_type: str, parent_rid: str, resources: ResourceManager):
    """
    Parse an <overrides> container tag that contains multiple <override> child tags.

    Args:
        overrides_tag: The <overrides> BeautifulSoup Tag containing override children
        parent_type: The type of the parent tag ('assignment' or 'quiz')
        parent_rid: The resource ID (name/title) of the parent assignment or quiz
        resources: The ResourceManager to add override resources to
    """
    for override_tag in overrides_tag.findAll('override', recursive=False):
        parse_override_tag(override_tag, parent_type, parent_rid, resources)
