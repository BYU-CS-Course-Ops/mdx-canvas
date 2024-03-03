import json
from pathlib import Path

from typing import Callable, Union

import pytz
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
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
    return get_img_and_text_contents(feedback[0]) if feedback else None


def get_incorrect_comments(question_tag):
    feedback = question_tag.css.filter('incorrect-comments')
    return get_img_and_text_contents(feedback[0]) if feedback else None


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


def get_img_and_text_contents(tag):
    """
    Typically, the body of a tag is found at contents[0], and sub-tags (like answers) are found later.
    However, images sometimes separate the text into multiple parts.
    This function joins the text and images together.
    """
    return "".join(
        [str(c) for c in tag.contents if isinstance(c, NavigableString) or (isinstance(c, Tag) and c.name == "img")])


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
        question_text, resources = markdown_processor(get_img_and_text_contents(correct_incorrect_tag))
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
        tuple[list[dict], list], tuple[dict, list]]: ...


class AttributeAdder:
    def __init__(self, settings: dict, settings_tag: Tag):
        self.settings = settings
        self.settings_tag = settings_tag

    def __call__(self, attribute, default=None, new_name=None, formatter=None):
        if attribute in self.settings_tag.attrs or default is not None:
            value = self.settings_tag.get(attribute, default)
            if formatter:
                value = formatter(value)
            self.settings[new_name if new_name else attribute] = value


def process(processor: Processor, question_tag, markdown_processor: ResourceExtractor):
    question, resources = processor.process(question_tag, markdown_processor)
    return question, resources


class TrueFalseProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        answers = get_answers(question_tag)

        check_correct_size(answers, 1, "True/False")

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


def check_correct_size(corrects: list, num, question_type):
    if num is not None and len(corrects) != num:
        raise Exception(f"{question_type} must have exactly {num} correct answer(s)\n"
                        "Answers: " + str(corrects))


class MultipleCommonProcessor:
    question_type: str
    num_correct: Union[int, None]

    def process(self, question_tag, markdown_processor: ResourceExtractor):
        corrects, incorrects = get_corrects_and_incorrects(question_tag)
        check_correct_size(corrects, self.num_correct, self.question_type)

        question_text, resources = markdown_processor(get_img_and_text_contents(question_tag))
        answers = []
        for answer in corrects + incorrects:
            answer_html, res = markdown_processor(get_img_and_text_contents(answer))
            answers.append((True if answer in corrects else False, answer_html))
            resources.extend(res)

        question = {
            "question_text": question_text,
            "question_type": self.question_type,
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


class MultipleChoiceProcessor(MultipleCommonProcessor):
    question_type = 'multiple_choice_question'
    num_correct = 1

    def process(self, question_tag, markdown_processor: ResourceExtractor):
        return super().process(question_tag, markdown_processor)


class MultipleAnswersProcessor(MultipleCommonProcessor):
    question_type = 'multiple_answers_question'
    num_correct = None

    def process(self, question_tag, markdown_processor: ResourceExtractor):
        return super().process(question_tag, markdown_processor)


class MatchingProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        pairs = question_tag.css.filter('pair')
        matches = []
        for pair in pairs:
            answer_left, answer_right = pair.css.filter('left')[0], pair.css.filter('right')[0]
            matches.append((answer_left.string.strip(), answer_right.string.strip()))

        distractors = question_tag.css.filter('distractors')
        distractor_text = get_img_and_text_contents(distractors[0]).strip() if len(distractors) > 0 else None
        question_text, resources = markdown_processor(get_img_and_text_contents(question_tag))
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
        question_text, resources = markdown_processor(get_img_and_text_contents(question_tag))
        question = {
            "question_text": question_text,
            "question_type": 'text_only_question',
        }
        return question, resources


class Parser:
    @staticmethod
    def get_list(string):
        items = string.strip().split(',')
        return [cell.strip() for cell in items if cell.strip()]

    @staticmethod
    def get_bool(string):
        # Forgiving boolean parser
        if isinstance(string, bool):
            return string

        if string.lower() == "true":
            return True
        elif string.lower() == "false":
            return False
        else:
            raise ValueError(f"Invalid boolean value: {string}")

    @staticmethod
    def get_dict(string):
        # Assumes the string is a comma-separated list of key-value pairs
        # Example: "key1=value1, key2=value2 "
        return dict(cell.strip().split('=') for cell in string.split(',') if cell.strip())


class OverrideParser:
    def __init__(self, date_formatter, templater, parser):
        self.date_formatter = date_formatter
        self.template = templater
        self.parser = parser

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
                override["sections"].append(get_img_and_text_contents(tag))
            elif tag.name == "student":
                override["students"].append(get_img_and_text_contents(tag))
            elif tag.name == "assignment":
                override["assignments"].append(self.parse_assignment_tag(tag))
            elif tag.name == "template-arguments":
                override["replacements"] = self.template(tag)
        return override

    def parse_assignment_tag(self, tag):
        settings = {
            "title": tag["title"],
        }
        adder = AttributeAdder(settings, tag)
        adder("available_from", new_name="unlock_at", formatter=self.date_formatter)
        adder("due_at", formatter=self.date_formatter)
        adder("available_to", new_name="lock_at", formatter=self.date_formatter)
        return settings


class ModuleParser:
    def __init__(self, parser):
        self.parser = parser

    def parse_module_settings(self, module_tag):
        settings = {
            "name": module_tag["title"],
            "position": module_tag["position"],
        }
        AttributeAdder(settings, module_tag)("published", False, formatter=self.parser.get_bool)
        return settings

    def parse(self, module_tag: Tag):
        module = {
            "type": "module",
            "name": module_tag["title"],
            "settings": self.parse_module_settings(module_tag),
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
        }

        adder = AttributeAdder(item, tag)
        adder("position")
        adder("indent")
        adder("page_url")
        adder("external_url")
        adder("new_tab", True, formatter=self.parser.get_bool)
        adder("completion_requirement")
        adder("iframe")
        adder("published", False, formatter=self.parser.get_bool)
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

    def __init__(self, markdown_processor: ResourceExtractor, group_indexer, date_formatter, templater, parser):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer
        self.date_formatter = date_formatter
        self.template = templater
        self.parser = parser

    def parse(self, quiz_tag: Tag):
        quiz = {
            "type": "quiz",
            "questions": [],
            "resources": [],
            "replacements": [],
            "settings": {}
        }
        for tag in quiz_tag.find_all():
            if tag.name == "settings":
                quiz["settings"] = self.parse_quiz_settings(tag)
                quiz["name"] = quiz["settings"]["title"]
            elif tag.name == "template-arguments":
                quiz["replacements"] = self.template(tag)
            elif tag.name == "question":
                question, res = self.parse_question(tag)
                quiz["resources"].extend(res)
                # if question is a  list of questions, add them all
                if isinstance(question, list):
                    quiz["questions"].extend(question)
                else:
                    quiz["questions"].append(question)
            elif tag.name == "description":
                description, res = self.markdown_processor(get_img_and_text_contents(tag))
                quiz["resources"].extend(res)
                quiz["settings"]["description"] = description
        return quiz

    def parse_quiz_settings(self, settings_tag):
        settings = {"title": settings_tag["title"]}

        adder = AttributeAdder(settings, settings_tag)

        adder("quiz_type", "assignment")
        adder("assignment_group", None, "assignment_group_id", formatter=self.group_indexer)
        adder("time_limit")
        adder("points_possible")
        adder("shuffle_answers", False, formatter=self.parser.get_bool)
        adder("hide_results", formatter=self.parser.get_bool)
        adder("show_correct_answers", True, formatter=self.parser.get_bool)
        adder("show_correct_answers_last_attempt", False, formatter=self.parser.get_bool)
        adder("show_correct_answers_at", None, formatter=self.date_formatter)
        adder("hide_correct_answers_at", None, formatter=self.date_formatter)
        adder("allowed_attempts")
        adder("scoring_policy", "keep_highest")
        adder("one_question_at_a_time", False, formatter=self.parser.get_bool)
        adder("cant_go_back", False, formatter=self.parser.get_bool)
        adder("available_from", None, "unlock_at", formatter=self.date_formatter)
        adder("due_at", None, formatter=self.date_formatter)
        adder("available_to", None, "lock_at", formatter=self.date_formatter)
        adder("access_code")
        adder("published", False, formatter=self.parser.get_bool)
        adder("one_time_results", False, formatter=self.parser.get_bool)

        return settings

    def parse_question(self, question_tag: Tag):
        processor = self.question_processors[question_tag["type"]]
        return processor.process(question_tag, self.markdown_processor)


class AssignmentParser:
    def __init__(self, markdown_processor: ResourceExtractor, group_indexer, date_formatter, templater, parser):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer
        self.date_formatter = date_formatter
        self.template = templater
        self.parser = parser

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
                assignment["replacements"] = self.template(tag)
            elif tag.name == "description":
                contents = get_img_and_text_contents(tag)
                description, res = self.markdown_processor(contents)
                assignment["settings"]["description"] = description
                assignment["resources"].extend(res)

        assignment["name"] = assignment["settings"]["name"]
        return assignment

    def parse_assignment_settings(self, settings_tag):
        settings = {"name": settings_tag["title"]}

        adder = AttributeAdder(settings, settings_tag)
        adder("position")
        adder("submission_types", "none", formatter=self.parser.get_list)
        adder("allowed_extensions", "", formatter=self.parser.get_list)
        adder("turnitin_enabled", False, formatter=self.parser.get_bool)
        adder("vericite_enabled", False, formatter=self.parser.get_bool)
        adder("turnitin_settings")
        adder("integration_data")
        adder("peer_reviews", False, formatter=self.parser.get_bool)
        adder("automatic_peer_reviews", False, formatter=self.parser.get_bool)
        adder("notify_of_update", False, formatter=self.parser.get_bool)
        adder("group_category", new_name="group_category_id")
        adder("grade_group_students_individually", False, formatter=self.parser.get_bool)
        adder("external_tool_tag_attributes", "", formatter=self.parser.get_dict)
        adder("points_possible")
        adder("grading_type", "points")
        adder("available_from", new_name="unlock_at", formatter=self.date_formatter)
        adder("due_at", formatter=self.date_formatter)
        adder("available_to", new_name="lock_at", formatter=self.date_formatter)
        adder("assignment_group", new_name="assignment_group_id", formatter=self.group_indexer)
        adder("assignment_overrides")
        adder("only_visible_to_overrides", False, formatter=self.parser.get_bool)
        adder("published", False, formatter=self.parser.get_bool)
        adder("grading_standard_id")
        adder("omit_from_final_grade", False, formatter=self.parser.get_bool)
        adder("hide_in_gradebook", False, formatter=self.parser.get_bool)
        adder("quiz_lti")
        adder("moderated_grading", False, formatter=self.parser.get_bool)
        adder("grader_count")
        adder("final_grader_id")
        adder("grader_comments_visible_to_graders", False, formatter=self.parser.get_bool)
        adder("graders_anonymous_to_graders", False, formatter=self.parser.get_bool)
        adder("grader_names_visible_to_final_grader", False, formatter=self.parser.get_bool)
        adder("anonymous_grading", False, formatter=self.parser.get_bool)
        adder("allowed_attempts", formatter=lambda x: -1 if x == "not_graded" else x)
        adder("annotatable_attachment_id")

        return settings


class PageParser:
    def __init__(self, markdown_processor: ResourceExtractor, date_formatter, parser):
        self.markdown_processor = markdown_processor
        self.date_formatter = date_formatter
        self.parser = parser

    def parse_page_settings(self, page_tag):
        settings = {
            "type": "page",
            "name": page_tag["title"],
            "body": "",
        }
        adder = AttributeAdder(settings, page_tag)
        adder("editing_roles", "teachers")
        adder("notify_of_update", False, formatter=self.parser.get_bool)
        adder("published", False, formatter=self.parser.get_bool)
        adder("front_page", False, formatter=self.parser.get_bool)
        adder("publish_at", formatter=self.date_formatter)
        return settings

    def parse(self, page_tag):
        page = {
            "type": "page",
            "name": page_tag["title"],
            "settings": self.parse_page_settings(page_tag),
            "resources": []
        }
        contents = get_img_and_text_contents(page_tag)
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

        parser = Parser()

        self.element_processors = {
            "quiz": QuizParser(self.markdown_processor, group_identifier, self.date_formatter,
                               self.parse_template_data, parser),
            "assignment": AssignmentParser(self.markdown_processor, group_identifier, self.date_formatter,
                                           self.parse_template_data, parser),
            "page": PageParser(self.markdown_processor, self.date_formatter, parser),
            "module": ModuleParser(parser),
            "override": OverrideParser(self.date_formatter, self.parse_template_data, parser)
        }

    def parse(self, text):
        soup = BeautifulSoup(text, "html.parser")
        document = []
        tag: Tag
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
                context[key] = value.replace('"', '\\"')
            # For each replacement, create an object from the template
            rendered = template.render(context)
            element = json.loads(rendered)
            elements.append(element)

        # Replacements become unnecessary after creating the elements
        for element in elements:
            del element["replacements"]
        return elements

    def parse_template_data(self, template_tag):
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
        if template_tag.get("filename"):
            csv = (self.path_to_files / template_tag.get("filename")).read_text()
            headers, *lines = csv.split('\n')
        else:
            headers, separator, *lines = get_img_and_text_contents(template_tag).strip().split('\n')
            # Remove whitespace and empty headers
            headers = [h.strip() for h in headers.split('|') if h.strip()]
            lines = [line for left_bar, *line, right_bar in [line.split('|') for line in lines]]

        data = []
        for line in lines:
            line = [phrase.strip() for phrase in line]

            replacements = defaultdict(dict)
            for header, value in zip(headers, line):
                replacements[header] = value

            data.append(replacements)
        return data
