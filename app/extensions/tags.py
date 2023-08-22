import re

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor
from markdown.postprocessors import Postprocessor

from bs4 import BeautifulSoup, NavigableString


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
        preprocessor = TagsPreprocessor(md)
        md.preprocessors.add("tags", preprocessor, '>normalize_whitespace')


class TagsPreprocessor(Preprocessor):
    """
    Works html tags into check and radio boxes
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self, lines):
        stash = self.md.htmlStash

        soup = BeautifulSoup("\n".join(lines), "html.parser")
        questions = soup.find_all('question')
        index = 1

        for question in questions:
            question.contents[0].replace_with(f"{index}. {question.contents[0][1:]}")
            print(question.string)
            rights = question.css.filter('right')

            one_correct = len(rights) == 1
            for right in rights:
                without_newlines = right.string.replace('\n', ' ')
                parens = "(x)" if one_correct else "[x]"
                right.replace_with(f"    - {parens} {without_newlines}")
            for wrong in question.css.filter('wrong'):
                without_newlines = wrong.string.replace('\n', ' ')
                parens = "( )" if one_correct else "[ ]"
                wrong.replace_with(f"    - {parens} {without_newlines}")

            question.replace_with("".join(question.contents))
            index += 1

        result = str(soup)
        print(result)
        return result.split("\n")
