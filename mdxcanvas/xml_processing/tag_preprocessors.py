from pathlib import Path
from typing import Callable

from bs4 import Tag

from ..resources import ResourceManager, FileData, ZipFileData, CanvasResource
from ..util import parse_xml
from ..xml_processing.attributes import parse_bool


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


def _parse_slice(field: str) -> slice:
    """
    Parse a 1-based, inclusive slice
    So, the slice should match the line numbers shown in your IDE
    """
    tokens = field.split(':')
    tokens = [
        int(token) if token else None
        for token in tokens
    ]

    tokens[0] -= 1  # make it 1-based

    if len(tokens) == 1:  # e.g. "3"
        tokens.append(None)

    # Tokens[1] +1 for inclusive, -1 for one-based, net: 0

    return slice(tokens[0], tokens[1])


def make_include_preprocessor(
        parent_folder: Path,
        process_markdown: Callable[[str], str]
):
    def process_include(tag: Tag):
        imported_filename = tag.get('path')
        imported_file = (parent_folder / imported_filename).resolve()
        imported_raw_content = imported_file.read_text()

        lines = tag.get('lines', '')
        if lines:
            grab = _parse_slice(lines)
            imported_raw_content = '\n'.join(imported_raw_content.splitlines()[grab])

        if parse_bool(tag.get('fenced', 'false')):
            imported_raw_content = f'```{imported_file.suffix.lstrip(".")}\n{imported_raw_content}\n```\n'

        imported_html = process_markdown(imported_raw_content)

        new_tag = Tag(name='div')
        new_tag['data-source'] = imported_filename
        if lines:
            new_tag['data-lines'] = lines
        new_tag.extend(parse_xml(imported_html))

        tag.replace_with(new_tag)

    return process_include


def make_link_preprocessor(resources: ResourceManager):
    def process_link(tag: Tag):
        link_type = tag['type']
        link_title = tag['title']

        resource_key = resources.get_resource_key(link_type, link_title)

        new_tag = Tag(name='a')
        new_tag['href'] = resource_key
        # TODO - add other course-link attributes here
        new_tag.string = tag['title']
        tag.replace_with(new_tag)

    return process_link
