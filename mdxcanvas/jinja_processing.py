import csv
import json
import jinja2 as jj
from pathlib import Path


def _get_global_args(global_args_path: Path) -> dict:
    if '.json' in global_args_path.name:
        return json.loads(global_args_path.read_text())
    elif '.csv' in global_args_path.name:
        return dict(csv.DictReader(global_args_path.read_text().splitlines()))


def _render_template(template, **kwargs):
    jj_template = jj.Environment().from_string(template)
    kwargs |= dict(zip=zip, split_list=lambda x: x.split(';'))
    return jj_template.render(**kwargs)


def _process_template(template: str, arg_sets: list[dict]):
    return '\n'.join([_render_template(template, **args) for args in arg_sets])


def process_jinja(
        template: str,
        args_path: Path,
        global_args_path: Path = None,
        line_id: str = None,
        **kwargs
) -> str:
    arg_sets = list(csv.DictReader(args_path.read_text().splitlines()))

    if global_args_path:
        kwargs |= _get_global_args(global_args_path)

    if line_id:
        arg_sets = [arg for arg in arg_sets if arg['Id'] == line_id]

    arg_sets = [{**args, **kwargs} for args in arg_sets]

    return _process_template(template, arg_sets)
