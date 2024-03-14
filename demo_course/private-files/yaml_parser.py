# parse the yaml file and return the data
import json
from pathlib import Path

from typing import Callable, Union

import pytz
from datetime import datetime
from typing import Protocol, TypeAlias
from collections import defaultdict

from jinja2 import Environment

ResourceExtractor: TypeAlias = Callable[[str], tuple[str, list]]

from strictyaml import load, Map, Str, Int, Seq, Optional, Any, Enum, MapPattern, YAMLError, Bool

from document_schema import document_schema


def make_iso(date: datetime | str | None, time_zone: str) -> str:
    if isinstance(date, datetime):
        return datetime.isoformat(date)
    elif isinstance(date, str):
        # Check if the string is already in ISO format
        try:
            return datetime.isoformat(datetime.fromisoformat(date))
        except ValueError:
            pass
        
        try_formats = [
            "%b %d, %Y, %I:%M %p",
            "%b %d %Y %I:%M %p",
            "%Y-%m-%dT%H:%M:%S%z"
        ]
        for format_str in try_formats:
            try:
                parsed_date = datetime.strptime(date, format_str)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f"Invalid date format: {date}")
        
        # Convert the parsed datetime object to the desired timezone
        to_zone = pytz.timezone(time_zone)
        parsed_date = parsed_date.replace(tzinfo=None)  # Remove existing timezone info
        parsed_date = parsed_date.astimezone(to_zone)
        return datetime.isoformat(parsed_date)
    else:
        raise TypeError("Date must be a datetime object or a string")


def parse_yaml(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        text = file.read()
    
    document = load(text, document_schema).data
    return document

class QuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
        
    def walk(self, question: dict):
        new_question = {}
        for key, value in question.items():
            if key == "text":
                new_question[key], new_question["resources"] = self.markdown_processor(value)
            else:
                new_question[key] = value
        return new_question
        

class QuizWalker:
    def __init__(self, markdown_processor: ResourceExtractor, group_identifier: Callable, date_formatter: Callable,
                 parse_template_data: Callable):
        self.markdown_processor = markdown_processor
        self.group_identifier = group_identifier
        self.date_formatter = date_formatter
        self.parse_template_data = parse_template_data
        self.question_walker = QuestionWalker(markdown_processor)
        
    def walk(self, quiz: dict):
        new_quiz = {}
        for key, value in quiz.items():
            if key in ["due_at", "lock_at", "unlock_at", "show_correct_answers_at", "hide_correct_answers_at"]:
                new_quiz[key] = self.date_formatter(value)
            else:
                new_quiz[key] = value
        
        if new_quiz.get("questions"):
            new_quiz["questions"] = [self.question_walker.walk(question) for question in new_quiz["questions"]]
        
        return new_quiz


class AssignmentWalker:
    def __init__(self, markdown_processor: ResourceExtractor, group_identifier: Callable, date_formatter: Callable,
                 parse_template_data: Callable):
        self.markdown_processor = markdown_processor
        self.group_identifier = group_identifier
        self.date_formatter = date_formatter
        self.parse_template_data = parse_template_data


class PageWalker:
    def __init__(self, markdown_processor: ResourceExtractor, date_formatter: Callable):
        self.markdown_processor = markdown_processor
        self.date_formatter = date_formatter


class ModuleWalker:
    pass


class OverrideWalker:
    def __init__(self, date_formatter: Callable, parse_template_data: Callable):
        self.date_formatter = date_formatter
        self.parse_template_data = parse_template_data


class DocumentWalker:
    def __init__(self, path_to_resources: Path, path_to_canvas_files: Path, markdown_processor: ResourceExtractor,
                 time_zone: str,
                 group_identifier=lambda x: 0):
        self.path_to_resources = path_to_resources
        self.path_to_files = path_to_canvas_files
        self.markdown_processor = markdown_processor
        self.date_formatter = lambda x: make_iso(x, time_zone)
        
        self.jinja_env = Environment()
        # This enables us to use the zip function in template documents
        
        self.jinja_env.globals.update(zip=zip, split_list=lambda sl: [s.strip() for s in sl.split(';')])
        
        self.child_walkers = {
            "quiz": QuizWalker(self.markdown_processor, group_identifier, self.date_formatter,
                               self.parse_template_data),
            "assignment": AssignmentWalker(self.markdown_processor, group_identifier, self.date_formatter,
                                           self.parse_template_data),
            "page": PageWalker(self.markdown_processor, self.date_formatter),
            "module": ModuleWalker(),
            "override": OverrideWalker(self.date_formatter, self.parse_template_data)
        }
    
    def walk(self, document: dict):
        new_documents = []
        if child_walker := self.child_walkers.get(document["type"]):
            templates = child_walker.walk(document)
            if not isinstance(templates, list):
                templates = [templates]
            for template in templates:
                new_documents.extend(self.create_elements_from_template(template))
        return new_documents
    
    def create_elements_from_template(self, element_template):
        if not (all_replacements := element_template.get("replacements", None)):
            return [element_template]
        
        # Element template is an object, turn it into text
        template_text = json.dumps(element_template, indent=4)
        
        # Use the text to create a jinja template
        template = self.jinja_env.from_string(template_text)
        
        elements = []
        for context in all_replacements:
            for key, value in context.items():
                context[key] = value.replace('"', '\\"')
            # For each replacement, create an object from the template
            rendered = template.render(context)
            element = json.loads(rendered)
            elements.append(element)
        
        # Replacements become unnecessary after creating the elements
        for element in elements:
            del element["replacements"]
        return elements
    
    def parse_template_data(self, template):
        """
        Parses a template tag into a list of dictionaries/canvas objects
        
            | Name | Date    |
            |---------|------------|
            | Lab 1   | October       |
            | Lab 2  | November |
        becomes
            [
                {"Name": "Lab 1", "Date": "October"},
                { "Name": "Lab 2", "Date": "November"}
            ]
        """
        if filename := template.get("filename"):
            csv = (self.path_to_files / filename).read_text()
            headers, *lines = csv.split('\n')
        elif text := template.get("text"):
            headers, separator, *lines = text.strip().split('\n')
            # Remove whitespace and empty headers
            headers = [h.strip() for h in headers.split('|') if h.strip()]
            lines = [line for left_bar, *line, right_bar in [line.split('|') for line in lines]]
        else:
            print(f"For template {template}, neither filename nor text was provided.")
            raise ValueError("Template must have either a filename or text")
        
        data = []
        for line in lines:
            line = [phrase.strip() for phrase in line]
            
            replacements = defaultdict(dict)
            for header, value in zip(headers, line):
                replacements[header] = value
            
            data.append(replacements)
        return data


if __name__ == "__main__":
    document = parse_yaml("Midterm.yaml")
    walker = DocumentWalker(Path("resources"), Path("canvas_files"), lambda x: (x, []), "US/Eastern")
    document = walker.walk(document)
    print(document)
