import textwrap

from bs4 import BeautifulSoup, NavigableString
import markdown as md
from markdown.extensions.codehilite import makeExtension as makeCodehiliteExtension


def _process_markdown_text(text: str):
    dedented = textwrap.dedent(text)

    html = md.markdown(dedented, extensions=[
        'fenced_code',
        'tables',
        'attr_list',

        # This embeds the highlight style directly into the HTML
        # instead of using CSS classes
        makeCodehiliteExtension(noclasses=True),

        # This forces the color of inline code to be black
        # as a workaround for Canvas's super-ugly default red :P
        # BlackInlineCodeExtension(),
        # TODO - Solve this with baked-in CSS

        # BakedCSSExtension(global_css)
        # TODO - make this a Tag processor also
    ])

    return BeautifulSoup(html, 'html.parser')


def _process_markdown(parent, excluded: list[str]):
    children = list(parent.children)
    for tag in children:
        if tag.name in excluded:
            continue

        if isinstance(tag, NavigableString):
            tag.replace_with(_process_markdown_text(tag.text))
        else:
            _process_markdown(tag, excluded)


def process_markdown(text: str, excluded: list[str]) -> str:
    """
    Process Markdown text and return XML text

    This purpose of this function is only the Markdown to XML step
    Custom XML/HTML tags should be handled by the XML processor
    This function simply converts all Markdown formatting to HTML

    This function processes Markdown in ALL XML/HTML tags
    (including nested tags) except those listed in `excluded`.

    :param text: the Markdown text to process
    :param excluded: a list of tag names to exclude; their contents are left untouched
    :returns: The XML/HTML text
    """
    soup = BeautifulSoup(text, 'html.parser')
    _process_markdown(soup, excluded)
    return str(soup)
