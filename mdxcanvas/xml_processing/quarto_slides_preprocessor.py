from pathlib import Path

from bs4 import Tag

from .tag_preprocessors import make_file_anchor_tag
from ..error_helpers import validate_required_attribute, format_tag, get_file_path
from ..processing_context import get_current_file
from ..resources import QuartoSlidesData
from ..resources import ResourceManager, CanvasResource


def _find_quarto_dependencies(parent: Path) -> list[str]:
    deps = []
    cur_dir = parent.absolute()
    while True:
        quarto_yaml = cur_dir / '_quarto.yaml'

        if quarto_yaml.exists():
            deps.append(str(quarto_yaml))
            extensions = cur_dir / '_extensions'
            if extensions.exists():
                deps.append(str(extensions))
            break

        if cur_dir.parent == cur_dir.parent:  # i.e. we're at root now
            break

        cur_dir = cur_dir.parent

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

        name = tag.get("name")
        if not name:
            name = qmd_file.stem + '.slides.html'

        checksum_paths = [str(qmd_file)] + _find_quarto_dependencies(parent)

        # noinspection PyTypeChecker
        file = CanvasResource(
            type='quarto-slides',
            id=name,
            data=QuartoSlidesData(
                path=str(qmd_file),
                checksum_paths=checksum_paths,
                slides_name=name,
                canvas_folder=tag.get('canvas_folder'),
                lock_at=tag.get("lock_at"),
                unlock_at=tag.get("unlock_at")
            ),
            content_path=str(get_current_file().resolve())
        )

        resource_key = resources.add_resource(file, 'uri')

        new_tag = make_file_anchor_tag(resource_key, name)
        tag.replace_with(new_tag)

    return process_quarto_slides
