import re
import csv
import json
import jinja2 as jj
from pathlib import Path

from bs4.element import Tag

from .markdown_processing import process_markdown_text
from ..util import parse_soup_from_xml, retrieve_contents


def _extract_headers(table: Tag) -> list[str]:
    return [th.text.strip() for th in table.find_all('th')]


def _extract_row_data(headers: list[str], row: Tag) -> dict:
    cells = row.find_all(['td', 'th'])
    if len(cells) != len(headers):
        return {}
    return {headers[i]: retrieve_contents(cells[i]) for i in range(len(headers))}


def _process_table(tag: Tag) -> list[dict]:
    headers = _extract_headers(tag)
    return [_extract_row_data(headers, tr) for tr in tag.find_all('tr')[1:] if _extract_row_data(headers, tr)]


def _h1_section(tag: Tag) -> dict | None:
    if not tag:
        return None
    section_data = {'Title': tag.text.strip()}

    child = tag.find_next(['h2', 'table'])
    if child.name == 'table':
        # Only one row of data is ever expected for h1 sections
        section_data |= _process_table(child)[0]

    return section_data


def _h2_section(tag: Tag) -> dict | None:
    if not tag:
        return None
    section_data = {tag.text.strip(): []}

    child = tag.find_next(['h2', 'table'])
    if child.name == 'table':
        section_data[tag.text.strip()] = _process_table(child)

    return section_data


def get_sections(text: str, tag_name) -> str:
    section = ''
    soup = parse_soup_from_xml(text)

    tag = soup.find([tag_name])
    while tag:
        if tag.name == tag_name:
            if section:
                yield section
            section = ''

        section += str(tag)
        tag = tag.find_next(['h1', 'h2', 'table'])

    if section:
        yield section


def _read_multiple_tables(html: str) -> list[dict]:
    rows = []

    for h1_section in get_sections(html, 'h1'):
        h1_soup = parse_soup_from_xml(h1_section)
        tag = h1_soup.find('h1')
        row_data = _h1_section(tag)

        for h2_section in get_sections(h1_section, 'h2'):
            h2_soup = parse_soup_from_xml(h2_section)
            tag = h2_soup.find('h2')
            row_data |= _h2_section(tag)

        rows.append(row_data)

    return rows


def _read_single_table(html: str) -> list[dict]:
    soup = parse_soup_from_xml(html)
    table = soup.find('table')
    return _process_table(table)


def _read_md_table(md_text: str) -> list[dict]:
    html = process_markdown_text(md_text)

    # Check if file contains header 1 or 2 tags, indicating multiple tables
    if re.search(r'<h[1|2]>', html):
        return _read_multiple_tables(html)
    else:
        return _read_single_table(html)


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


def _process_template(template: str, arg_sets: list[dict]):
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
    else:
        arg_sets = [kwargs]

    return _process_template(template, arg_sets)
