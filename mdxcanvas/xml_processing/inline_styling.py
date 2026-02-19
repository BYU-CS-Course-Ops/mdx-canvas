import cssutils
from bs4 import BeautifulSoup
from ..util import parse_soup_from_xml


def get_style(soup: BeautifulSoup) -> str:
    style = ''

    for tag in soup.find_all("style"):
        content = tag.text.strip()
        if content not in style:
            style += content + ' '
        tag.decompose()

    return style


def parse_css(css: str) -> dict[str, dict[str, str]]:
    css_parser = cssutils.CSSParser(validate=False)
    stylesheet = css_parser.parseString(css)
    styles = {}
    for rule in stylesheet:
        if rule.type == rule.STYLE_RULE:
            selector = rule.selectorText
            properties = {prop.name: prop.value for prop in rule.style}
            styles[selector] = properties
    return styles


def apply_inline_styles(soup: BeautifulSoup, styles: dict[str, dict[str, str]]) -> None:
    for selector, properties in styles.items():
        for tag in soup.select(selector):
            # Parse existing styles into a dictionary
            existing_style = tag.get('style', '')
            existing_props = {}
            if existing_style and (existing_style := str(existing_style)):
                for prop in existing_style.split(';'):
                    prop = prop.strip()
                    if ':' in prop:
                        key, value = prop.split(':', 1)
                        existing_props[key.strip()] = value.strip()

            # Merge properties: new CSS properties override existing inline styles
            merged_props = { **properties, **existing_props }

            # Reconstruct style string
            style_string = ";".join([f"{prop}:{value}" for prop, value in merged_props.items()])
            tag['style'] = style_string


def bake_css(soup: BeautifulSoup, global_css: str) -> None:
    css = get_style(soup)
    css = parse_css(global_css + css)
    apply_inline_styles(soup, css)


if __name__ == '__main__':
    # Example usage
    html_content = '''<p>Go team</p>'''
    css_content = '''p { font-size: 200px; }'''

    # Parse the CSS and HTML
    parsed_styles = parse_css(css_content)
    soup = parse_soup_from_xml(html_content)
    apply_inline_styles(soup, parsed_styles)
    print(soup)
