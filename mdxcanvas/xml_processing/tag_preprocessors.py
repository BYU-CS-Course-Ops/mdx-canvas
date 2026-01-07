from pathlib import Path
from typing import Callable

from bs4 import Tag

from ..error_helpers import format_tag, get_file_path, validate_required_attribute
from ..our_logging import get_logger
from ..processing_context import FileContext, get_current_file
from ..resources import ResourceManager, FileData, ZipFileData, CanvasResource, get_key
from ..util import parse_soup_from_xml
from ..xml_processing.attributes import parse_bool, get_tag_path

logger = get_logger()


def make_course_settings_preprocessor(parent: Path, resources: ResourceManager):
    def process_course_settings(tag: Tag):
        name = tag.get('name')
        course_code = tag.get('code')
        image_path = tag.get('image')

        if not (any([name, course_code, image_path])):
            raise ValueError(
                f"Course settings tag must have at least one of: name, code, or image @ {format_tag(tag)}\n  in {get_file_path(tag)}")

        image_resource_key = None
        if image_path:
            image_path = (parent / image_path).resolve().absolute()
            if not image_path.is_file():
                raise ValueError(
                    f"Course image file not found @ {format_tag(tag)}\n  Image path: {image_path}\n  in {get_file_path(tag)}")

            file = CanvasResource(
                type='file',
                id=image_path.name,
                data=FileData(
                    path=str(image_path),
                    canvas_folder=tag.get('canvas_folder', None)
                ),
                content_path=str(get_current_file().resolve())
            )
            image_resource_key = resources.add_resource(file, 'id')

        course_settings = CanvasResource(
            type='course_settings',
            id='',
            data={
                'name': name,
                'code': course_code,
                'image': image_resource_key
            },
            content_path=str(get_current_file().resolve())
        )
        resources.add_resource(course_settings, 'name')

    return process_course_settings


def make_image_preprocessor(parent: Path, resources: ResourceManager):
    def process_image(tag: Tag):
        # TODO - handle b64-encoded images

        src = validate_required_attribute(tag, 'src', 'img')
        if src.startswith('http') or src.startswith('__@@'):
            # No changes necessary
            return

        # Assume it's a local file
        src_path = (parent / src).resolve().absolute()
        if not src_path.is_file():
            raise ValueError(
                f"Image file not found @ {format_tag(tag)}\n  File path: {src_path}\n  in {get_file_path(tag)}")
        src = src_path

        file = CanvasResource(
            type='file',
            id=src.name,
            data=FileData(
                path=str(src),
                canvas_folder=tag.get('canvas_folder', None)
            ),
            content_path=str(get_current_file().resolve())
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
        path_value = validate_required_attribute(tag, 'path', 'file')
        attrs = tag.attrs
        path = (parent / path_value).resolve().absolute()
        if not path.is_file():
            raise ValueError(f"File not found @ {format_tag(tag)}\n  File path: {path}\n  in {get_file_path(tag)}")
        # Only pop the path after validation succeeds
        attrs.pop('path')
        file = CanvasResource(
            type='file',
            id=path.name,
            data=FileData(
                path=str(path),
                canvas_folder=attrs.get('canvas_folder', None),
                unlock_at=attrs.get('unlock_at', None),
                lock_at=attrs.get('lock_at', None)
            ),
            content_path=str(get_current_file().resolve())
        )
        resource_key = resources.add_resource(file, 'uri')
        new_tag = make_file_anchor_tag(resource_key, path.name, **tag.attrs)

        tag.replace_with(new_tag)

    return process_file


def make_zip_preprocessor(parent: Path, resources: ResourceManager):
    def process_zip(tag: Tag):
        content_folder = validate_required_attribute(tag, 'path', 'zip')

        name = tag.get("name")
        if not name:
            name = (
                       content_folder
                       .replace('.', '')
                       .replace('/', '-')
                       .strip('-')
                   ) + '.zip'

        content_folder_path = (parent / content_folder).resolve().absolute()
        if not content_folder_path.exists():
            raise ValueError(
                f"Folder not found @ {format_tag(tag)}\n  Folder path: {content_folder_path}\n  in {get_file_path(tag)}")
        content_folder = str(content_folder_path)

        additional_files = tag.get("additional_files")
        if additional_files:
            additional_files = [str((parent / file).resolve().absolute()) for file in additional_files.split(',')]

        priority_folder = tag.get("priority_path")
        if priority_folder:
            priority_folder = str((parent / priority_folder).resolve().absolute())

        exclude_pattern = tag.get("exclude")

        file = CanvasResource(
            type='zip',
            id=name,
            data=ZipFileData(
                zip_file_name=name,
                content_folder=content_folder,
                additional_files=additional_files,
                exclude_pattern=exclude_pattern,
                priority_folder=priority_folder,
                canvas_folder=tag.get('canvas_folder')
            ),
            content_path=str(get_current_file().resolve())
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
        args_file_path = tag.get('args', None)

        # Check if the included file exists first
        if not imported_file.exists():
            containing_file = get_current_file() or "unknown file"
            raise FileNotFoundError(
                f"Include file not found @ {format_tag(tag)}\n"
                f"  in {containing_file}"
            )

        args_file = None
        if args_file_path is not None:
            args_file = (parent_folder / args_file_path).resolve().absolute()

            # Check if args file exists
            if not args_file.exists():
                containing_file = get_current_file() or "unknown file"
                raise FileNotFoundError(
                    f"Args file not found @ {format_tag(tag)}\n"
                    f"  in {containing_file}"
                )

        # Track the included file in context for error messages
        with FileContext(imported_file):
            imported_raw_content = imported_file.read_text(encoding='utf-8')
            suffixes = imported_file.suffixes

            lines = tag.get('lines', '')
            if lines:
                grab = _parse_slice(lines)
                imported_raw_content = '\n'.join(imported_raw_content.splitlines()[grab])

            if parse_bool(tag.get('fenced', 'false')):
                imported_raw_content = f'```{imported_file.suffix.lstrip(".")}\n{imported_raw_content}\n```\n'
                suffixes = suffixes + ['.md']

            imported_html = process_file(
                imported_file.parent,
                imported_raw_content,
                suffixes,
                args_file=args_file
            )

            use_div = parse_bool(tag.get('usediv', 'true'))

            include_result = parse_soup_from_xml(imported_html)

            if not use_div:
                tag.replace_with(include_result)

            else:
                new_tag = Tag(name='div')
                new_tag['data-source'] = str(imported_file)
                if lines:
                    new_tag['data-lines'] = lines
                new_tag.extend(include_result)
                tag.replace_with(new_tag)

    return process_include


def make_link_preprocessor():
    def process_link(tag: Tag):
        link_type = validate_required_attribute(tag, 'type', 'course-link')
        # TODO: Canvas supports `course navigation` links, do we?
        if link_type not in ['syllabus', 'page', 'assignment', 'quiz', 'announcement', 'discussion', 'module', 'file']:
            raise ValueError(f'Invalid course-link type "{link_type}" @ {format_tag(tag)}\n  in {get_file_path(tag)}')

        link_rid = validate_required_attribute(tag, 'id', 'course-link')

        new_tag = Tag(name='a')
        new_tag['href'] = get_key(link_type, link_rid, 'uri')
        link_text = tag.string.strip() if tag.string is not None else ''
        if not link_text:
            link_text = get_key(link_type, link_rid, 'title')
        new_tag.string = link_text
        tag.replace_with(new_tag)

    return process_link


def make_markdown_page_preprocessor(
        parent_folder: Path,
        process_file: Callable
):
    def process_markdown_page(tag: Tag):
        content_path = validate_required_attribute(tag, 'path', 'md-page')
        content_path_obj = Path(parent_folder) / content_path

        page_title = tag.get('title')
        if page_title is None:
            # Only read file if it exists for getting the title
            if content_path_obj.exists():
                first_line = content_path_obj.read_text().splitlines()[0]
                if first_line.startswith('# '):
                    page_title = first_line.strip('#').strip()
                else:
                    page_title = content_path_obj.stem
            else:
                # File doesn't exist, use filename as title
                page_title = content_path_obj.stem

        include_tag = Tag(name='include', attrs={'path': content_path})

        page_tag = Tag(name='page', attrs={'title': page_title})
        page_tag.append(include_tag)

        if (page_id := tag.get('id', None)) is not None:
            page_tag['id'] = page_id

        include_processor = make_include_preprocessor(parent_folder, process_file)

        try:
            include_processor(include_tag)  # Replaces include_tag with new content
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found @ {format_tag(tag)}\n  in {get_file_path(tag)}") from e

        tag.replace_with(page_tag)

    return process_markdown_page
