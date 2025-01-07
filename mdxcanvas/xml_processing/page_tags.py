from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_bool, parse_date
from ..util import retrieve_contents
from ..resources import ResourceManager, CanvasResource


class PageTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, page_tag: Tag):
        settings = {
            "type": "page",
            "body": retrieve_contents(page_tag),
        }

        fields = [
            Attribute('title', required=True),
            Attribute('editing_roles', 'teachers'),
            Attribute('notify_of_update', False, parse_bool),
            Attribute('student_todo_at', parser=parse_date),
            Attribute('front_page', False, parse_bool),
            Attribute('published', parser=parse_bool),
            Attribute('publish_at', parser=parse_date)
        ]

        settings.update(parse_settings(page_tag, fields))

        page = CanvasResource(
            type='page',
            name=settings['title'],
            data=settings
        )
        self._resources.add_resource(page)
