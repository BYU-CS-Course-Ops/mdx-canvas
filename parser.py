from bs4 import BeautifulSoup
import markdown as md
from pathlib import Path
from datetime import datetime


def readfile(filepath: Path):
    with open(filepath) as file:
        return file.read()


def get_rights_and_wrongs(question_tag):
    rights = question_tag.css.filter('right')
    wrongs = question_tag.css.filter('wrong')
    return rights, wrongs


def get_answers(question_tag):
    rights, wrongs = get_rights_and_wrongs(question_tag)
    return rights + wrongs


def get_fancy_html(markdown_or_file: str, files_folder=None):
    if markdown_or_file.endswith('.md'):
        text = readfile(files_folder / markdown_or_file)

        html = md.markdown(text, extensions=['fenced_code'])
        return html
    else:
        return md.markdown(markdown_or_file, extensions=['fenced_code'])


class TFConverter:
    def process(self, right_wrong_tag):
        is_true = right_wrong_tag.name == "right"
        question = {
            "question_text": get_fancy_html(right_wrong_tag.contents[0]),
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
        return question


class TrueFalseProcessor:
    def process(self, question_tag):
        answers = get_answers(question_tag)
        if len(answers) != 1:
            raise Exception("True false questions must have one right or wrong answer")

        return TFConverter().process(answers[0])


class MultipleTrueFalseProcessor:
    def process(self, question_tag):
        questions = [
            TextProcessor().process(question_tag)
        ]
        for answer in get_answers(question_tag):
            questions.append(TFConverter().process(answer))
        return questions


class MultipleChoiceProcessor:
    def process(self, question_tag):
        rights, wrongs = get_rights_and_wrongs(question_tag)
        if len(rights) != 1:
            raise Exception("Multiple choice questions must have exactly one right answer")

        question = {
            "question_text": get_fancy_html(question_tag.contents[0]),
            "question_type": 'multiple_choice_question',
            "points_possible": 1,
            "answers": [
                {
                    "answer_text": answer.string,
                    "answer_weight": 100 if answer in rights else 0
                } for answer in rights + wrongs
            ]
        }
        return question


class MultipleAnswersProcessor:
    def process(self, question_tag):
        rights, wrongs = get_rights_and_wrongs(question_tag)
        question = {
            "question_text": get_fancy_html(question_tag.contents[0]),
            "question_type": 'multiple_answers_question',
            "points_possible": 1,
            "answers": [
                {
                    "answer_text": answer.string,
                    "answer_weight": 100 if answer in rights else 0
                } for answer in rights + wrongs
            ]
        }
        return question


class MatchingProcessor:
    def process(self, question_tag):
        lefts = question_tag.css.filter('left')
        rights = question_tag.css.filter('right')
        if len(lefts) < len(rights):
            raise Exception("Matching questions must have at least as many lefts as rights")
        matches = zip(lefts, rights)
        distractors = rights[len(lefts):]
        question = {
            "question_text": get_fancy_html(question_tag.contents[0]),
            "question_type": 'matching_question',
            "points_possible": 1,
            "answers": [
                {
                    "answer_match_left": answer_left.string,
                    "answer_match_right": answer_right.string,
                    "answer_weight": 100
                } for answer_left, answer_right in matches
            ],
            "matching_answer_incorrect_matches": '\n'.join(distractors)
        }
        return question


class TextProcessor:
    def process(self, question_tag):
        question = {
            "question_text": get_fancy_html(question_tag.contents[0]),
            "question_type": 'text_only_question',
        }
        return question


question_processors = {
    "multiple-choice": MultipleChoiceProcessor(),
    "multiple-answers": MultipleAnswersProcessor(),
    "true-false": TrueFalseProcessor(),
    "multiple-tf": MultipleTrueFalseProcessor(),
    "matching": MatchingProcessor(),
    "text": TextProcessor()
}


class Parser:
    def __init__(self, text: str, course):
        self.text = text
        self.course = course
        self.settings = {}
        self.instructions = ""
        self.questions = []

    def parse_document(self):
        soup = BeautifulSoup(self.text, "html.parser")
        document = []
        for tag in soup.children:
            if tag.name == "quiz":
                document.append(self.parse_quiz(tag))
        return document

    def parse_quiz(self, quiz_tag):
        quiz = {"questions": []}
        for tag in quiz_tag.children:
            if tag.name == "settings":
                quiz["settings"] = self.parse_settings(tag)
            elif tag.name == "question":
                question = self.parse_question(tag)
                # if question is a  list of questions, add them all
                if isinstance(question, list):
                    quiz["questions"].extend(question)
                else:
                    quiz["questions"].append(question)
        return quiz

    def get_group_index(self, group: str):
        groups = self.course.get_assignment_groups()
        group_index = 0
        if group:
            if not any(g.name == group for g in groups):
                print("Created Assignment Group: " + group)
                self.course.create_assignment_group(name=group)
            group_index = [g.name for g in groups].index(group)
        return group_index

    @staticmethod
    def make_iso(date: datetime | str | None):
        input_format = "%b %d, %Y, %I:%M %p"

        if date is None:
            return None
        if isinstance(date, str):
            date = datetime.strptime(date, input_format)
        return datetime.isoformat(date)

    def parse_settings(self, settings_tag):
        settings = {
            "title": settings_tag["title"],
            "quiz_type": settings_tag.get("quiz_type", "assignment"),
            "assignment_group_id": self.get_group_index(settings_tag.get("assignment_group", None)),
            "time_limit": settings_tag.get("time_limit", None),
            "shuffle_answers": settings_tag.get("shuffle_answers", False),
            "hide_results": None,
            "show_correct_answers": True,
            "show_correct_answers_at": self.make_iso(settings_tag.get("show_correct_answers_at", None)),
            "allowed_attempts": settings_tag.get("allowed_attempts", 1),
            "scoring_policy": settings_tag.get("scoring_policy", "keep_highest"),
            "one_question_at_a_time": settings_tag.get("one_question_at_a_time", False),
            "cant_go_back": settings_tag.get("cant_go_back", False),
            "access_code": settings_tag.get("access_code", None),
            "due_at": self.make_iso(settings_tag.get("due_at", None)),
            "lock_at": self.make_iso(settings_tag.get("available_to", None)),
            "unlock_at": self.make_iso(settings_tag.get("available_from", None)),
            "published": settings_tag.get("published", True),
            "one_time_results": settings_tag.get("one_time_results", False),
        }
        return settings

    def parse_question(self, question_tag):
        processor = question_processors[question_tag["type"]]
        return processor.process(question_tag)
