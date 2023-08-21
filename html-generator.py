"""
    Developed by Osanda Deshan & Preston Raab
"""
import sys
import os

import markdown
from markdown import preprocessors
from jinja2 import Environment, PackageLoader, select_autoescape

# Render the result including jQuery, Bootstrap.
WRAPPER_RENDER = True
LOOKUP_FOLDER = './markdown-quiz-files'
OUTPUT_FOLDER = 'generated-quizzes'


# def get_fancy_html(self, markdown_or_file: str):
#     if markdown_or_file.endswith('.md'):
#         text = readfile(self.files_folder / markdown_or_file)
#
#         html = md.markdown(text, extensions=['fenced_code'])
#         soup = BeautifulSoup(html, "html.parser")
#         for img in soup.find_all('img'):
#             basic_image_html = self.get_img_html(img["src"], img["alt"])
#             img.replace_with(BeautifulSoup(basic_image_html, "html.parser"))
#         html = str(soup)
#
#         return html
#     else:
#         return md.markdown(markdown_or_file, extensions=['fenced_code'])

def render_test(file_name: str, markdown_content: str) -> None:
    """Render quiz in Markdown format to HTML."""

    extensions = ['tables', "app.extensions.tags", "app.extensions.checkbox", "app.extensions.radio", "app.extensions.textbox", 'fenced_code']

    html = markdown.markdown(markdown_content, extensions=extensions, output_format="html5")
    env = Environment(loader=PackageLoader('app', 'static'), autoescape=select_autoescape(['html', 'xml']))

    javascript = env.get_template('app.js').render()

    test_html = env.get_template('base.html').render(content=html, javascript=javascript)
    if WRAPPER_RENDER:
        test_html = env.get_template('wrapper.html').render(content=test_html)

    with open(os.path.join(OUTPUT_FOLDER, f"{file_name[:-2]}html"), "w+") as f:  # create final file
        f.write(test_html)


if __name__ == "__main__":
    # Convert all the .md (markdown) files inside the [markdown-quiz-files] folder
    print("-" * 50 + "\nMarkdown Quiz Generator v0.1\n" + "-" * 50)

    WRAPPER_RENDER = 'embed' not in sys.argv

    for file_name in os.listdir(LOOKUP_FOLDER):
        if file_name.endswith('.md'):
            with open(os.path.join(LOOKUP_FOLDER, file_name), "r") as f:
                print(f"Converting to Markdown ({file_name}) ...")
                render_test(file_name, f.read())

    sys.exit(0)
