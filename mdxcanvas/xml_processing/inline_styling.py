import cssutils
from bs4 import BeautifulSoup
from ..util import parse_soup_from_xml


def get_style(soup):
    style = ''

    for tag in soup.find_all("style"):
        content = tag.text.strip()
        if content not in style:
            style += content + ' '
        tag.decompose()

    return style, soup


def parse_css(css):
    css_parser = cssutils.CSSParser()
    stylesheet = css_parser.parseString(css)
    styles = {}
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE:
            selector = rule.selectorText
            properties = {prop.name: prop.value for prop in rule.style}
            styles[selector] = properties
    return styles


def apply_inline_styles(html, styles):
    soup = parse_soup_from_xml(html)
    for selector, properties in styles.items():
        for tag in soup.select(selector):
            style_string = "; ".join([f"{prop}: {value}" for prop, value in properties.items()])
            existing_style = tag.get('style', '')
            tag['style'] = style_string + ((existing_style and '; ') or '') + existing_style
    return str(soup)


def bake_css(soup: BeautifulSoup, global_css: str):
    css, soup = get_style(soup)
    css = parse_css(global_css + css)
    soup = apply_inline_styles(str(soup), css)
    return soup


if __name__ == '__main__':
    # Example usage
    html_content = '''<p>Go team</p>'''
    css_content = '''p { font-size: 200px; }'''

    # Parse the CSS and HTML
    parsed_styles = parse_css(css_content)
    styled_html = apply_inline_styles(html_content, parsed_styles)
    print(styled_html)
