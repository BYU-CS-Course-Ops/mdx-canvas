import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor
from markdown.preprocessors import HtmlBlockPreprocessor

from bs4 import BeautifulSoup

def makeExtension(configs=None):
    if configs is None:
        return TagsExtension()
    else:
        return TagsExtension(configs=configs)


class TagsExtension(Extension):

    def __init__(self, **kwargs):
        self.config = {}
        super().__init__(**kwargs)

    def extendMarkdown(self, md, md_globals):
        list_class = self.getConfig("list_class")
        renderer = self.getConfig("render_item")
        # md.preprocessors.add(
        #     'html_block',
        #     HtmlBlockPreprocessor(md),
        #     '>normalize_whitespace')
        preprocessor = TagsPreprocessor(md)
        md.preprocessors.add("tags", preprocessor, '>normalize_whitespace')


class TagsPreprocessor(Preprocessor):
    """
    Works html tags into check and radio boxes
    """

    list_pattern = re.compile(r"(<ul>\n<li>\([ Xx]\))")
    item_pattern = re.compile(r"^<li>\(([ Xx])\)(.*)</li>$", re.MULTILINE)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, lines):
        stash = self.md.htmlStash

        soup = BeautifulSoup("\n".join(lines), "html.parser")
        questions = soup.find_all('question')
        for question in questions:
            print(question.contents)
            print(question.right)
            question.replace_with()

        html = re.sub(self.list_pattern, self._convert_list, html)
        return re.sub(self.item_pattern, self._convert_item, html)

    def _convert_list(self, match):
        return match.group(1).replace("<ul>", f"<ul class=\"{self.list_class}\">")

    def _convert_item(self, match):
        state, caption = match.groups()
        return self.render_item(caption, state != " ")


def render_item(caption, checked):
    correct = "1" if checked else "0"
    fake = "0" if checked else "1"

    return f"<li>" \
           f"<label><input type=\"radio\" data-question=\"{fake}\" data-content=\"{correct}\" />{caption}</label>" \
           f"</li>"
