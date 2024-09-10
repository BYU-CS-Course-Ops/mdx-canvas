import textwrap
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Callable, Union
from typing import Protocol, TypeAlias

import pytz
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from jinja2 import Environment


ResourceExtractor: TypeAlias = Callable[[str], tuple[str, list]]


def order_elements(element: dict) -> OrderedDict:
    new_list = []
    for key, value in element.items():
        if isinstance(value, dict):
            new_list.append((key, order_elements(value)))
        else:
            new_list.append((key, value))
    return OrderedDict(sorted(element.items(), key=lambda x: x[0]))


def get_corrects(question_tag):
    corrects = question_tag.select('correct')
    return corrects


def get_correct_comments(question_tag):
    feedback = question_tag.select('correct-comments')
    return get_text_contents(feedback[0]) if feedback else None


def get_incorrect_comments(question_tag):
    feedback = question_tag.select('incorrect-comments')
    return get_text_contents(feedback[0]) if feedback else None


def get_points(question_tag, default=1):
    points = question_tag.get("points", default)
    try:
        return int(points)
    except ValueError:
        print("Invalid points value: " + points)
        return default


def get_answers(question_tag):
    return question_tag.select('correct, incorrect')


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


def get_text_contents(tag, children_tag_names: list[str] = ()):
    """
    Typically, the body of a tag is found at contents[0], and sub-tags (like answers) are found later.
    However, images sometimes separate the text into multiple parts.
    This function joins the text and images together.
    """
    return textwrap.dedent("".join(
        [str(c) for c in tag.contents if
         isinstance(c, NavigableString) or (isinstance(c, Tag) and c.name not in children_tag_names)]))


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
        question_text, resources = markdown_processor(
            get_text_contents(correct_incorrect_tag, ["correct-comments", "incorrect-comments"]))
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
    def __init__(self, settings: dict, settings_tag: Tag, parser):
        self.settings = settings
        self.settings_tag = settings_tag
        self.parser = parser

    def __call__(self, attribute, default=None, new_name=None, formatter=None, typ=None):
        if attribute in self.settings_tag.attrs or default is not None:
            value = self.settings_tag.get(attribute, default)
            if formatter:
                value = formatter(value)
            if typ:
                value = self.parser.parse(value, typ)
            self.settings[new_name if new_name else attribute] = value


def process(processor: Processor, question_tag, markdown_processor: ResourceExtractor):
    question, resources = processor.process(question_tag, markdown_processor)
    return question, resources


class TrueFalseProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: ResourceExtractor):
        answers = get_answers(question_tag)

        check_answer_size(answers, 1, "True/False question must have exactly 1 answer!")

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
        header_question_text, resources = markdown_processor(
            get_text_contents(question_tag, ["correct", "incorrect", "correct-comments", "incorrect-comments"]))
        header_question = {
            "question_text": header_question_text,
            "question_type": 'text_only_question',
        }
        questions = [header_question]
        for answer in get_answers(question_tag):
            tf_question, res = process(TFConverter(), answer, markdown_processor)
            questions.append(tf_question)
            resources.extend(res)
        return questions, resources


def check_answer_size(answers: list, num, explanation):
    if num is not None and len(answers) != num:
        raise Exception(f"{explanation}\n"
                        "Answers: " + str(answers))


class MultipleCommonProcessor:
    question_type: str
    num_correct: Union[int, None]

    def process(self, question_tag, markdown_processor: ResourceExtractor):
        corrects = get_corrects(question_tag)
        check_answer_size(corrects, self.num_correct,
                          f"{self.question_type} questions must have exactly {self.num_correct} correct answer!")

        question_text, resources = markdown_processor(
            get_text_contents(question_tag, ["correct", "incorrect", "correct-comments", "incorrect-comments"]))
        answers = []
        for answer in get_answers(question_tag):
            answer_html, res = markdown_processor(get_text_contents(answer))
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
        pairs = question_tag.select('pair')
        matches = []
        for pair in pairs:
            answer_left, answer_right = pair.select('left')[0], pair.select('right')[0]
            matches.append((answer_left.string.strip(), answer_right.string.strip()))

        distractors = question_tag.select('distractors')
        distractor_text = get_text_contents(distractors[0]).strip() if len(distractors) > 0 else None

        question_text, resources = markdown_processor(get_text_contents(
            question_tag,
            ["pair", "distractors", "correct-comments", "incorrect-comments"]
        ))

        question = {
            "question_text": question_text,
            "question_type": 'matching_question',
            "points_possible": get_points(question_tag, default=len(matches)),
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
        question_text, resources = markdown_processor(get_text_contents(question_tag))
        question = {
            "question_text": question_text,
            "question_type": 'text_only_question',
        }
        return question, resources


class Parser:
    def __init__(self):
        pass

    def parse(self, string, typ):
        if typ == str:
            return string
        elif typ == int:
            return self.get_int(string)
        elif typ == bool:
            return self.get_bool(string)
        elif typ == list:
            return self.get_list(string)
        elif typ == dict:
            return self.get_dict(string)

    def get_list(self, string):
        items = string.strip().split(',')
        return [cell.strip() for cell in items if cell.strip()]

    def get_bool(self, string):
        # Forgiving boolean parser
        if isinstance(string, bool):
            return string

        if string.lower() == "true":
            return True
        elif string.lower() == "false":
            return False
        else:
            raise ValueError(f"Invalid boolean value: {string}")

    def get_dict(self, string):
        # Assumes the string is a comma-separated list of key-value pairs
        # Example: "key1=value1, key2=value2 "
        return dict(cell.strip().split('=') for cell in string.split(',') if cell.strip())

    def get_int(self, string):
        return int(string)


class OverrideParser:
    def __init__(self, date_formatter, parser):
        self.date_formatter = date_formatter
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
                override["sections"].append(get_text_contents(tag))
            elif tag.name == "student":
                override["students"].append(get_text_contents(tag))
            elif tag.name == "assignment":
                override["assignments"].append(self.parse_assignment_tag(tag))
        return override

    def parse_assignment_tag(self, tag):
        settings = {
            "title": tag["title"],
        }
        adder = AttributeAdder(settings, tag, self.parser)
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
        AttributeAdder(settings, module_tag, self.parser)("published", False, bool)
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

        adder = AttributeAdder(item, tag, self.parser)
        adder("position", int)
        adder("indent", int)
        adder("page_url")
        adder("external_url")
        adder("new_tab", True, bool)
        adder("completion_requirement")
        adder("iframe")
        adder("published", False, bool)
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

    def __init__(self, markdown_processor: ResourceExtractor, group_indexer, date_formatter, parser):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer
        self.date_formatter = date_formatter
        self.parser = parser

    def parse(self, quiz_tag: Tag):
        quiz = {
            "type": "quiz",
            "name": quiz_tag["title"],
            "questions": [],
            "resources": []
        }
        quiz.update(self.parse_quiz_settings(quiz_tag))

        for tag in quiz_tag.find_all():
            if tag.name == "question":
                question, res = self.parse_question(tag)
                quiz["resources"].extend(res)
                # if question is a  list of questions, add them all
                if isinstance(question, list):
                    quiz["questions"].extend(question)
                else:
                    quiz["questions"].append(question)
            elif tag.name == "description":
                description, res = self.markdown_processor(get_text_contents(tag))
                quiz["resources"].extend(res)
                quiz["description"] = description
        return quiz

    def parse_quiz_settings(self, settings_tag):
        settings = {"title": settings_tag["title"]}

        adder = AttributeAdder(settings, settings_tag, self.parser)

        adder("quiz_type", "assignment")
        adder("assignment_group", None, "assignment_group_id", formatter=self.group_indexer)
        adder("time_limit", None, typ=int)
        adder("shuffle_answers", False, typ=bool)
        adder("hide_results", typ=str)
        adder("show_correct_answers", True, typ=bool)
        adder("show_correct_answers_last_attempt", False, typ=bool)
        adder("show_correct_answers_at", None, formatter=self.date_formatter)
        adder("hide_correct_answers_at", None, formatter=self.date_formatter)
        adder("allowed_attempts", -1, typ=int)
        adder("scoring_policy", "keep_highest")
        adder("one_question_at_a_time", False, typ=bool)
        adder("cant_go_back", False, typ=bool)
        adder("available_from", None, "unlock_at", formatter=self.date_formatter)
        adder("due_at", None, formatter=self.date_formatter)
        adder("available_to", None, "lock_at", formatter=self.date_formatter)
        adder("access_code")
        adder("published", False, typ=bool)
        adder("one_time_results", False, typ=bool)

        return settings

    def parse_question(self, question_tag: Tag):
        processor = self.question_processors[question_tag["type"]]
        return processor.process(question_tag, self.markdown_processor)


class AssignmentParser:
    def __init__(self, markdown_processor: ResourceExtractor, group_indexer, date_formatter, parser):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer
        self.date_formatter = date_formatter
        self.parser = parser

    def parse(self, assignment_tag):
        assignment = {
            "type": "assignment",
            "name": assignment_tag["title"],
            "resources": [],
            "settings": self.parse_assignment_settings(assignment_tag)
        }

        for tag in assignment_tag.find_all():
            if tag.name == "description":
                contents = get_text_contents(tag)
                description, res = self.markdown_processor(contents)
                assignment["settings"]["description"] = description
                assignment["resources"].extend(res)

        assignment["name"] = assignment["name"]
        return assignment

    def parse_assignment_settings(self, settings_tag):
        settings = {"name": settings_tag["title"]}

        adder = AttributeAdder(settings, settings_tag, self.parser)
        adder("allowed_attempts", formatter=lambda x: -1 if x == "not_graded" else x),
        adder("allowed_extensions", "", typ=list),
        adder("annotatable_attachment_id"),
        adder("assignment_group", new_name="assignment_group_id", formatter=self.group_indexer),
        adder("assignment_overrides"),
        adder("automatic_peer_reviews", False, typ=bool),
        adder("available_from", new_name="unlock_at", formatter=self.date_formatter),
        adder("available_to", new_name="lock_at", formatter=self.date_formatter),
        adder("due_at", formatter=self.date_formatter),
        adder("external_tool_tag_attributes", "", typ=dict),
        adder("final_grader_id"),
        adder("grade_group_students_individually", False, typ=bool),
        adder("grading_standard_id"),
        adder("grading_type", "points"),
        adder("grader_comments_visible_to_graders", False, typ=bool),
        adder("grader_count"),
        adder("grader_names_visible_to_final_grader", False, typ=bool),
        adder("graders_anonymous_to_graders", False, typ=bool),
        adder("group_category", new_name="group_category_id"),
        adder("hide_in_gradebook", False, typ=bool),
        adder("integration_data"),
        adder("moderated_grading", False, typ=bool),
        adder("notify_of_update", False, typ=bool),
        adder("omit_from_final_grade", False, typ=bool),
        adder("only_visible_to_overrides", False, typ=bool),
        adder("peer_reviews", False, typ=bool),
        adder("points_possible"),
        adder("position"),
        adder("published", False, typ=bool),
        adder("quiz_lti"),
        adder("submission_types", "none", typ=list),
        adder("turnitin_enabled", False, typ=bool),
        adder("turnitin_settings"),
        adder("vericite_enabled", False, typ=bool)

        return settings


class PageParser:
    def __init__(self, markdown_processor: ResourceExtractor, date_formatter, parser):
        self.markdown_processor = markdown_processor
        self.date_formatter = date_formatter
        self.parser = parser

    def parse_page_settings(self, page_tag):
        settings = {
            "type": "page",
            "title": page_tag["title"],
            "body": "",
        }
        adder = AttributeAdder(settings, page_tag, self.parser)
        adder("editing_roles", "teachers")
        adder("notify_of_update", False, typ=bool)
        adder("published", False, typ=bool)
        adder("front_page", False, typ=bool)
        adder("publish_at", formatter=self.date_formatter)
        return settings

    def parse(self, page_tag):
        page = {
            "type": "page",
            "name": page_tag["title"],
            "settings": self.parse_page_settings(page_tag),
            "resources": []
        }
        contents = get_text_contents(page_tag)
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
            "quiz": QuizParser(self.markdown_processor, group_identifier, self.date_formatter,parser),
            "assignment": AssignmentParser(self.markdown_processor, group_identifier, self.date_formatter, parser),
            "page": PageParser(self.markdown_processor, self.date_formatter, parser),
            "module": ModuleParser(parser),
            "override": OverrideParser(self.date_formatter, parser)
        }

    def parse(self, text):
        soup = BeautifulSoup(text, "html.parser")
        document = []
        tag: Tag
        for tag in soup.children:
            parser = self.element_processors.get(tag.name, None)
            if parser:
                templates = parser.parse(tag)
                if not isinstance(templates, list):
                    templates = [templates]
                templates = [order_elements(template) for template in templates]
        return document

