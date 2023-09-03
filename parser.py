import pandas as pandas
from typing import Callable, Union

from bs4 import BeautifulSoup
from datetime import datetime
from bs4.element import Tag
from typing import Protocol


def get_corrects_and_incorrects(question_tag):
    corrects = question_tag.css.filter('correct')
    incorrects = question_tag.css.filter('incorrect')
    return corrects, incorrects


def get_points(question_tag):
    points = question_tag.css.filter('points')
    return points[0].contents[0].strip() if len(points) > 0 else 1


def get_answers(question_tag):
    corrects, incorrects = get_corrects_and_incorrects(question_tag)
    return corrects + incorrects


def make_iso(date: datetime | str | None):
    input_format = "%b %d, %Y, %I:%M %p"

    if date is None:
        return None
    if isinstance(date, str):
        # For templating
        if date.startswith("{"):
            return date
        date = datetime.strptime(date, input_format)
    return datetime.isoformat(date)


def parse_template_data(template_tag):
    """
    Parses a template tag into a list of dictionaries
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
    lines = template_tag.contents[0].strip().split('\n')
    # Grab the headers from the table, removing whitespace and empty headers
    headers = lines[0].split('|')
    headers = [h.strip() for h in headers if h.strip()]
    # The lines with data start at index 2, after the header and the separator
    for line in lines[2:]:
        line = line.split('|')
        # Splitting on | leaves empty strings at the beginning and end
        line = [l.strip() for l in line][1:-1]
        data.append(dict(zip(headers, line)))
    return data


class TFConverter:
    @staticmethod
    def process(correct_incorrect_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        is_true = correct_incorrect_tag.name == "correct"
        question_text, resources = markdown_processor(correct_incorrect_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'true_false_question',
            "points_possible": get_points(correct_incorrect_tag),
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
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]) -> Union[
        tuple[list[dict], list], tuple[dict, list]]:
        ...


def process(processor: Processor, question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
    question, resources = processor.process(question_tag, markdown_processor)
    return question, resources


class TrueFalseProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        answers = get_answers(question_tag)
        if len(answers) != 1:
            raise Exception("True false questions must have one correct or incorrect answer")

        return process(TFConverter(), answers[0], markdown_processor)


class MultipleTrueFalseProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        heading_question, resources = process(TextQuestionProcessor(), question_tag, markdown_processor)
        questions = [heading_question]
        for answer in get_answers(question_tag):
            tf_question, res = process(TFConverter(), answer, markdown_processor)
            questions.append(tf_question)
            resources.extend(res)
        return questions, resources


class MultipleChoiceProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        corrects, incorrects = get_corrects_and_incorrects(question_tag)
        if len(corrects) != 1:
            raise Exception("Multiple choice questions must have exactly one correct answer")

        return process(MultipleAnswersProcessor(), question_tag, markdown_processor)


class MultipleAnswersProcessor:
    @staticmethod
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        corrects, incorrects = get_corrects_and_incorrects(question_tag)

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
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        pairs = question_tag.css.filter('pair')
        matches = []
        for pair in pairs:
            answer_left, answer_right = pair.css.filter('left')[0], pair.css.filter('right')[0]
            matches.append((answer_left.string.strip(), answer_right.string.strip()))

        for match in matches:
            print(match)

        distractors = question_tag.css.filter('distractors')
        distractor_text = distractors[0].contents[0].strip() if len(distractors) > 0 else None
        question_text, resources = markdown_processor(question_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'matching_question',
            "points_possible": get_points(question_tag),
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
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        question_text, resources = markdown_processor(question_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'text_only_question',
        }
        return question, resources


class OverrideParser:
    def __init__(self):
        pass

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
            elif tag.name == "assignments":
                lines = tag.contents[0].strip().split('\n')
                override["assignments"] = [l.strip() for l in lines if l.strip()]
        return override


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
                "published": module_tag.get("published", True),
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
            "new_tab": tag.get("new_tab", True),
            "completion_requirement": tag.get("completion_requirement", None),
            "iframe": tag.get("iframe", None),
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

    def __init__(self, markdown_processor: Callable[[str], tuple[str, list]], group_indexer):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer

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
            "show_correct_answers": True,
            "show_correct_answers_at": make_iso(settings_tag.get("show_correct_answers_at", None)),
            "allowed_attempts": settings_tag.get("allowed_attempts", 1),
            "scoring_policy": settings_tag.get("scoring_policy", "keep_highest"),
            "one_question_at_a_time": settings_tag.get("one_question_at_a_time", False),
            "cant_go_back": settings_tag.get("cant_go_back", False),
            "access_code": settings_tag.get("access_code", None),
            "due_at": make_iso(settings_tag.get("due_at", None)),
            "lock_at": make_iso(settings_tag.get("available_to", None)),
            "unlock_at": make_iso(settings_tag.get("available_from", None)),
            "published": settings_tag.get("published", True),
            "one_time_results": settings_tag.get("one_time_results", False),
        }
        return settings

    def parse_question(self, question_tag: Tag):
        processor = self.question_processors[question_tag["type"]]
        return processor.process(question_tag, self.markdown_processor)


class AssignmentParser:
    def __init__(self, markdown_processor: Callable[[str], tuple[str, list]], group_indexer):
        self.markdown_processor = markdown_processor
        self.group_indexer = group_indexer

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
                contents = "".join([str(c) for c in tag.contents])
                description, res = self.markdown_processor(contents)
                assignment["settings"]["description"] = description
                assignment["resources"].extend(res)

        assignment["name"] = assignment["settings"]["name"]
        return assignment

    def parse_assignment_settings(self, settings_tag):
        settings = {
            "name": settings_tag["name"],
            "position": settings_tag.get("position", None),
            "submission_types": settings_tag.get("submission_types", ["none"]),
            "allowed_extensions": settings_tag.get("allowed_extensions", []),
            "turnitin_enabled": settings_tag.get("turnitin_enabled", False),
            "vericite_enabled": settings_tag.get("vericite_enabled", False),
            "turnitin_settings": settings_tag.get("turnitin_settings", None),
            "integration_data": settings_tag.get("integration_data", None),
            "peer_reviews": settings_tag.get("peer_reviews", False),
            "automatic_peer_reviews": settings_tag.get("automatic_peer_reviews", False),
            "notify_of_update": settings_tag.get("notify_of_update", False),
            "group_category_id": settings_tag.get("group_category", None),
            "grade_group_students_individually": settings_tag.get("grade_group_students_individually", False),
            "external_tool_tag_attributes": settings_tag.get("external_tool_tag_attributes", None),
            "points_possible": settings_tag.get("points_possible", None),
            "grading_type": settings_tag.get("grading_type", "points"),
            "due_at": make_iso(settings_tag.get("due_at", None)),
            "lock_at": make_iso(settings_tag.get("available_to", None)),
            "unlock_at": make_iso(settings_tag.get("available_from", None)),
            "assignment_group_id": self.group_indexer(settings_tag.get("assignment_group", None)),
            "assignment_overrides": settings_tag.get("assignment_overrides", None),
            "only_visible_to_overrides": settings_tag.get("only_visible_to_overrides", False),
            "published": settings_tag.get("published", True),
            "grading_standard_id": settings_tag.get("grading_standard_id", None),
            "omit_from_final_grade": settings_tag.get("omit_from_final_grade", False),
            "hide_in_gradebook": settings_tag.get("hide_in_gradebook", False),
            "quiz_lti": settings_tag.get("quiz_lti", None),
            "moderated_grading": settings_tag.get("moderated_grading", False),
            "grader_count": settings_tag.get("grader_count", None),
            "final_grader_id": settings_tag.get("final_grader_id", None),
            "grader_comments_visible_to_graders": settings_tag.get("grader_comments_visible_to_graders", False),
            "graders_anonymous_to_graders": settings_tag.get("graders_anonymous_to_graders", False),
            "grader_names_visible_to_final_grader": settings_tag.get("grader_names_visible_to_final_grader", False),
            "anonymous_grading": settings_tag.get("anonymous_grading", False),
            "allowed_attempts": settings_tag.get("allowed_attempts", 1),
            "annotatable_attachment_id": settings_tag.get("annotatable_attachment_id", None),
        }
        return settings


class PageParser:
    def __init__(self, markdown_processor: Callable[[str], tuple[str, list]]):
        self.markdown_processor = markdown_processor

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
                "publish_at": make_iso(page_tag.get("publish_at", None)),
            },
            "resources": []
        }
        contents = "".join([str(c) for c in page_tag.contents])
        body, res = self.markdown_processor(contents)
        page["settings"]["body"] = body
        page["resources"].extend(res)
        return page


class DocumentParser:
    def __init__(self, path_to_resources, markdown_processor: Callable[[str], tuple[str, list]],
                 group_indexer=lambda x: 0):
        self.path_to_resources = path_to_resources
        self.markdown_processor = markdown_processor
        self.element_processors = {
            "quiz": QuizParser(self.markdown_processor, group_indexer),
            "assignment": AssignmentParser(self.markdown_processor, group_indexer),
            "page": PageParser(self.markdown_processor),
            "module": ModuleParser(),
            "override": OverrideParser()
        }

    def parse(self, text):
        soup = BeautifulSoup(text, "html.parser")
        document = []
        for tag in soup.children:
            parser = self.element_processors.get(tag.name, None)
            if parser:
                element = parser.parse(tag)
                if isinstance(element, list):
                    document.extend(element)
                else:
                    document.append(element)
        return document
