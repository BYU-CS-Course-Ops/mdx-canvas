import re
import xml.etree.ElementTree as etree

from markdown.inlinepatterns import BacktickInlineProcessor, BACKTICK_RE
from markdown.extensions import Extension


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

