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


class ZipTagProcessor(HtmlBlockPreprocessor):
    def run(self, lines: list[str]) -> list[str]:
        soup = BeautifulSoup("\n".join(lines), "html.parser")
        document = []
        for tag in soup.find_all("zip"):
            # Create a new div element
            div = Tag(name="div")
            div["class"] = "zip"
            # Add the contents of the zip tag to the div
            for child in tag.children:
                if isinstance(child, NavigableString):
                    div.append(child)
                else:
                    div.append(child.prettify())
            # Replace the zip tag with the div
            tag.replace_with(div)
        return str(soup).split("\n")


class CustomXMLTagProcessor(HtmlBlockPreprocessor):
    custom_tag_processors = {
        "zip": ZipTagProcessor
    }
    
    def __init__(self, md):
        super().__init__(md)
    
    def run(self, lines: list[str]) -> list[str]:
        soup = BeautifulSoup("\n".join(lines), "html.parser")
        document = []
        return super().run(lines)


class CustomTagExtension(Extension):
    # We use 'html_block' and 20 which are the same values
    # used in markdown.preprocessors.py to register the original
    # HTMLBlockPreprocessor.
    # By reusing the same name, it overrides the original processor with ours
    def __init__(self, *args, **kwargs):
        super().__init__()
    
    def extendMarkdown(self, md):
        md.preprocessors.register(CustomXMLTagProcessor(md), 'html_block', 20)
