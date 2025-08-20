from pathlib import Path

from bs4 import Tag

from .attributes import get_tag_path
from .core import TagProcessor
from ..resources import ResourceManager, FileData, CanvasResource


def make_file_anchor_tag(resource_key: str, filename: str, **kwargs):
    """Make an anchor tag for a file in Canvas"""
    attrs = {
        **kwargs,
        'href': f'{resource_key}?wrap=1',
        'class': 'instructure_file_link inline_disabled',
        'title': filename,
        'target': '_blank',
        'rel': 'noopener noreferrer'
    }

    new_tag = Tag(name='a', attrs=attrs)
    new_tag.string = filename

    return new_tag


class FileTagProcessor(TagProcessor):
    def __init__(self,
                 resources: ResourceManager,
                 ):
        super().__init__(10)
        self.resources = resources

    def handles_tag(self, tag: Tag) -> bool:
        return tag.name == 'file'

    def process_tag(self, tag: Tag, parent: Path) -> list[Tag]:
        attrs = tag.attrs
        path = (parent / attrs.pop('path')).resolve().absolute()
        if not path.is_file():
            raise ValueError(f"File {path} is not a file @ {get_tag_path(tag)}")
        file = CanvasResource(
            type='file',
            name=path.name,
            data=FileData(
                path=str(path),
                canvas_folder=attrs.get('canvas_folder', None),
                unlock_at=attrs.get('unlock_at', None),
                lock_at=attrs.get('lock_at', None)
            )
        )
        resource_key = self.resources.add_resource(file, 'uri')
        return [make_file_anchor_tag(resource_key, path.name, **tag.attrs)]
