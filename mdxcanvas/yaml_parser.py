# parse the yaml file and return the data
from collections import OrderedDict
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Callable
from typing import TypeAlias

import pytz
from jinja2 import Environment
from strictyaml import load

from .templating import Templater
from .document_schema import document_schema

ResourceExtractor: TypeAlias = Callable[[str], tuple[str, list]]


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


def parse_yaml(text: str) -> list:
    document = load(text, document_schema).data
    return document


class TextQuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
    
    def walk(self, question: dict):
        question, resources = self.markdown_processor(question["text"])
        return {"question_text": question, "question_type": "text_only_question"}, resources


class TrueFalseQuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
    
    def walk(self, question):
        text, resources = self.markdown_processor(question["text"])
        correct = question.get("correct")
        
        new_question = {
            "question_text": text,
            "question_type": "true_false_question",
            "points_possible": question.get("points_possible", 1),
            "answers": [
                {"answer_text": "True", "answer_weight": 100 if correct else 0},
                {"answer_text": "False", "answer_weight": 0 if correct else 100}
            ]
        }
        for key in ["correct_comments", "incorrect_comments"]:
            if question.get(key):
                new_question[key] = question[key]
        return new_question, resources


class MultipleCommonQuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
    
    def walk(self, question: dict):
        text, resources = self.markdown_processor(question["text"])
        
        answers = question["answers"]
        corrects = [answer["correct"] for answer in answers if answer.get("correct", False)]
        incorrects = [answer["incorrect"] for answer in answers if answer.get("incorrect", False)]
        
        answers = []
        for answer in corrects + incorrects:
            answer_text, res = self.markdown_processor(answer)
            resources.extend(res)
            answers.append({
                "answer_html": answer_text,
                "answer_weight": 100 if answer in corrects else 0
            })
        
        new_question = {
            "question_text": text,
            "question_type": "multiple_answers_question" if question[
                                                                "type"] == "multiple_answers" else "multiple_choice_question",
            "points_possible": question.get("points_possible", 1),
            "correct_comments": question.get("correct_comments"),
            "incorrect_comments": question.get("incorrect_comments"),
            "answers": answers
        }
        return new_question, resources


class MultipleChoiceQuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
        self.multiple_answers_walker = MultipleCommonQuestionWalker(markdown_processor)
    
    def walk(self, question: dict):
        corrects = [a["correct"] for a in question["answers"] if a.get("correct", False)]
        
        if len(corrects) != 1:
            print(question["answers"])
            raise ValueError(f"Multiple choice questions must have exactly one correct answer.\n"
                             f"Question: \n"
                             f"\t{question['text']}\n"
                             f"Correct answers given: \n"
                             f"\t" + "\n\t".join(corrects))
        
        return self.multiple_answers_walker.walk(question)


class MatchingQuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
    
    def walk(self, question: dict):
        text, resources = self.markdown_processor(question["text"])
        
        answers = []
        for pair in question["answers"]:
            left, right = pair["left"], pair["right"]
            answers.append({
                "answer_match_left": left,
                "answer_match_right": right,
                "answer_weight": 100
            })
        
        distractor_text = question.get("distractors", None)
        
        new_question = {
            "question_text": text,
            "question_type": "matching_question",
            "points_possible": question.get("points_possible", 1),
            "correct_comments": question.get("correct_comments"),
            "incorrect_comments": question.get("incorrect_comments"),
            "answers": answers,
            "matching_answer_incorrect_matches": distractor_text
        }
        return new_question, resources


class MultipleTrueFalseQuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
        self.true_false_walker = TrueFalseQuestionWalker(markdown_processor)
        self.text_walker = TextQuestionWalker(markdown_processor)
        
    def walk(self, question: dict):
        """
        Breaks up a multiple true/false question into multiple true/false questions
        Uses the text as the text to a text_only_question
        Correct answers are converted to a true_false_question where True is the correct answer
        Incorrect answers are converted to a true_false_question where False is the correct answer
        """
        new_questions = []
        text, resources = self.markdown_processor(question["text"])
        
        q, r = self.text_walker.walk({"text": text})
        new_questions.append(q)
        resources.extend(r)
        
        for answer in question["answers"]:
            correct = answer.get("correct", False)
            tf_question = {
                "type": "true_false",
                "text": answer["correct" if correct else "incorrect"],
                "points_possible": question.get("points_possible", 1),
                "correct": correct,
            }
            q, r = self.true_false_walker.walk(tf_question)
            new_questions.append(q)
            resources.extend(r)
        
        return new_questions, resources


class QuestionWalker:
    def __init__(self, markdown_processor: ResourceExtractor):
        self.markdown_processor = markdown_processor
        self.child_walkers = {
            "text": TextQuestionWalker(markdown_processor),
            "multiple_choice": MultipleChoiceQuestionWalker(markdown_processor),
            "true_false": TrueFalseQuestionWalker(markdown_processor),
            "multiple_answers": MultipleCommonQuestionWalker(markdown_processor),
            "matching": MatchingQuestionWalker(markdown_processor),
            "multiple_tf": MultipleTrueFalseQuestionWalker(markdown_processor)
        }
    
    def walk(self, question: dict):
        if child_walker := self.child_walkers.get(question["type"]):
            return child_walker.walk(question)
        else:
            raise ValueError(f"Invalid question type: {question['type']}")


class QuizWalker:
    def __init__(self, markdown_processor: ResourceExtractor, group_identifier: Callable, date_formatter: Callable,
                 parse_template_data: Callable):
        self.markdown_processor = markdown_processor
        self.group_identifier = group_identifier
        self.date_formatter = date_formatter
        self.parse_template_data = parse_template_data
        self.question_walker = QuestionWalker(markdown_processor)
    
    def walk(self, quiz: dict):
        new_quiz = {
            "resources": [], "one_question_at_a_time": False,
            "one_time_results": False,
            "published": False,
            "cant_go_back": False,
            "scoring_policy": "keep_highest",
            "show_correct_answers": True,
            "show_correct_answers_last_attempt": False,
        }
        for key, value in quiz.items():
            if key in ["due_at", "lock_at", "unlock_at", "show_correct_answers_at", "hide_correct_answers_at"]:
                new_quiz[key] = self.date_formatter(value)
            elif key == "title":
                new_quiz["name"] = value
                new_quiz["title"] = value
            elif key == "description":
                new_quiz["description"], res = self.markdown_processor(quiz["description"])
                new_quiz["resources"].extend(res)
            elif key == "assignment_group":
                new_quiz["assignment_group_id"] = self.group_identifier(value)
            elif key == "questions":
                new_quiz["questions"] = []
                for question in value:
                    new_questions, res = self.question_walker.walk(question)
                    if not isinstance(new_questions, list):
                        new_questions = [new_questions]
                    new_quiz["questions"].extend(new_questions)
                    new_quiz["resources"].extend(res)
            else:
                new_quiz[key] = value
        
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


def order_elements(element: dict) -> OrderedDict:
    new_list = []
    for key, value in element.items():
        if isinstance(value, dict):
            new_list.append((key, order_elements(value)))
        else:
            new_list.append((key, value))
    return OrderedDict(sorted(element.items(), key=lambda x: x[0]))


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
        
        self.templater = Templater(self.jinja_env, self.path_to_files)
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
    
    def walk(self, documents: list):
        new_documents = []
        for document in documents:
            if child_walker := self.child_walkers.get(document["type"]):
                templates = child_walker.walk(document)
                if not isinstance(templates, list):
                    templates = [templates]
                templates = [order_elements(template) for template in templates]
                for template in templates:
                    new_documents.extend(self.templater.create_elements_from_template(template))
        return new_documents
    
    
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

