from pathlib import Path

from bs4 import Tag

from .attributes import get_tag_path
from .core import TagProcessor
from ..resources import CanvasResource, FileData, ResourceManager


class ImageTagProcessor(TagProcessor):
    def __init__(self,
                 resources: ResourceManager
                 ):
        super().__init__(10)
        self.resources = resources

    def handles_tag(self, tag: Tag) -> bool:
        return tag.name == 'img'

    def process_tag(self, tag: Tag, parent: Path) -> list[Tag]:
        # TODO - handle b64-encoded images

        src = tag.get('src')
        if src.startswith('http'):
            # No changes necessary
            return []

        # Assume it's a local file
        src = (parent / src).resolve().absolute()
        if not src.is_file():
            raise ValueError(f"Image file {src} is not a file @ {get_tag_path(tag)}")

        file = CanvasResource(
            type='file',
            name=src.name,
            data=FileData(
                path=str(src),
                canvas_folder=tag.get('canvas_folder', None),
                lock_at=None,
                unlock_at=None
            )
        )
        tag['src'] = self.resources.add_resource(file, 'uri') + '/preview'
        return []
