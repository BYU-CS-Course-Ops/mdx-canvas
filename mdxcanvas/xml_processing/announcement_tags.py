from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_date
from ..resources import ResourceManager, CanvasResource
from ..util import retrieve_contents


class AnnouncementTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, announcement_tag: Tag):
        fields = [
            Attribute('title', new_name='name', required=True),
            Attribute('is_announcement', True),
            Attribute('posted_at', required=True, new_name='upload_at', parser=parse_date),
        ]

        settings = {
            "type": "discussion_topics",
            "message": retrieve_contents(announcement_tag)
        }

        settings.update(parse_settings(announcement_tag, fields))

        announcement = CanvasResource(
            type='discussion_topics',
            name=settings['name'],
            data=settings,
        )
        self._resources.add_resource(announcement)
