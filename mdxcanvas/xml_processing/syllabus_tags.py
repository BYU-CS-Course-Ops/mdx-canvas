from bs4.element import Tag

from ..resources import ResourceManager, CanvasResource, SyllabusData
from ..util import retrieve_contents
from ..processing_context import get_current_file_str


class SyllabusTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, tag: Tag):
        syllabus = CanvasResource(
            type='syllabus',
            id='syllabus',
            data=SyllabusData(content=retrieve_contents(tag)),
            content_path=get_current_file_str()
        )
        self._resources.add_resource(syllabus)
