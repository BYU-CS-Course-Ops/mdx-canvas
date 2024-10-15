import csv
import json
import jinja2 as jj
from pathlib import Path

from .markdown_processing import process_markdown_text
from ..util import parse_soup_from_xml, retrieve_contents


def _read_md_table(md_text: str) -> list[dict]:
    # Assume the only thing in the markdown is a single table
    html = process_markdown_text(md_text)

    soup = parse_soup_from_xml(html)
    table = soup.find('table')

    # Thank you, GPT:
    # Extract headers
    headers = [th.text.strip() for th in table.find_all('th')]

    # Iterate over rows and create list of dictionaries
    rows = []
    for tr in table.find_all('tr')[1:]:  # skipping the header row
        cells = tr.find_all(['td', 'th'])
        if len(cells) != len(headers):
            continue  # Skip any rows that do not match the number of headers
        row_data = {headers[i]: retrieve_contents(cells[i]) for i in range(len(headers))}
        rows.append(row_data)

    return rows


def _get_global_args(global_args_path: Path) -> dict:
    if '.json' in global_args_path.name:
        return json.loads(global_args_path.read_text())
    elif '.csv' in global_args_path.name:
        return dict(csv.DictReader(global_args_path.read_text().splitlines()))
    else:
        raise NotImplementedError('Global args file of type: ' + global_args_path.suffix)


def _get_args(args_path: Path) -> list[dict]:
    if args_path.suffix == '.json':
        return json.loads(args_path.read_text())

    elif args_path.suffix == '.csv':
        return list(csv.DictReader(args_path.read_text().splitlines()))

    elif args_path.suffix == '.md':
        return _read_md_table(args_path.read_text())

    else:
        raise NotImplementedError('Args file of type: ' + args_path.suffix)


def _render_template(template, **kwargs):
    jj_template = jj.Environment().from_string(template)
    kwargs |= dict(zip=zip, split_list=lambda x: x.split(';'))
    return jj_template.render(**kwargs)


def _process_template(template: str, arg_sets: list[dict] | None):
    if arg_sets is None:
        return _render_template(template)
    else:
        return '\n'.join([_render_template(template, **args) for args in arg_sets])


def process_jinja(
        template: str,
        args_path: Path = None,
        global_args_path: Path = None,
        **kwargs
) -> str:
    arg_sets = _get_args(args_path) if args_path is not None else None

    if global_args_path:
        kwargs |= _get_global_args(global_args_path)

    if arg_sets is not None:
        arg_sets = [{**args, **kwargs} for args in arg_sets]

    return _process_template(template, arg_sets)
