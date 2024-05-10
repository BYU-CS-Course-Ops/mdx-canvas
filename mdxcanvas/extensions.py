import re
import xml.etree.ElementTree as etree

from markdown.inlinepatterns import BacktickInlineProcessor, BACKTICK_RE
from markdown.extensions import Extension

from markdown.preprocessors import HtmlBlockPreprocessor
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, PageElement

from typing import Protocol


class BlackInlineCodeProcessor(BacktickInlineProcessor):
    def handleMatch(self, m: re.Match[str], data: str) -> tuple[etree.Element | str, int, int]:
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


# Make a Protocol for any tag processor, it should take a Tag and return a Tag
# This way we can define a type hint for the tag_processors dictionary
class TagProcessor(Protocol):
    def __call__(self, tag: Tag) -> Tag:
        ...
    

class CustomHTMLBlockTagProcessor(HtmlBlockPreprocessor):
    tag_processors: dict[str, TagProcessor]
    
    def __init__(self, md, tag_processors: dict[str, TagProcessor]):
        super().__init__(md)
        self.custom_tag_processors = tag_processors
    
    def run(self, lines: list[str]) -> list[str]:
        soup = BeautifulSoup("\n".join(lines), "html.parser")
        for tag in soup.find_all():
            if tag.name in self.custom_tag_processors:
                processor = self.custom_tag_processors[tag.name]
                tag.replace_with(processor(tag))
        return str(soup).split("\n")


class CustomTagExtension(Extension):
    def __init__(self, tag_processors: dict[str, TagProcessor]):
        super().__init__()
        self.tag_processors = tag_processors
    
    def extendMarkdown(self, md):
        # When registering the CustomHTMLBlockTagProcessor, we use a priority of 19
        # which is one less than the original priority for 'html_block'
        md.preprocessors.register(CustomHTMLBlockTagProcessor(md, self.tag_processors), 'custom_tag', 19)
