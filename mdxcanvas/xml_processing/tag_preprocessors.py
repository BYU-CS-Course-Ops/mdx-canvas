from pathlib import Path
from bs4 import Tag

from mdxcanvas.resources import ResourceManager, FileData, ZipFileData, CanvasResource


def make_image_preprocessor(parent: Path, resources: ResourceManager):
    def process_image(tag: Tag):
        # TODO - handle b64-encoded images
        src = (parent / tag.get('src')).resolve().absolute()
        file = CanvasResource(
            type='file',
            name=src.name,
            data=FileData(
                path=str(src),
                canvas_folder=tag.get('canvas_folder', None)
            )
        )
        tag['src'] = f'{resources.add_resource(file)}/preview'

    return process_image


def make_file_anchor_tag(resource_key: str, filename: str, **kwargs):
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


def make_file_preprocessor(parent: Path, resources: ResourceManager):
    def process_file(tag: Tag):
        attrs = tag.attrs
        path = (parent / attrs.pop('path')).resolve().absolute()
        file = CanvasResource(
            type='file',
            name=path.name,
            data=FileData(
                path=str(path),
                canvas_folder=attrs.get('canvas_folder', None)
            )
        )
        resource_key = resources.add_resource(file)
        new_tag = make_file_anchor_tag(resource_key, path.name, **tag.attrs)

        tag.replace_with(new_tag)

    return process_file


def make_zip_preprocessor(parent: Path, resources: ResourceManager):
    def process_zip(tag: Tag):
        content_folder = tag.get("path")

        name = tag.get("name")
        if not name:
            name = (
                       content_folder
                       .replace('.', '')
                       .replace('/', '-')
                       .strip('-')
                   ) + '.zip'

        content_folder = str((parent / content_folder).resolve().absolute())

        priority_folder = tag.get("priority_path")
        if priority_folder:
            priority_folder = str((parent / priority_folder).resolve().absolute())

        exclude_pattern = tag.get("exclude")

        file = CanvasResource(
            type='zip',
            name=name,
            data=ZipFileData(
                zip_file_name=name,
                content_folder=content_folder,
                exclude_pattern=exclude_pattern,
                priority_folder=priority_folder,
                canvas_folder=tag.get('canvas_folder')
            )
        )

        resource_key = resources.add_resource(file)

        new_tag = make_file_anchor_tag(resource_key, name)
        tag.replace_with(new_tag)

    return process_zip
