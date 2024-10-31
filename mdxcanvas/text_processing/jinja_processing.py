import re
import csv
import json
import jinja2 as jj
from pathlib import Path

from bs4 import BeautifulSoup
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


def _process_subsection(tag: Tag) -> dict:
    section_data = {tag.text.strip(): []}
    table = tag.find_next('table')
    if table:
        section_data[tag.text.strip()] = _process_table(table)
    return section_data


def get_section(tag: str, soup: BeautifulSoup) -> list[BeautifulSoup]:
    tags = soup.find_all(tag)
    sections = []

    for i in range(len(tags) - 1):
        section = ""
        for sibling in tags[i].next_siblings:
            if sibling == tags[i + 1]:
                break
            section += str(sibling)
        sections.append(parse_soup_from_xml(str(tags[i]) + section))

    last_section = str(tags[-1])
    for sibling in tags[-1].next_siblings:
        last_section += str(sibling)
    sections.append(parse_soup_from_xml(last_section))

    return sections

def _process_section(section: BeautifulSoup) -> dict:
    # Get title
    tag = section.find('h1')
    row_data = {'Title': tag.text.strip()}

    # Process table if it exists
    tag = tag.find_next(['table', 'h2'])
    if tag.name == 'table':
        row_data.update(_process_table(tag)[0])

    # Process subsections
    subsections = get_section("h2", section)
    for subsection in subsections:
        tag = subsection.find('h2')
        row_data.update(_process_subsection(tag))

    return row_data

def _read_multiple_tables(html: str) -> list[dict]:
    soup = parse_soup_from_xml(html)
    sections = get_section("h1", soup)
    return [_process_section(section) for section in sections]


def _read_single_table(html: str) -> list[dict]:
    soup = parse_soup_from_xml(html)
    table = soup.find('table')
    return _process_table(table)


def _read_md_table(md_text: str) -> list[dict]:
    html = process_markdown_text(md_text)

    # Check if file contains any header tags, indicating multiple tables
    if re.search(r'<h[1-6]>', html):
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
