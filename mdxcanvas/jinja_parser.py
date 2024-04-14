import csv
import json

import jinja2 as jj

from pathlib import Path


def _process_jinja(template: jj.Template, global_args, arg_sets) -> str:
    content = []
    for args in arg_sets:
        content.append(template.render(
            **global_args,
            **args
        ))
    return '\n'.join(content)


def process_jinja(template_file: Path) -> str:
    """
    Takes a jinja template file and renders it with the given arguments.
    The template file contains comments which store the global and local arguments.

    :param template_file: The path to the jinja template file
    :return: The rendered jinja template as a string

    Examples:
    ----------
    >>> template_file.read_text()
    {# global.json #}
    {# local.csv #}

    >>> process_jinja(Path("template.jinja")
    "<assignment
        title="Day 1"
        description="This is the first day of the course"
        due_date="2021-01-01"
        points_possible="10"
        submission_types="online_upload">
    </assignment>
    <quiz
        title="Quiz 1"
        description="This is the first quiz of the course"
        due_date="2021-01-01"
        points_possible="10">
    </quiz>"
    """
    template = template_file.read_text()

    global_args = {}
    arg_sets = [{}]

    # Finds the global and template argument paths
    for line in template.splitlines():
        if not line.startswith('{#'):  # i.e. commented line in jinja
            break  # only look at initial commented lines
        line = line.strip("{}# '\"")

        if line.endswith('.json'):
            global_args_file = (template_file.parent / line).resolve()
            global_args = json.loads(global_args_file.read_text())

        elif line.endswith('.csv'):
            args_file = (template_file.parent / line).resolve()
            arg_sets = list(csv.DictReader(args_file.read_text().splitlines()))

    jj_template = jj.Environment().from_string(template)
    global_args |= dict(zip=zip, split_list=lambda x: x.split(';'))
    return _process_jinja(jj_template, global_args, arg_sets)


if __name__ == '__main__':
    print(process_jinja(Path("../demo_course/public-files/template-material/DayTemplate.jinja")))