from pathlib import Path
from typing import cast

from bs4.element import Tag

from .tag_preprocessors import make_file_anchor_tag
from ..error_helpers import validate_required_attribute, format_tag, get_file_path
from ..processing_context import get_current_file_str
from ..resources import QuartoSlidesData
from ..resources import ResourceManager, CanvasResource
from ..util import find_quarto_root


def _find_quarto_dependencies(slide_file: Path) -> list[str]:
    quarto_root = find_quarto_root(slide_file)
    deps = []

    quarto_yaml = quarto_root / '_quarto.yaml'
    if quarto_yaml.exists():
        deps.append(str(quarto_yaml))

    quarto_yaml = quarto_root / '_quarto.yml'
    if quarto_yaml.exists():
        deps.append(str(quarto_yaml))

    extensions = quarto_root / '_extensions'
    if extensions.exists():
        deps.append(str(extensions))

    return deps


def make_quarto_slides_preprocessor(parent: Path, resources: ResourceManager):
    def process_quarto_slides(tag: Tag):
        qmd_file = (
                parent
                / validate_required_attribute(tag, 'path', 'quarto-slides')
        ).resolve().absolute()

        if not qmd_file.exists():
            raise ValueError(
                f"File not found @ {format_tag(tag)}\n  File path: {qmd_file}\n  in {get_file_path(tag)}")

        name = cast(str, tag.get("name"))
        if not name:
            name = qmd_file.name.replace('.qmd', '.slides.html')

        checksum_paths = [str(qmd_file)] + _find_quarto_dependencies(qmd_file)

        # noinspection PyTypeChecker
        file = CanvasResource(
            type='quarto-slides',
            id=name,
            data=QuartoSlidesData(
                path=str(qmd_file),
                root_path=str(parent),
                checksum_paths=checksum_paths,
                slides_name=name,
                canvas_folder=cast(str, tag.get('canvas_folder')),
                lock_at=cast(str, tag.get("lock_at")),
                unlock_at=cast(str, tag.get("unlock_at"))
            ),
            content_path=get_current_file_str()
        )

        resource_key = cast(str, resources.add_resource(file, 'uri'))

        new_tag = make_file_anchor_tag(resource_key, name)
        tag.replace_with(new_tag)

    return process_quarto_slides
