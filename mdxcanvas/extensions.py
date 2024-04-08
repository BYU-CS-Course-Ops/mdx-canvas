import re
import xml.etree.ElementTree as etree

from markdown.inlinepatterns import BacktickInlineProcessor, BACKTICK_RE
from markdown.extensions import Extension

from markdown.preprocessors import HtmlBlockPreprocessor
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString


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


class CustomXMLTagProcessor(HtmlBlockPreprocessor):
    def __init__(self, md):
        super().__init__(md)
        self.custom_tag_processors = {}
    
    
    def run(self, lines: list[str]) -> list[str]:
        soup = BeautifulSoup("\n".join(lines), "html.parser")
        document = []
        return super().run(lines)
    
    def add_custom_tag_processor(self, name, processor):
        self.custom_tag_processors[name] = processor
        


class CustomTagExtension(Extension):
    # We use 'html_block' and 20 which are the same values
    # used in markdown.preprocessors.py to register the original
    # HTMLBlockPreprocessor.
    # By reusing the same name, it overrides the original processor with ours
    def extendMarkdown(self, md):
        name = 'html_block'
        if name in self:
            processor = self[name]
            processor.add_custom_tag_processor('custom', lambda tag: tag)
        else:
            md.preprocessors.register(CustomXMLTagProcessor(md), 'html_block', 20)
