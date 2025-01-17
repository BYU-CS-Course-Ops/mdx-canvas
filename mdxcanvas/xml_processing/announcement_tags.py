from datetime import datetime

from bs4 import Tag

from .attributes import parse_settings, Attribute, parse_date, parse_bool
from ..resources import ResourceManager, CanvasResource
from ..util import retrieve_contents


class AnnouncementTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, announcement_tag: Tag):
        # Note - it appears you can edit announcement that haven't published yet
        # Not sure if you can edit announcements that have published already
        # Gordon Bean (Jan 17, 2025)

        fields = [
            Attribute('title', required=True),
            Attribute('is_announcement', True, parser=parse_bool),
            Attribute('publish_date', required=True, new_name='delayed_post_at', parser=parse_date,
                      default=datetime.now().isoformat()),
        ]

        # https://canvas.instructure.com/doc/api/discussion_topics.html#method.discussion_topics.create
        # delayed_post_at
        # is_section_specific
        # permissions.reply
        # published
        # specific_sections

        settings = {
            "type": "discussion_topics",
            "message": retrieve_contents(announcement_tag)
        }

        settings.update(parse_settings(announcement_tag, fields))

        announcement = CanvasResource(
            type='announcement',
            name=settings['title'],
            data=settings,
        )
        self._resources.add_resource(announcement)
