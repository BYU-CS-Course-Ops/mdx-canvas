import re
import textwrap
from xml.etree.ElementTree import Element

import markdown as md
from bs4 import NavigableString, Tag, Comment
from markdown import Extension
from markdown.extensions.codehilite import makeExtension as makeCodehiliteExtension
from markdown.inlinepatterns import BACKTICK_RE, BacktickInlineProcessor

from .inline_math import InlineMathExtension
from ..util import parse_soup_from_xml


class BlackInlineCodeProcessor(BacktickInlineProcessor):
    def handleMatch(self, m: re.Match[str], data: str) -> tuple[Element | str, int, int]:
        el, start, end = super().handleMatch(m, data)
        el.attrib['style'] = 'color: #000000'
        return el, start, end


class BlackInlineCodeExtension(Extension):
    def extendMarkdown(self, md):
        # We use 'backtick' and 190 which are the same values
        # used in markdown.inlinepatterns.py to register the original
        # BacktickInlineCodeProcessor.
        # By reusing the same name, it overrides the original processor with ours
        md.inlinePatterns.register(BlackInlineCodeProcessor(BACKTICK_RE), 'backtick', 190)


def replace_characters(text: str, replacements: dict[str, str]) -> str:
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def replace_problematic_characters(text: str, replacements: dict[str, str]) -> str:
    output_lines = []
    lines = iter(text.splitlines())

    for line in lines:
        if line.strip().startswith('```'):
            output_lines.append(line)
            for code_line in lines:
                output_lines.append(replace_characters(code_line, replacements))
                if code_line.strip().startswith('```'):
                    break
        else:
            output_lines.append(line)

    return '\n'.join(output_lines)


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
        BlackInlineCodeExtension(),
        # TODO - can we solve this with baked-in CSS?

        # TODO - add support for tilde => <del> (strikethrough) (look for extension)
        #  or maybe look for a github-flavored-markdown extension
    ])

    return html


def _form_blocks(tag: Tag, excluded: list[str], inline: list[str]) -> tuple[bool, list[Tag]]:
    block_tags = []

    for child in list(tag.children):  # Make a copy because .children will change after the yield
        if isinstance(child, Comment) or child.name in excluded:
            if block_tags:
                yield True, block_tags
            block_tags = []

        elif isinstance(child, NavigableString) or child.name in inline:
            block_tags.append(child)

        else:
            # Some other kind of tag -> breaks up a block
            if block_tags:
                yield True, block_tags
            yield False, [child]
            block_tags = []

    if block_tags:
        yield True, block_tags


def _process_markdown(parent, excluded: list[str], inline: list[str]):
    for needs_markdown, block in _form_blocks(parent, excluded, inline):
        if needs_markdown:
            result = parse_soup_from_xml(
                process_markdown_text(
                    ''.join((str(b) for b in block))
                )
            )
            for tag in block:
                tag.replace_with(result)
        else:
            for tag in block:
                _process_markdown(tag, excluded, inline)


def process_markdown(text: str, excluded: list[str], inline: list[str]) -> str:
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
    content = replace_problematic_characters(text, {'<': '&lt;'})
    soup = parse_soup_from_xml(content)
    _process_markdown(soup, excluded, inline)
    return str(soup)
