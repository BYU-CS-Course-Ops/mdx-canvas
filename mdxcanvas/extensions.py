from markdown.extensions import Extension

from markdown.postprocessors import Postprocessor
from markdown.preprocessors import Preprocessor, HtmlBlockPreprocessor
from bs4 import BeautifulSoup
from bs4.element import Tag

from typing import Protocol

from .xml_processing.inline_styling import get_style, parse_css, apply_inline_styles
from .util import parse_soup_from_xml

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
        joined = "\n".join(lines)
        if "<" not in joined or ">" not in joined:
            return lines
        soup = parse_soup_from_xml(joined)
        for tag in soup.find_all():
            if tag.name in self.custom_tag_processors:
                processor = self.custom_tag_processors[tag.name]
                new_tag = processor(tag)
                tag.replace_with(new_tag)
        return str(soup).split("\n")


class PrintLinesPreprocessor(Preprocessor):
    """
    Used for debugging the state of the document
    in the middle of the preprocessor chain
    """
    def __init__(self, md, label):
        super().__init__(md)
        self.label = label

    def run(self, lines: list[str]) -> list[str]:
        print(f'START LINES {self.label} ----------------------------------------')
        for line in lines:
            print(line, end='' if line.endswith('\n') else '\n')
        print(f'END LINES   {self.label} ----------------------------------------')
        return lines


class CustomTagExtension(Extension):
    def __init__(self, tag_processors: dict[str, TagProcessor]):
        super().__init__()
        self.tag_processors = tag_processors

    def extendMarkdown(self, md):
        # When registering the CustomHTMLBlockTagProcessor, we use a priority of 22
        # which is two more than the original priority for 'html_block'
        # (i.e. will run BEFORE the 'html_block' processor)
        md.preprocessors.register(
            CustomHTMLBlockTagProcessor(md, self.tag_processors),
            'custom_tag', 22
        )


class BakedCSSPostProcessor(Postprocessor):
    def __init__(self, global_css):
        super().__init__()
        self.global_css = global_css

    def run(self, text):
        soup = parse_soup_from_xml(text)
        css, soup = get_style(soup)
        css = parse_css(self.global_css + css)
        soup = apply_inline_styles(str(soup), css)
        return str(soup)


class BakedCSSExtension(Extension):
    def __init__(self, global_css: str = ''):
        super().__init__()
        self.global_css = global_css

    def extendMarkdown(self, md):
        # By default something is at 20 and 30 so we chose 7 so it runs last
        md.postprocessors.register(
            BakedCSSPostProcessor(self.global_css),
            'baked-css', 7
        )