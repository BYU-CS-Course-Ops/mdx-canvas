import csv
import json
from pathlib import Path

import jinja2 as jj

import markdowndata

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

    elif args_path.suffix == '.md':
        return markdowndata.loads(content)

    else:
        raise NotImplementedError('Args file of type: ' + args_path.suffix)


def _check_dict_value_type(args: dict, expected_type: type, ignored_keys: list = None) -> bool:
    for key, value in args.items():
        if key in ignored_keys:
            continue
        if isinstance(value, expected_type):
            return False
    return True


def _render_template(template: str, args: dict | list = None, global_args: dict = None) -> str:
    jj_template = jj.Environment(trim_blocks=True, lstrip_blocks=True).from_string(template)

    context = {
        "zip": zip,
        "enumerate": enumerate,
        "split_list": lambda x: x.split(";"),
    }

    if global_args:
        context |= global_args

    if args:
        context |= {"args": args}

    return jj_template.render(context)


def process_jinja(
        template: str,
        args_path: Path = None,
        global_args: dict = None
) -> str:

    if args_path:
        args = _get_args(args_path, global_args)
    else:
        args = {}

    return _render_template(template, args=args, global_args=global_args)
