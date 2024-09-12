import re

from markdown import Markdown, Extension
from markdown.preprocessors import Preprocessor


class InlineMathPreprocessor(Preprocessor):
    """
    Canvas supports \(...\) inline math (MathJax)
    But the \(...\) get mangled into (...) somewhere along the way.
    This extension stashes \(...\) so it is preserved
    """

    def run(self, lines):
        new_lines = []

        # inline_dollar_math_pattern = re.compile(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)')
        # See https://docs.mathjax.org/en/latest/basic/mathematics.html
        #  for the rationale for why the $...$ syntax is not usually supported

        mathjax_inline_pattern = re.compile(r'\\\((.+?)\\\)')

        for line in lines:
            m = mathjax_inline_pattern.search(line)
            while m:
                line = line.replace(m.group(0), self.md.htmlStash.store(m.group(0)))
                m = mathjax_inline_pattern.search(line)
            new_lines.append(line)

        return new_lines


# Define the extension that uses the preprocessor
class InlineMathExtension(Extension):
    def extendMarkdown(self, md: Markdown):
        md.preprocessors.register(InlineMathPreprocessor(md), 'inlinemath', 27)
