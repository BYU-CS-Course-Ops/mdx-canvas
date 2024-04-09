import csv
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, Template

TEMPLATE_PATH = Path('../demo_course/public-files/canvas-templates/')
GLOBAL_PATH = '../demo_course/public-files/template-args/global_template_args.csv'


def get_content(csv_file: csv) -> list[dict[str, str]]:
    """
    Reads a csv file where each row represents a new assignment
    and returns a list of dictionaries where each dictionary
    represents an assignment with its variables.

    header1,header2,header3,...,headerN
    first,value2,value3,...,valueN
    second,value2,value3,...,valueN
    ...
    last,value2,value3,...,valueN

    [
        {
            'header1': 'first',
            'header2': 'value2',
            ...,
            'headerN': 'valueN'
        },
        {
            'header1': 'second',
            'header3': 'value3',
            ...,
            'headerN': 'valueN'},
        ...
        {
            'header1': 'last',
            'header3': 'value3',
            ...,
            'headerN': 'valueN'
        }
    ]
    """
    global_content = {}
    with open(GLOBAL_PATH, 'r') as global_file:
        global_reader = csv.DictReader(global_file)
        for row in global_reader:
            global_content = row

    assignment_content = []
    with open(csv_file, 'r') as assignment_file:
        assignment_reader = csv.DictReader(assignment_file)
        for row in assignment_reader:
            assignment_content.append({**global_content, **row})

    return assignment_content


class JinjaParser:
    def __init__(self, template_path: str):
        self.env = Environment(loader=FileSystemLoader(TEMPLATE_PATH))
        self.template = self.env.get_template(template_path)

        self.get_template_info()

        self.content = get_content(TEMPLATE_PATH / self.csv_file)

        self.assignments = self.render()

    def get_template_info(self):
        """
        Extracts the csv file and type of assignment from the template

        {% set type = "hw" %}
        {% set data = "hw_template_args.csv" %}
        """
        template_vars = self.template.module.__dict__
        try:
            self.type = template_vars['type']
            self.csv_file = template_vars['content']
        except KeyError:
            raise KeyError('The template is missing the type or content variable')

    def _get_filename(self, assignment: dict[str, str]) -> str:
        if 'Id' not in assignment:
            filename = f'{self.type}-{assignment["Title"]}'
        else:
            filename = f'{self.type}-{assignment["Id"]}'
        return filename

    def _get_template(self, assignment: dict[str, str]) -> Template:
        if self.type == 'hw' and assignment.get("Id") == "0":
            template = self.env.get_template('HwZeroTemplate.jinja')
        else:
            template = self.template
        return template

    def render(self) -> dict[str, str]:
        """
        Renders the template with the content of each assignment
        and returns a dictionary with the filename as the key and
        the content as the value.

        {
            'hw-1': 'content1',
            'hw-2': 'content2',
            ...
            'hw-N': 'contentN'
        }
        """
        rendered_assignments = {}
        for assignment in self.content:
            template = self._get_template(assignment)

            filename = self._get_filename(assignment)
            content = template.render(assignment)

            rendered_assignments[filename] = content

        return rendered_assignments


if __name__ == "__main__":
    parser = JinjaParser('HwTemplate.jinja')
    print(parser.assignments)
