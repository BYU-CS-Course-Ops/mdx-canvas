import textwrap

from bs4 import NavigableString
import markdown as md
from markdown.extensions.codehilite import makeExtension as makeCodehiliteExtension

from .inline_math import InlineMathExtension
from ..util import parse_soup_from_xml


def process_markdown_text(text: str) -> str:
    dedented = textwrap.dedent(text)

    html = md.markdown(dedented, extensions=[
        'fenced_code',
        'tables',
        'attr_list',

        # This embeds the highlight style directly into the HTML
        # instead of using CSS classes
        makeCodehiliteExtension(noclasses=True),

        # This preserves \(...\) inline math expressions
        #  so Canvas will render them with MathJax
        InlineMathExtension(),

        # This forces the color of inline code to be black
        # as a workaround for Canvas's super-ugly default red :P
        # BlackInlineCodeExtension(),
        # TODO - Solve this with baked-in CSS

        # TODO - add support for tilde => <del> (strikethrough) (look for extension)
        #  or maybe look for a github-flavored-markdown extension
    ])
    return html


def _process_markdown(parent, excluded: list[str]):
    children = list(parent.children)
    for tag in children:
        if tag.name in excluded:
            continue

        if isinstance(tag, NavigableString):
            tag.replace_with(parse_soup_from_xml(process_markdown_text(tag.text)))
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
    soup = parse_soup_from_xml(text)
    _process_markdown(soup, excluded)
    return str(soup)
