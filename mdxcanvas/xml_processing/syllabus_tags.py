from bs4 import Tag

from mdxcanvas.resources import ResourceManager, CanvasResource, SyllabusData
from mdxcanvas.util import retrieve_contents


class SyllabusTagProcessor:
    def __init__(self, resources: ResourceManager):
        self._resources = resources

    def __call__(self, tag: Tag):
        syllabus = CanvasResource(
            type='syllabus',
            name='syllabus',
            data=SyllabusData(content=retrieve_contents(tag))
        )
        self._resources.add_resource(syllabus)