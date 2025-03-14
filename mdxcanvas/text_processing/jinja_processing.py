import csv
import json
import re
from pathlib import Path
from typing import Any

import jinja2 as jj
from bs4.element import Tag

from .markdown_processing import process_markdown_text
from ..our_logging import get_logger
from ..util import parse_soup_from_xml, retrieve_contents

logger = get_logger()

def _tokenize(text: str, break_tags):
    soup = parse_soup_from_xml(text)
    current_section = ''

    for tag in soup.find_all():
        if tag.name in break_tags and current_section:
            yield current_section
            current_section = ''
        current_section += str(tag)

    if current_section:
        yield current_section


def _extract_headers(table: Tag) -> list[str]:
    return [th.text.strip() for th in table.find_all('th')]


def _extract_row_data(headers: list[str], row: Tag) -> dict:
    cells = row.find_all(['td', 'th'])
    if len(cells) != len(headers):
        logger.debug(f'Row data does not match headers: {row} ')
        return {}
    return {headers[i]: retrieve_contents(cells[i]) for i in range(len(headers))}


def _process_table(tag: Tag) -> list[dict]:
    headers = _extract_headers(tag)
    rows = (_extract_row_data(headers, tr) for tr in tag.find_all('tr')[1:])
    return [row for row in rows if row]


def _process_h1_table(tag: Tag) -> dict:
    headers = _extract_headers(tag)

    if headers == ['Key', 'Value']:
        rows = (_extract_row_data(headers, tr) for tr in tag.find_all('tr')[1:])
        return {
            row['Key']: row['Value']
            for row in rows
            if row
        }

    else:
        return _extract_row_data(headers, tag.find_all('tr')[1])


def _parse_h1_header_data(text: str):
    section_data = {}

    tokens = _tokenize(text, ['h1', 'h3', 'table'])
    for token in tokens:
        soup = parse_soup_from_xml(token)
        first_tag = soup.find()
        if first_tag.name == 'h1':
            section_data['Title'] = first_tag.text.strip()

        elif first_tag.name == 'h3':
            section_data[first_tag.text.strip()] = ''.join(str(tag) for tag in first_tag.next_siblings)

        elif first_tag.name == 'table':
            section_data |= _process_h1_table(first_tag)

    return section_data


def _parse_h2_section(text: str) -> tuple[str, list[dict]]:
    soup = parse_soup_from_xml(text)

    title_tag = soup.find('h2')
    section_name = title_tag.text.strip()

    table_tag = soup.find('table')
    section_data = _process_table(table_tag) if table_tag else []

    return section_name, section_data


def _parse_h1_section(h1_section: str) -> dict[str, Any]:
    tokens = list(_tokenize(h1_section, ['h1', 'h2']))

    h1_section_data: dict[str, Any] = _parse_h1_header_data(tokens[0])

    for token in tokens[1:]:
        section_name, h2_section_data = _parse_h2_section(token)
        h1_section_data[section_name] = h2_section_data

    return h1_section_data


def _read_multiple_tables(text: str):
    rows = []
    for h1_section in _tokenize(text, ['h1']):
        rows.append(_parse_h1_section(h1_section))
    return rows


def _read_single_table(html: str) -> list[dict]:
    soup = parse_soup_from_xml(html)
    table = soup.find('table')
    if table is None:
        return []
    return _process_table(table)


def _read_md_table(md_text: str) -> list[dict]:
    html = process_markdown_text(md_text)

    # Check if file contains header 1 or 2 tags, indicating multiple tables
    if re.search(r'<h[1|2]>', html):
        return _read_multiple_tables(html)
    else:
        return _read_single_table(html)


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
        return _read_md_table(content)

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
        arg_sets = [{**args, **kwargs} for args in arg_sets]
    else:
        arg_sets = [kwargs]

    return _process_template(template, arg_sets)
