from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_date, parse_int
from ..resources import ResourceManager, CanvasResource, get_key


def parse_override_tag(override_tag: Tag, parent_type: str, parent_rid: str, resources: ResourceManager):
    """
    Parse an <override> tag that is a child of an assignment or quiz tag.
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
        "rtype": parent_type,
    }

    settings.update(parse_settings(override_tag, fields))

    if settings['rtype'] == 'quiz':
        settings['assignment_id'] = get_key(settings['rtype'], settings['assignment_rid'], 'assignment_id')
    elif settings['rtype'] == 'assignment':
        settings['assignment_id'] = get_key(settings['rtype'], settings['assignment_rid'], 'id')
    else:
        raise ValueError(f'Overrides only support for assignments and quizzes, not {settings['rtype']}')


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
    """
    for override_tag in overrides_tag.findAll('override', recursive=False):
        parse_override_tag(override_tag, parent_type, parent_rid, resources)
