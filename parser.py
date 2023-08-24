from typing import Callable, Union

from bs4 import BeautifulSoup
from datetime import datetime
from bs4.element import Tag
from typing import Protocol


def get_corrects_and_incorrects(question_tag):
    corrects = question_tag.css.filter('correct')
    incorrects = question_tag.css.filter('incorrect')
    return corrects, incorrects


def get_answers(question_tag):
    corrects, incorrects = get_corrects_and_incorrects(question_tag)
    return corrects + incorrects


def make_iso(date: datetime | str | None):
    input_format = "%b %d, %Y, %I:%M %p"

    if date is None:
        return None
    if isinstance(date, str):
        date = datetime.strptime(date, input_format)
    return datetime.isoformat(date)


class TFConverter:
    @staticmethod
    def process(correct_incorrect_tag, markdown_processor: Callable[[str], tuple[str, list]]):
        is_true = correct_incorrect_tag.name == "correct"
        question_text, resources = markdown_processor(correct_incorrect_tag.contents[0])
        question = {
            "question_text": question_text,
            "question_type": 'true_false_question',
            "points_possible": 1,
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
    def process(question_tag, markdown_processor: Callable[[str], tuple[str, list]]) -> Union[tuple[list[dict], list], tuple[dict, list]]:
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
            "points_possible": 1,
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
            "points_possible": 1,
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
            "questions": [],
            "resources": [],
        }
        for tag in quiz_tag.find_all():
            if tag.name == "settings":
                quiz["settings"] = self.parse_quiz_settings(tag)
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


class DocumentParser:
    def __init__(self, path_to_resources, markdown_processor: Callable[[str], tuple[str, list]],
                 group_indexer=lambda x: 0):
        self.path_to_resources = path_to_resources
        self.markdown_processor = markdown_processor
        self.element_processors = {
            "quiz": QuizParser(self.markdown_processor, group_indexer),
        }

    def parse(self, text):
        soup = BeautifulSoup(text, "html.parser")
        document = []
        for tag in soup.find_all():
            parser = self.element_processors.get(tag.name, None)
            if parser:
                element = parser.parse(tag)
                if isinstance(element, list):
                    document.extend(element)
                else:
                    document.append(element)
        return document
