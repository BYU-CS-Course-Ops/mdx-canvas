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

def _render_template(template: str, args: dict | list = None, global_args: dict = None, key: str = "items") -> str:
    """
    Renders a Jinja template using either a dictionary or a list as context.

    Args:
        template (str): The Jinja2 template string.
        args (dict | list): The context data to render the template.
        key (str, optional): The key under which to nest list data. Defaults to 'items'.

    Returns:
        str: The rendered template string.
    """

    # Compile the template
    jj_template = jj.Environment(trim_blocks=True, lstrip_blocks=True).from_string(template)

    if args:
        # Add global arguments
        if isinstance(args, dict):
            nested_dict_found = False
            for _, value in args.items():
                if isinstance(value, dict):
                    value |= global_args
                    nested_dict_found = True
            if not nested_dict_found:
                args |= global_args

        elif isinstance(args, list):
            for item in args:
                item |= global_args

        else:
            raise TypeError("Args must be a dictionary or a list.")

        if isinstance(args, dict) and _check_dict_value_type(args, dict, ignored_keys=["Group_Weights"]):
            # If args is a dict with string values, use it directly
            context = args
        else:
            context = {key: args}

    elif global_args and not args:
        context = global_args

    else:
        raise ValueError("Either args or global_args must be provided.")

    # Extend with helper functions
    context |= {
        "zip": zip,
        "enumerate": enumerate,
        "split_list": lambda x: x.split(";"),
    }

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
