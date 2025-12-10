import csv
import json
from pathlib import Path

import markdowndata
import yaml
from jinja2 import Environment, FileSystemLoader

from ..our_logging import get_logger

logger = get_logger()


def _get_args(args_path: Path, global_args: dict) -> dict | list:
    if args_path.suffix == '.jinja':
        content = _render_template(args_path.read_text(), global_args=global_args)
        args_path = Path(args_path.stem)
    else:
        content = args_path.read_text()

    if args_path.suffix == '.json':
        return json.loads(content)

    elif args_path.suffix == '.csv':
        return list(csv.DictReader(content.splitlines()))

    elif args_path.suffix in ['.md', '.mdd']:
        return markdowndata.loads(content)

    elif args_path.suffix in ['.yaml', '.yml']:
        return yaml.safe_load(content)

    else:
        raise NotImplementedError('Args file of type: ' + args_path.suffix)


def _render_template(
        template: str,
        parent_folder: Path = None,
        args_path: Path = None,
        args: dict | list = None,
        global_args: dict = None,
        templates: list[Path] = None
) -> str:
    loader_paths = [parent_folder, args_path, *(templates or [])]
    loader_paths = [p for p in loader_paths if p is not None]

    env = Environment(
        loader=FileSystemLoader(loader_paths),
    )

    context = {
        "zip": zip,
        "enumerate": enumerate,
        "split_list": lambda x: x.split(";"),
        "read_file": lambda f: (parent_folder / f).absolute().read_text()
    }

    if global_args:
        context |= global_args

    if args:
        context |= {"args": args}

    jj_template = env.from_string(template)
    return jj_template.render(context)


def process_jinja(
        template: str,
        parent_folder: Path = None,
        args_path: Path = None,
        global_args: dict = None,
        templates: list[Path] = None
) -> str:
    if args_path:
        args = _get_args(args_path, global_args)
    else:
        args = {}

    return _render_template(
        template,
        parent_folder=parent_folder,
        args_path=args_path,
        args=args,
        global_args=global_args,
        templates=templates
    )
