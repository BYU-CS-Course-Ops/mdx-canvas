import csv
import json
from pathlib import Path

import jinja2 as jj

import markdowndata

from ..our_logging import get_logger

logger = get_logger()

def _get_args(args_path: Path,
              global_args: dict = None,
              **kwargs
) -> list[dict]:
    if args_path.suffix == '.jinja':
        content = process_jinja(args_path.read_text(),
                                global_args=global_args,
                                **kwargs)

        # Remove the '.jinja' suffix for further processing
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


def _render_template(template, **kwargs):
    jj_template = jj.Environment().from_string(template)
    kwargs |= dict(zip=zip, split_list=lambda x: x.split(';'))
    return jj_template.render(**kwargs)


def _process_template(template: str, arg_sets: list[dict]):
    return '\n'.join([_render_template(template, **args) for args in arg_sets])


def process_jinja(
        template: str,
        args_path: Path = None,
        global_args: dict = None,
        **kwargs
) -> str:

    if args_path:
        arg_sets = _get_args(args_path,
                             global_args=global_args,
                             **kwargs)
    else:
        arg_sets = None

    if global_args:
        kwargs |= global_args

    if arg_sets is not None:
        if isinstance(arg_sets, list):
            arg_sets = [{**args, **kwargs} for args in arg_sets]
        elif isinstance(arg_sets, dict):
            try:
                arg_sets = [{**args, **kwargs} for args in arg_sets.values()]
            except TypeError:
                arg_sets = [{**arg_sets, **kwargs}]
    else:
        arg_sets = [kwargs]

    return _process_template(template, arg_sets)
