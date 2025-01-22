from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_date, parse_int
from ..resources import ResourceManager, CanvasResource, get_key


class OverrideTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, override_tag: Tag):
        fields = [
            Attribute('available_from', parser=parse_date, new_name='unlock_at'),
            Attribute('available_to', parser=parse_date, new_name='lock_at'),
            Attribute('due_at', parser=parse_date),
            Attribute('late_due', parser=parse_date),
            Attribute('title'),  # required if using student IDs
            Attribute('section_id', new_name='course_section_id', required=True, parser=parse_int),
            # TODO - support student IDs also
            Attribute('title', new_name='assignment_name', required=True),  # name of assignment to modify with this override
            Attribute('type', new_name='rtype', required=True)
        ]

        settings = {
            "type": "override",
        }

        settings.update(parse_settings(override_tag, fields))

        settings['name'] = f"{settings['assignment_name']}|{settings['course_section_id']}"
        settings['assignment_id'] = get_key(settings['rtype'], settings['assignment_name'], 'id')

        assignment = CanvasResource(
            type='override',
            name=settings['name'],
            data=settings
        )
        self._resources.add_resource(assignment)
