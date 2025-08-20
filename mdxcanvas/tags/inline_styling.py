from pathlib import Path

import cssutils
from bs4 import BeautifulSoup

from .core import TagProcessor
from ..util import parse_soup_from_xml


def _get_style(soup):
    style = ''

    for tag in soup.find_all("style"):
        content = tag.text.strip()
        if content not in style:
            style += content + ' '
        tag.decompose()

    return style, soup


def _parse_css(css):
    css_parser = cssutils.CSSParser()
    stylesheet = css_parser.parseString(css)
    styles = {}
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE:
            selector = rule.selectorText
            properties = {prop.name: prop.value for prop in rule.style}
            styles[selector] = properties
    return styles


def _apply_inline_styles(html: str, styles):
    soup = parse_soup_from_xml(html)
    for selector, properties in styles.items():
        for tag in soup.select(selector):
            style_string = "; ".join([f"{prop}: {value}" for prop, value in properties.items()])
            existing_style = tag.get('style', '')
            tag['style'] = style_string + ((existing_style and '; ') or '') + existing_style
    return soup


class BakeCSSTagProcessor(TagProcessor):
    def __init__(self, global_css: str):
        super().__init__(19.9999)
        self.global_css = global_css

    def handles_soup(self, soup: BeautifulSoup) -> bool:
        return True

    def process_soup(self, soup: BeautifulSoup, parent: Path) -> BeautifulSoup:
        css, soup = _get_style(soup)
        css = _parse_css(self.global_css + css)
        soup = _apply_inline_styles(str(soup), css)
        return soup


if __name__ == '__main__':
    # Example usage
    html_content = '''<p>Go team</p>'''
    css_content = '''p { font-size: 200px; }'''

    # Parse the CSS and HTML
    parsed_styles = _parse_css(css_content)
    styled_html = _apply_inline_styles(html_content, parsed_styles)
    print(styled_html)
