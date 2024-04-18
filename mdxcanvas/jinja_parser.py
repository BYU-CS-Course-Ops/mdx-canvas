import re
import csv
import json
import jinja2 as jj
from pathlib import Path
from itertools import takewhile


def _process_single__template(template, global_args, arg_sets, **kwargs):
    jj_template = jj.Environment().from_string(template)
    global_args |= dict(zip=zip, split_list=lambda x: x.split(';'))

    content = []

    for arg_set in arg_sets:
        content.append(
            jj_template.render(
                **global_args,
                **arg_set,
                **kwargs
            ))

    return '\n'.join(content)


def process_jinja(template_file: Path, **kwargs) -> str:
    """
    Takes a jinja template file and renders it with the given arguments.
    The template file contains comments which store the global and local arguments.

    :param template_file: The path to the jinja template file
    :return: The rendered jinja template as a string

    Example:
    ----------
    # >>> process_jinja(Path("template.jinja"))
    "<assignment
        title="Day 1"
        description="This is the first day of the course"
        due_date="2021-01-01"
        points_possible="10"
    </assignment>
    <quiz
        title="Quiz 1"
        description="This is the first quiz of the course"
        due_date="2021-01-01"
        points_possible="10">
    </quiz>"
    """
    template = template_file.read_text()

    args_template = jj.Environment().from_string('\n'.join(takewhile(lambda x: re.match(r' *{% *set', x), template.splitlines())))
    template_args = args_template.module.__dict__

    if 'global' in template_args:
        global_args_file = (template_file.parent / template_args.get('global')).resolve()
        global_args = json.loads(global_args_file.read_text())
    else:
        global_args = {}

    if 'args' in template_args:
        args_file = (template_file.parent / template_args.get('args')).resolve()
        arg_sets = list(csv.DictReader(args_file.read_text().splitlines()))
    else:
        arg_sets = [{}]

    if 'templates' in template_args:
        contents = []
        template_folder = template_file.parent.resolve()
        for arg_set in arg_sets:
            template_file = template_folder / arg_set['Filename']
            content = process_jinja(template_file, **arg_set)
            contents.append(content)
        return '\n'.join(contents)

    else:
        return _process_single__template(template, global_args, arg_sets, **kwargs)


if __name__ == '__main__':
    # print(process_jinja(Path("../demo_course/public-files/template-material/reading-quiz-templates/ReadingQuiz.canvas.jinja")))
    print(process_jinja(Path("../demo_course/public-files/template-material/HwTemplate.canvas.xml.jinja")))