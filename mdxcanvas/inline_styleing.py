import cssutils
from bs4 import BeautifulSoup


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
    soup = BeautifulSoup(html, 'html.parser')
    for selector, properties in styles.items():
        for tag in soup.select(selector):
            style_string = "; ".join([f"{prop}: {value}" for prop, value in properties.items()])
            existing_style = tag.get('style', '')
            tag['style'] = existing_style + (existing_style and '; ' or '') + style_string
    return soup.prettify()


if __name__ == '__main__':
    # Example usage
    html_content = '''<p>Go team</p>'''
    css_content = '''p { font-size: 200px; }'''

    # Parse the CSS and HTML
    parsed_styles = parse_css(css_content)
    styled_html = apply_inline_styles(html_content, parsed_styles)
    print(styled_html)
