import csv
import json
import re
from pathlib import Path
from typing import Optional, cast

import markdowndata
import yaml
from jinja2 import Environment, FileSystemLoader

from ..our_logging import get_logger
from ..processing_context import get_current_file_str

logger = get_logger()


def _get_args(args_path: Path, global_args: Optional[dict]) -> dict | list:
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
        parent_folder: Optional[Path] = None,
        args_path: Optional[Path] = None,
        args: Optional[dict | list] = None,
        global_args: Optional[dict] = None,
        templates: Optional[list[Path]] = None
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
        "exists": lambda path: (cast(Path, parent_folder) / path).exists(),
        "read_file": lambda f: (cast(Path, parent_folder) / f).absolute().read_text(),
        "glob": lambda *args, **kwargs: list(sorted(str(f.relative_to(cast(Path, parent_folder))) for f in
                                         cast(Path, parent_folder).glob(*args, **kwargs))),
        "parent": lambda path: str(Path(path).parent),
        "load": lambda path: _get_args((cast(Path, parent_folder) / path).absolute(), global_args),
        "debug": lambda msg: logger.debug(msg),
        "get_arg": lambda *args: cast(dict, global_args).get(*args),
        # "grep": lambda pattern, string, *args: m.groups() if (m := re.search(pattern, string, *args)) else None
        "search": re.search
    }

    if global_args:
        context |= global_args

    if args:
        context |= {"args": args}

    try:
        jj_template = env.from_string(template)
        return jj_template.render(context)
    except Exception as ex:
        raise Exception(f'Error processing {get_current_file_str()}', ex)


def process_jinja(
        template: str,
        parent_folder: Optional[Path] = None,
        args_path: Optional[Path] = None,
        global_args: Optional[dict] = None,
        templates: Optional[list[Path]] = None
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
