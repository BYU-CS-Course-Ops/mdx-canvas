import os
import csv
from jinja2 import Environment, FileSystemLoader, Template


class JinjaParser:
    def __init__(self, template_path: str):
        self.dir_path = os.path.dirname(template_path)
        self.filename = os.path.basename(template_path)

        self.env = Environment(loader=FileSystemLoader(self.dir_path))
        self.template = self.env.get_template(self.filename)

        self.get_template_info()

        self.content = self.get_content()

        self.assignments = self.render()

    def get_template_info(self):
        """
        Extracts the csv file and type of assignment from the template

        {% set type = "type" %}
        {% set content = "type_template_args.csv" %}
        {% set global_content = "global_template_args.csv" %}
        {% set alternate_temp = "alternate_temp.jinja" %}
        """
        template_vars = self.template.module.__dict__
        try:
            self.type = template_vars['type']
            self.csv_file = f"{self.dir_path}/{template_vars['content']}"
            self.global_file = f"{self.dir_path}/{template_vars['global_content']}"
            if self.type == "hw":
                self.alternate = template_vars['alternate_temp']
        except KeyError:
            raise KeyError('The template is missing the type, content, or global_content variable')

    def get_content(self) -> list[dict[str, str]]:
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
        with open(self.global_file, 'r') as global_file:
            global_reader = csv.DictReader(global_file)
            for row in global_reader:
                global_content = row

        assignment_content = []
        with open(self.csv_file, 'r') as assignment_file:
            assignment_reader = csv.DictReader(assignment_file)
            for row in assignment_reader:
                assignment_content.append({**global_content, **row})

        return assignment_content

    def _get_filename(self, assignment: dict[str, str]) -> str:
        if 'Id' not in assignment:
            filename = f'{self.type}-{assignment["Title"]}'
        else:
            filename = f'{self.type}-{assignment["Id"]}'
        return filename

    def _get_template(self, assignment: dict[str, str]) -> Template:
        if self.type == 'hw' and assignment.get("Id") == "0":
            template = self.env.get_template(self.alternate)
        else:
            template = self.template
        return template

    def render(self) -> str:
        """
        Returns the contents of the assignments rendered with the template
        as a giant string

        "<quiz
            title="Homework 0 - Getting Started"
            due_at="{{ Due_At }}, {{ Year }}, 11:59 PM"
            available_from="{{ Start }}, {{ Year }}, 12:00 AM"
            ...
        >
        <assignment
            title="Homework 1a - Getting Started"
            due_at="{{ Due_At }}, {{ Year }}, 11:59 PM"
            available_from="{{ Start }}, {{ Year }}, 12:00 AM"
            ...
        >"
        """
        rendered_assignments = []
        for assignment in self.content:
            template = self._get_template(assignment)

            content = template.render(assignment)

            rendered_assignments.append(content)

        return ''.join(rendered_assignments)


if __name__ == "__main__":
    parser = JinjaParser('../demo_course/public-files/template-material/ProjectTemplate.jinja')
