from bs4 import Tag

from mdxcanvas.resources import ResourceManager, CanvasResource, SyllabusData
from mdxcanvas.util import retrieve_contents
from mdxcanvas.processing_context import get_current_file


class SyllabusTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, tag: Tag):
        syllabus = CanvasResource(
            type='syllabus',
            id='syllabus',
            data=SyllabusData(content=retrieve_contents(tag)),
            content_path=str(get_current_file().resolve())
        )
        self._resources.add_resource(syllabus)
