import json
from pathlib import Path

from typing import Callable, Union

from bs4 import BeautifulSoup
from bs4.element import Tag
from datetime import datetime
from typing import Protocol, TypeAlias
from collections import defaultdict

from jinja2 import Environment

ResourceExtractor: TypeAlias = Callable[[str], tuple[str, list]]


def get_corrects_and_incorrects(question_tag):
    corrects = question_tag.css.filter('correct')
    incorrects = question_tag.css.filter('incorrect')
    return corrects, incorrects


def get_correct_comments(question_tag):
    feedback = question_tag.css.filter('correct-comments')
    return get_contents(feedback[0]) if feedback else None


def get_incorrect_comments(question_tag):
    feedback = question_tag.css.filter('incorrect-comments')
    return get_contents(feedback[0]) if feedback else None


def get_points(question_tag, default=1):
    points = question_tag.get("points", default)
    try:
        return int(points)
    except ValueError:
        print("Invalid points value: " + points)
        return default


def get_answers(question_tag):
    corrects, incorrects = get_corrects_and_incorrects(question_tag)
    return corrects + incorrects


def string_is_date(date: str):
    # For templating. The string might not be a date yet.
    # Once the template arguments are filled in, we will apply make_iso.
    if date.startswith("{") or "due" in date.lower() or "lock" in date.lower():
        return False
    has_digit = False
    for d in range(10):
        if f"{d}" in date:
            has_digit = True
    return has_digit


def make_iso(date: datetime | str | None, time_zone: str):
    # Example date: Sep 5, 2023, 12:00 AM
    # Example time_zone: ' -0600'   (mountain time)
    input_formats = [
        "%b %d, %Y, %I:%M %p %z",
        "%b %d %Y %I:%M %p %z",
        "%Y-%m-%dT%H:%M:%S%z"
    ]

    if date is None:
        return None
    if isinstance(date, datetime):
        return datetime.isoformat(date)
    elif isinstance(date, str):
        # Template dates don't need to be converted
        if not string_is_date(date):
            return date
        # If the date doesn't have  a time zone, add one
        if not "-" in date:
            date = date + time_zone
        for input_format in input_formats:
            try:
                if "-" in date:  # If the date already has a time zone
                    date = datetime.strptime(date, input_format)
                else:
                    date = datetime.strptime(date + time_zone, input_format)
                return datetime.isoformat(date)
            except ValueError:
                continue
        raise Exception(f"Invalid date format: " + date)
    else:
        raise Exception("Date must be a datetime object or a string")


def get_contents(tag):
    return "".join([str(c) for c in tag.contents])


def parse_template_data(template_tag):
    """
    Parses a template tag into a list of dictionaries
    Each dictionary will become a canvas object
    Converts the following:
    | header1 | header2    |
    |---------|------------|
    | first   | quiz       |
    | second  | assignment |
    into
    [
        {
            "header1": "first",
            "header2": "quiz"
        },
        {
            "header1": "second",
            "header2": "assignment"
        }
    ]
    """
    data = []
    headers, separator, *lines = get_contents(template_tag).strip().split('\n')
    # Remove whitespace and empty headers
    headers = [h.strip() for h in headers.split('|') if h.strip()]
    for line in lines:
        left_bar, *line, right_bar = line.split('|')
        line = [phrase.strip() for phrase in line]

        replacements = defaultdict(dict)
        for header, value in zip(headers, line):
            replacements[header] = value

        data.append(replacements)
    return data


question_types = [
    'calculated_question',
    'essay_question',
    'file_upload_question',
    'fill_in_multiple_blanks_question',
    'matching_question',
    'multiple_answers_question',
    'multiple_choice_question',
    'multiple_dropdowns_question',
    'numerical_question',
    'short_answer_question',
    'text_only_question',
    'true_false_question'
]


class TFConverter:
    @staticmethod
    def process(correct_incorrect_tag, markdown_processor: ResourceExtractor):
        is_true = correct_incorrect_tag.name == "correct"
        question_text, resources = markdown_processor(correct_incorrect_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'true_false_question',
            "points_possible": get_points(correct_incorrect_tag),
            "correct_comments": get_correct_comments(correct_incorrect_tag),
            "incorrect_comments": get_incorrect_comments(correct_incorrect_tag),
            "answers": [
                {
                    "answer_text": "True",
                    "answer_weight": 100 if is_true else 0
                },
                {
                    "answer_text": "False",
                    "answer_weight": 0 if is_true else 100
                }
            ]
        }
        return question, resources


class Processor(Protocol):
    """
    A processor takes a question tag and a Markdown processor
      returning question(s) and a list of resources
    """

    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor) -> Union[
        tuple[list[dict], list], tuple[dict, list]]:
        ...


def process(processor: Processor, question_tag, markdown_processor: ResourceExtractor):
    question, resources = processor.process(question_tag, markdown_processor)
    return question, resources


class TrueFalseProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        answers = get_answers(question_tag)
        if len(answers) != 1:
            raise Exception("True false questions must have one correct or incorrect answer\n"
                            "Answers: " + str(answers))

        question, resources = process(TFConverter(), answers[0], markdown_processor)
        if not get_points(answers[0], 0):
            points = get_points(question_tag)
            question["points_possible"] = points
        if not question["correct_comments"]:
            question["correct_comments"] = get_correct_comments(question_tag)
        if not question["incorrect_comments"]:
            question["incorrect_comments"] = get_incorrect_comments(question_tag)
        return question, resources


class MultipleTrueFalseProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        heading_question, resources = process(TextQuestionProcessor(), question_tag, markdown_processor)
        questions = [heading_question]
        for answer in get_answers(question_tag):
            tf_question, res = process(TFConverter(), answer, markdown_processor)
            questions.append(tf_question)
            resources.extend(res)
        return questions, resources


class MultipleChoiceProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        corrects, incorrects = get_corrects_and_incorrects(question_tag)
        if len(corrects) != 1:
            raise Exception("Multiple choice questions must have exactly one correct answer\n"
                            "Corrects: " + str(corrects))

        question_text, resources = markdown_processor(question_tag.contents[0])
        answers = []
        for answer in corrects + incorrects:
            answer_html, res = markdown_processor(answer.string)
            answers.append((True if answer in corrects else False, answer_html))
            resources.extend(res)

        question = {
            "question_text": question_text,
            "question_type": 'multiple_choice_question',
            "points_possible": get_points(question_tag),
            "correct_comments": get_correct_comments(question_tag),
            "incorrect_comments": get_incorrect_comments(question_tag),
            "answers": [
                {
                    "answer_html": answer_html,
                    "answer_weight": 100 if correct else 0
                } for correct, answer_html in answers
            ]
        }
        return question, resources


class MultipleAnswersProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        corrects, incorrects = get_corrects_and_incorrects(question_tag)

        question_text, resources = markdown_processor(question_tag.contents[0])
        answers = []
        for answer in corrects + incorrects:
            answer_html, res = markdown_processor(answer.string)
            answers.append((True if answer in corrects else False, answer_html))
            resources.extend(res)

        question = {
            "question_text": question_text,
            "question_type": 'multiple_answers_question',
            "points_possible": get_points(question_tag),
            "correct_comments": get_correct_comments(question_tag),
            "incorrect_comments": get_incorrect_comments(question_tag),
            "answers": [
                {
                    "answer_html": answer_html,
                    "answer_weight": 100 if correct else 0
                } for correct, answer_html in answers
            ]
        }
        return question, resources


class MatchingProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        pairs = question_tag.css.filter('pair')
        matches = []
        for pair in pairs:
            answer_left, answer_right = pair.css.filter('left')[0], pair.css.filter('right')[0]
            matches.append((answer_left.string.strip(), answer_right.string.strip()))

        distractors = question_tag.css.filter('distractors')
        distractor_text = distractors[0].contents[0].strip() if len(distractors) > 0 else None
        question_text, resources = markdown_processor(question_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'matching_question',
            "points_possible": get_points(question_tag),
            "correct_comments": get_correct_comments(question_tag),
            "incorrect_comments": get_incorrect_comments(question_tag),
            "answers": [
                {
                    "answer_match_left": answer_left,
                    "answer_match_right": answer_right,
                    "answer_weight": 100
                } for answer_left, answer_right in matches
            ],
            "matching_answer_incorrect_matches": distractor_text
        }
        return question, resources


class TextQuestionProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        question_text, resources = markdown_processor(question_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'text_only_question',
        }
        return question, resources


class OverrideParser:
    def __init__(self, date_formatter):
        self.date_formatter = date_formatter

    def parse(self, override_tag: Tag):
        override = {
            "type": "override",
            "settings": {},
            "sections": [],
            "students": [],
            "assignments": []
        }
        for tag in override_tag.find_all():
            if tag.name == "section":
                override["sections"].append(tag.contents[0])
            elif tag.name == "student":
                override["students"].append(tag.contents[0])
            elif tag.name == "assignment":
                override["assignments"].append(self.parse_assignment_tag(tag))
            elif tag.name == "template-arguments":
                override["replacements"] = parse_template_data(tag)
        return override

    def parse_assignment_tag(self, tag):
        settings = {
            "title": tag.get("title", None),
            "due_at": self.date_formatter(tag.get("due_at", None)),
            "lock_at": self.date_formatter(tag.get("available_to", None)),
            "unlock_at": self.date_formatter(tag.get("available_from", None))
        }
        return settings


class ModuleParser:
    def __init__(self):
        pass

    def parse(self, module_tag: Tag):
        module = {
            "type": "module",
            "name": module_tag["title"],
            "settings": {
                "name": module_tag["title"],
                "position": module_tag["position"],
                "published": module_tag.get("published", "true"),
            },
            "items": []
        }
        for item_tag in module_tag.find_all():
            module["items"].append(self.parse_module_item(item_tag))
        return module

    casing = {
        "file": "File",
        "page": "Page",
        "discussion": "Discussion",
        "assignment": "Assignment",
        "quiz": "Quiz",
        "subheader": "SubHeader",
        "externalurl": "ExternalUrl",
        "externaltool": "ExternalTool"
    }

    def parse_module_item(self, tag: Tag):
        item = {
            "title": tag["title"],
            "type": self.casing[tag.name],
            "position": tag.get("position", None),
            "indent": tag.get("indent", None),
            "page_url": tag.get("page_url", None),
            "external_url": tag.get("url", None),
            "new_tab": tag.get("new_tab", "true"),
            "completion_requirement": tag.get("completion_requirement", None),
            "iframe": tag.get("iframe", None),
            "published": tag.get("published", "true"),
        }
        return item


class QuizParser:
    question_processors = {
        "multiple-choice": MultipleChoiceProcessor(),
        "multiple-answers": MultipleAnswersProcessor(),
        "true-false": TrueFalseProcessor(),
        "multiple-tf": MultipleTrueFalseProcessor(),
        "matching": MatchingProcessor(),
        "text": TextQuestionProcessor()
    }

    def __init__(self, markdown_processor: ResourceExtractor, group_indexer, date_formatter):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer
        self.date_formatter = date_formatter

    def parse(self, quiz_tag: Tag):
        quiz = {
            "type": "quiz",
            "questions": [],
            "resources": [],
            "replacements": []
        }
        for tag in quiz_tag.find_all():
            if tag.name == "settings":
                quiz["settings"] = self.parse_quiz_settings(tag)
                quiz["name"] = quiz["settings"]["title"]
            elif tag.name == "template-arguments":
                quiz["replacements"] = parse_template_data(tag)
            elif tag.name == "question":
                question, res = self.parse_question(tag)
                quiz["resources"].extend(res)
                # if question is a  list of questions, add them all
                if isinstance(question, list):
                    quiz["questions"].extend(question)
                else:
                    quiz["questions"].append(question)
        return quiz

    def parse_quiz_settings(self, settings_tag):
        settings = {
            "title": settings_tag["title"],
            "quiz_type": settings_tag.get("quiz_type", "assignment"),
            "assignment_group_id": self.group_indexer(settings_tag.get("assignment_group", None)),
            "time_limit": settings_tag.get("time_limit", None),
            "shuffle_answers": settings_tag.get("shuffle_answers", False),
            "hide_results": None,
            "show_correct_answers": settings_tag.get("show_correct_answers", True),
            "show_correct_answers_last_attempt": settings_tag.get("show_correct_answers_last_attempt", False),
            "show_correct_answers_at": self.date_formatter(settings_tag.get("show_correct_answers_at", None)),
            "allowed_attempts": settings_tag.get("allowed_attempts"),
            "scoring_policy": settings_tag.get("scoring_policy", "keep_highest"),
            "one_question_at_a_time": settings_tag.get("one_question_at_a_time", False),
            "cant_go_back": settings_tag.get("cant_go_back", False),
            "access_code": settings_tag.get("access_code", None),
            "due_at": self.date_formatter(settings_tag.get("due_at", None)),
            "lock_at": self.date_formatter(settings_tag.get("available_to", None)),
            "unlock_at": self.date_formatter(settings_tag.get("available_from", None)),
            "published": settings_tag.get("published", True),
            "one_time_results": settings_tag.get("one_time_results", False),
        }
        return settings

    def parse_question(self, question_tag: Tag):
        processor = self.question_processors[question_tag["type"]]
        return processor.process(question_tag, self.markdown_processor)


class AssignmentParser:
    def __init__(self, markdown_processor: ResourceExtractor, group_indexer, date_formatter):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer
        self.date_formatter = date_formatter

    def parse(self, assignment_tag):
        assignment = {
            "name": "",
            "type": "assignment",
            "resources": [],
            "replacements": [],
            "settings": {}
        }
        for tag in assignment_tag.find_all():
            if tag.name == "settings":
                settings = self.parse_assignment_settings(tag)
                assignment["settings"].update(settings)
            elif tag.name == "template-arguments":
                assignment["replacements"] = parse_template_data(tag)
            elif tag.name == "description":
                contents = get_contents(tag)
                description, res = self.markdown_processor(contents)
                assignment["settings"]["description"] = description
                assignment["resources"].extend(res)

        assignment["name"] = assignment["settings"]["name"]
        return assignment

    def get_list(self, string):
        items = string.strip().split(',')
        return [l.strip() for l in items if l.strip()]

    def get_bool(self, string):
        if string.lower() == "true":
            return True
        else:
            return False

    def get_dict(self, string):
        items = string.strip().split(',')
        return {l.strip().split('=')[0]: l.strip().split('=')[1] for l in items if l.strip()}

    def parse_assignment_settings(self, settings_tag):
        settings = {
            "name": settings_tag["title"],
            "position": settings_tag.get("position", None),
            "submission_types": self.get_list(settings_tag.get("submission_types", "none")),
            "allowed_extensions": self.get_list(settings_tag.get("allowed_extensions", "")),
            "turnitin_enabled": self.get_bool(settings_tag.get("turnitin_enabled", "False")),
            "vericite_enabled": self.get_bool(settings_tag.get("vericite_enabled", "False")),
            "turnitin_settings": settings_tag.get("turnitin_settings", None),
            "integration_data": settings_tag.get("integration_data", None),
            "peer_reviews": self.get_bool(settings_tag.get("peer_reviews", "False")),
            "automatic_peer_reviews": self.get_bool(settings_tag.get("automatic_peer_reviews", "False")),
            "notify_of_update": self.get_bool(settings_tag.get("notify_of_update", "False")),
            "group_category_id": settings_tag.get("group_category", None),
            "grade_group_students_individually": self.get_bool(
                settings_tag.get("grade_group_students_individually", "False")),
            "external_tool_tag_attributes": self.get_dict(settings_tag.get("external_tool_tag_attributes", "")),
            "points_possible": settings_tag.get("points_possible", None),
            "grading_type": settings_tag.get("grading_type", "points"),
            "due_at": self.date_formatter(settings_tag.get("due_at", None)),
            "lock_at": self.date_formatter(settings_tag.get("available_to", None)),
            "unlock_at": self.date_formatter(settings_tag.get("available_from", None)),
            "assignment_group_id": self.group_indexer(settings_tag.get("assignment_group", None)),
            "assignment_overrides": settings_tag.get("assignment_overrides", None),
            "only_visible_to_overrides": self.get_bool(settings_tag.get("only_visible_to_overrides", "False")),
            "published": self.get_bool(settings_tag.get("published", "True")),
            "grading_standard_id": settings_tag.get("grading_standard_id", None),
            "omit_from_final_grade": self.get_bool(settings_tag.get("omit_from_final_grade", "False")),
            "hide_in_gradebook": self.get_bool(settings_tag.get("hide_in_gradebook", "False")),
            "quiz_lti": settings_tag.get("quiz_lti", None),
            "moderated_grading": self.get_bool(settings_tag.get("moderated_grading", "False")),
            "grader_count": settings_tag.get("grader_count", None),
            "final_grader_id": settings_tag.get("final_grader_id", None),
            "grader_comments_visible_to_graders": self.get_bool(
                settings_tag.get("grader_comments_visible_to_graders", "False")),
            "graders_anonymous_to_graders": self.get_bool(settings_tag.get("graders_anonymous_to_graders", "False")),
            "grader_names_visible_to_final_grader": self.get_bool(
                settings_tag.get("grader_names_visible_to_final_grader", "False")),
            "anonymous_grading": self.get_bool(settings_tag.get("anonymous_grading", "False")),
            "allowed_attempts": -1 if settings_tag.get("grading_type") == "not_graded" else settings_tag.get("allowed_attempts"),
            "annotatable_attachment_id": settings_tag.get("annotatable_attachment_id", None),
        }
        return settings


class PageParser:
    def __init__(self, markdown_processor: ResourceExtractor, date_formatter):
        self.markdown_processor = markdown_processor
        self.date_formatter = date_formatter

    def parse(self, page_tag):
        page = {
            "type": "page",
            "name": page_tag["title"],
            "settings": {
                "title": page_tag["title"],
                "body": "",
                "editing_roles": page_tag.get("editing_roles", "teachers"),
                "notify_of_update": page_tag.get("notify_of_update", False),
                "published": page_tag.get("published", True),
                "front_page": page_tag.get("front_page", False),
                "publish_at": self.date_formatter(page_tag.get("publish_at", None)),
            },
            "resources": []
        }
        contents = "".join([str(c) for c in page_tag.contents])
        body, res = self.markdown_processor(contents)
        page["settings"]["body"] = body
        page["resources"].extend(res)
        return page


class DocumentParser:
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

        self.element_processors = {
            "quiz": QuizParser(self.markdown_processor, group_identifier, self.date_formatter),
            "assignment": AssignmentParser(self.markdown_processor, group_identifier, self.date_formatter),
            "page": PageParser(self.markdown_processor, self.date_formatter),
            "module": ModuleParser(),
            "override": OverrideParser(self.date_formatter)
        }

    def parse(self, text):
        soup = BeautifulSoup(text, "html.parser")
        document = []
        for tag in soup.children:
            parser = self.element_processors.get(tag.name, None)
            if parser:
                elements = parser.parse(tag)
                if not isinstance(elements, list):
                    elements = [elements]
                for element in elements:
                    new_elements = self.create_elements_from_template(element)
                    document.extend(new_elements)
        return document

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
                context[key] = value.replace('"','\\"')
            # For each replacement, create an object from the template
            rendered = template.render(context)
            element = json.loads(rendered)
            elements.append(element)

        # Replacements become unnecessary after creating the elements
        for element in elements:
            del element["replacements"]
        return elements
