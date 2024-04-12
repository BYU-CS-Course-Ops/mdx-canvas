import os
import csv
from jinja2 import Environment, FileSystemLoader, Template


def split_list(input_string):
    return input_string.split(';')


class JinjaParser:

    def parse(self, template_path: str) -> str:
        """
        Parses the content of the template using the Jinja2 templating engine

        Args:
            template_path (str): The path to the template file

        Returns:
            str: The rendered content of the assignments
        """
        # Get the directory path and filename of the template
        self.dir_path = os.path.dirname(template_path)
        self.filename = os.path.basename(template_path)

        # Creates a jinja environment and updates the appropriate variables
        self.env = Environment(loader=FileSystemLoader(self.dir_path))
        self.env.globals.update(split_list=split_list)
        self.env.globals.update(zip=zip)

        # Load the template
        self.template = self.env.get_template(self.filename)

        # Get the template information and content
        self.get_template_info()
        self.content = self.get_content()

        # Render the content
        return self.render()

    def get_template_info(self):
        """
        Extracts information from the template module and sets instance variables accordingly.

        This method populates the following instance variables:

        - self.type: The type of the template.
        - self.csv_file: The path to the CSV file associated with the template content.
        - self.global_file: The path to the global file associated with the template.
        - self.alternate: An optional alternate template.

        Raises:
            KeyError: If the template is missing the type, content, or global_content variable
        """
        template_vars = self.template.module.__dict__
        try:
            self.type = template_vars['type']
            self.csv_file = f"{self.dir_path}/{template_vars['content']}"
            self.global_file = f"{self.dir_path}/{template_vars['global_content']}"
            self.alternate = template_vars.get('alternate_temp')
        except KeyError:
            raise KeyError('The template is missing the type, content, or global_content variable')

    def get_content(self) -> list[dict[str, str]]:
        """
        Creates a list of dictionary where each dictionary is a
        new assignment.

        Returns:
            list[dict[str, str]]: A list of dictionaries where each dictionary
            is a new assignment of the global args and the assignments args

        Example:
        --------
        >>> self.get_content()
        [
            {
                'title': 'example 1',
                'due_at': 'Jan 3',
                ...,
                'late_date': 'Jan 13'
            },
            {
                'title': 'example 2',
                'due_at': 'Jan 5',
                ...,
                'late_date': 'Jan 15'},
            ...
            {
                'title': 'example 3',
                'due_at': 'Jan 7',
                ...,
                'late_date': 'Jan 17'
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

    def _get_template(self, assignment: dict[str, str]) -> Template:
        """
        Gets the appropriate template for the current assignment

        Args:
            assignment (dict[str, str]): The current assignment

        Returns:
            Template: The appropriate template for the current assignment
        """
        if self.type == 'hw' and assignment.get("Id") == "0":  # HW 0 is a special case
            template = self.env.get_template(self.alternate)
        else:
            template = self.template
        return template

    def render(self) -> str:
        """
        Renders the content of the assignments using the template

        Returns:
            str: The rendered content of the assignments

        Example:
        --------
        >>> self.render()
        "<quiz
            title="example 1 - example assignment 1"
            due_at="Jan 3, 2024, 11:59 PM"
            available_from="Jan 5, 2024, 12:00 AM"
            ...>
        <assignment
            title="example 2 - example assignment 2"
            due_at="Jan 5, 2024, 11:59 PM"
            available_from="Jan 15, 2024, 12:00 AM"
            ...>"
        """
        rendered_assignments = []
        for assignment in self.content:
            template = self._get_template(assignment)
            content = template.render(assignment, var=assignment)  # var is only needed for the DayTemplate
            rendered_assignments.append(content)
        return ''.join(rendered_assignments)
