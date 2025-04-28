from pathlib import Path
from typing import Callable

from bs4 import Tag

from ..resources import ResourceManager, FileData, ZipFileData, CanvasResource, get_key
from ..util import parse_soup_from_xml
from ..xml_processing.attributes import parse_bool, get_tag_path


def make_image_preprocessor(parent: Path, resources: ResourceManager):
    def process_image(tag: Tag):
        # TODO - handle b64-encoded images

        src = tag.get('src')
        if src.startswith('http'):
            # No changes necessary
            return

        # Assume it's a local file
        src = (parent / src).resolve().absolute()
        if not src.is_file():
            raise ValueError(f"Image file {src} is not a file @ {get_tag_path(tag)}")

        file = CanvasResource(
            type='file',
            name=src.name,
            data=FileData(
                path=str(src),
                canvas_folder=tag.get('canvas_folder', None)
            )
        )
        tag['src'] = resources.add_resource(file, 'uri') + '/preview'

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
        resource_key = resources.add_resource(file, 'uri')
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

        additional_files = tag.get("additional_files")
        if additional_files:
            additional_files = [str((parent / file).resolve().absolute()) for file in additional_files.split(',')]

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
                additional_files=additional_files,
                exclude_pattern=exclude_pattern,
                priority_folder=priority_folder,
                canvas_folder=tag.get('canvas_folder')
            )
        )

        resource_key = resources.add_resource(file, 'uri')

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
        process_file: Callable
):
    def process_include(tag: Tag):
        imported_filename = tag.get('path')
        imported_file = (parent_folder / imported_filename).resolve()

        imported_raw_content = imported_file.read_text(encoding='utf-8')
        suffixes = imported_file.suffixes

        lines = tag.get('lines', '')
        if lines:
            grab = _parse_slice(lines)
            imported_raw_content = '\n'.join(imported_raw_content.splitlines()[grab])

        if parse_bool(tag.get('fenced', 'false')):
            imported_raw_content = f'```{imported_file.suffix.lstrip(".")}\n{imported_raw_content}\n```\n'
            suffixes = suffixes + ['.md']

        args_file = tag.get('args', None)
        if args_file is not None:
            # Note: the args file, like the path, is relative to the primary file, not the included file
            args_file = (parent_folder / args_file).resolve().absolute()

        imported_html = process_file(
            imported_file.parent,
            imported_raw_content,
            suffixes,
            args_file=args_file
        )

        use_div = parse_bool(tag.get('usediv', 'true'))

        include_result = parse_soup_from_xml(imported_html)

        if not use_div:
            tag.parent.extend(include_result)

        else:
            new_tag = Tag(name='div')
            new_tag['data-source'] = imported_filename
            if lines:
                new_tag['data-lines'] = lines
            new_tag.extend(include_result)
            tag.replace_with(new_tag)

    return process_include


def make_link_preprocessor():
    def process_link(tag: Tag):
        link_type = tag['type']
        link_title = tag['title']

        new_tag = Tag(name='a')
        new_tag['href'] = get_key(link_type, link_title, 'uri')
        # TODO - add other course-link attributes here
        link_text = tag.string.strip() if tag.string is not None else ''
        if not link_text:
            link_text = tag['title']
        new_tag.string = link_text
        tag.replace_with(new_tag)

    return process_link


def make_markdown_page_preprocessor(
        parent_folder: Path,
        process_file: Callable
):
    def process_markdown_page(tag: Tag):
        content_path = tag['path']

        page_title = tag.get('title')
        if page_title is None:
            page_title = Path(content_path).stem

        include_tag = Tag(name='include', attrs={'path': content_path})

        page_tag = Tag(name='page', attrs={'title': page_title})
        page_tag.append(include_tag)

        include_processor = make_include_preprocessor(parent_folder, process_file)
        include_processor(include_tag)  # Replaces include_tag with new content

        tag.replace_with(page_tag)

    return process_markdown_page
