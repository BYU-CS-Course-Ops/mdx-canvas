import os
import pathlib
import re

import update_canvas as updater

from canvasapi.quiz import Quiz
from canvasapi.course import Course

from datetime import datetime

import markdown as md
from pathlib import Path
from bs4 import BeautifulSoup

LOOKUP_FOLDER = './markdown-quiz-files'

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


def readfile(filepath: Path):
    with open(filepath) as file:
        return file.read()


class QuizCreator:
    markdown = ""
    image_folder = Path(__file__).parent / "images"
    files_folder = Path(__file__).parent / "markdown-quiz-files"
    course = None
    quiz: Quiz = None

    def __init__(self, course: Course, markdown: str, image_folder: Path = None, files_folder: Path = None):
        self.markdown = markdown
        self.image_folder = image_folder if image_folder else self.image_folder
        self.files_folder = files_folder if files_folder else self.image_folder
        self.course = course

    def create_quiz(self, title: str, description: str = "", quiz_type: str = "assignment",
                    assignment_group: str = None,
                    time_limit: int = None, shuffle_answers: bool = True, points_possible: int = 40,
                    due_at: datetime = None, show_correct_answers_at: datetime = None, allowed_attempts: int = 1,
                    scoring_policy: str = "keep_highest", one_question_at_a_time: bool = False,
                    cant_go_back: bool = False,
                    access_code: str = None, available_to: datetime = None, available_from: datetime = None,
                    published: bool = True,
                    one_time_results: bool = False):

        self.quiz = self.course.create_quiz(quiz={
            "title": title,
            "description": self.get_fancy_html(description),
            "quiz_type": quiz_type,
            "assignment_group_id": self.get_group_index(assignment_group),
            "time_limit": time_limit,
            "shuffle_answers": shuffle_answers,
            "hide_results": None,
            "show_correct_answers": True,
            "show_correct_answers_at": self.make_iso(show_correct_answers_at),
            "allowed_attempts": allowed_attempts,
            "scoring_policy": scoring_policy,
            "one_question_at_a_time": one_question_at_a_time,
            "cant_go_back": cant_go_back,
            "access_code": access_code,
            "due_at": self.make_iso(due_at),
            "lock_at": self.make_iso(available_to),
            "unlock_at": self.make_iso(available_from),
            "published": published,
            "one_time_results": one_time_results
        })

    def make_iso(self, date: datetime | str | None):
        input_format = "%b %d, %Y, %I:%M %p"

        if date is None:
            return None
        if isinstance(date, str):
            date = datetime.strptime(date, input_format)
        return datetime.isoformat(date)

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
    def delete_if_exception(function):
        def wrapper(self, *args, **kwargs):
            try:
                function(self, *args, **kwargs)
            except Exception as e:
                print(e)
                self.quiz.delete()
                raise e

        return wrapper

    def get_img_html(self, image_name, alt_text):
        folders = self.course.get_folders()
        if not any(f.name == "Generated-Quizzes" for f in folders):
            print("Created Quizzes Folder")
            self.course.create_folder(name="Generated-Quizzes", parent_folder_path="", hidden=True)

        if not any(f.name == self.quiz.title for f in folders):
            print(f"Created {self.quiz.title} folder")
            folder_object = self.course.create_folder(name=self.quiz.title, parent_folder_path="Generated-Quizzes",
                                                      hidden=True)
        else:
            folder_object = [f for f in folders if f.name == self.quiz.title][0]
        file_object_id = folder_object.upload(self.image_folder / image_name)[1]["id"]
        html_text = f'<p><img id="{image_name}" src="/courses/{self.course.id}/files/{file_object_id}/preview" alt="{alt_text}" /></p>'
        return html_text

    def get_fancy_html(self, markdown_or_file: str):
        if markdown_or_file.endswith('.md'):
            text = readfile(self.files_folder / markdown_or_file)

            html = md.markdown(text, extensions=['fenced_code'])
            soup = BeautifulSoup(html, "html.parser")
            for img in soup.find_all('img'):
                basic_image_html = self.get_img_html(img["src"], img["alt"])
                img.replace_with(BeautifulSoup(basic_image_html, "html.parser"))
            html = str(soup)

            return html
        else:
            return md.markdown(markdown_or_file, extensions=['fenced_code'])

    @delete_if_exception
    def create_matching_question(self, description: str, matches: list[tuple[str, str]], distractors: list[str] = []):
        """
        :param description: The question text
        :param matches: A list of tuples of the form (answer_left, answer_right)
        :param distractors: A list of distractors, strings that are not in the list of matches
        """
        self.quiz.create_question(question={
            "question_name": description,
            "question_text": self.get_fancy_html(description),
            "question_type": 'matching_question',
            "answers": [
                {
                    "answer_match_left": answer_left,
                    "answer_match_right": answer_right,
                } for answer_left, answer_right in matches
            ],
            "matching_answer_incorrect_matches": '\n'.join(distractors)
        })
        print(f"Created matching question: {description}")

    @delete_if_exception
    def create_true_false_series(self, preamble: str, questions: list[tuple[str, bool]]):
        """
        :param preamble: The common text to the series of true/false questions
        :param questions: A list of tuples of the form (description, is_true)
        """
        self.quiz.create_question(question={
            "question_name": preamble,
            "question_text": self.get_fancy_html(preamble),
            "question_type": 'text_only_question'
        })
        for file, is_true in questions:
            self.create_true_false_question(file, is_true)

    @delete_if_exception
    def create_true_false_question(self, description: str, is_true: bool):
        """
        :param description: The file with the question
        :param is_true: True if the answer is true, False if the answer is false
        """
        self.quiz.create_question(question={
            "question_name": description,
            "question_text": self.get_fancy_html(description),
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
        })
        print(f"Created true/false question which is {is_true}: {description}")

    @delete_if_exception
    def create_multiple_answers_question(self, description: str, answers: list[str], correct_answers: list[int]):
        """
        :param description: The file with the question
        :param answers: The list of answers, files or strings
        :param correct_answers: The list of indices of the correct answers
        """
        self.quiz.create_question(question={
            "question_name": description,
            "question_text": self.get_fancy_html(description),
            "question_type": 'multiple_answers_question',
            "points_possible": 1,
            "answers": [
                {
                    "answer_html": self.get_fancy_html(answer),
                    "answer_weight": 100 if i in correct_answers else 0
                } for i, answer in enumerate(answers)
            ]
        })
        print("Created multiple-answers question: " + description)

    @delete_if_exception
    def create_multiple_choice_question(self, description: str, answers: list[str], correct_answer: int):
        """
        :param description: The file with the question
        :param answers: The list of answers, files or strings
        :param correct_answer: The index of the correct answer
        """
        self.quiz.create_question(question={
            "question_name": description,
            "question_text": self.get_fancy_html(description),
            "question_type": 'multiple_choice_question',
            "points_possible": 1,
            "answers": [
                {
                    "answer_html": self.get_fancy_html(answer),
                    "answer_weight": 100 if i == correct_answer else 0
                } for i, answer in enumerate(answers)
            ]
        })
        print("Created multiple-choice question: " + description)

    @delete_if_exception
    def create_text_question(self, file_or_text):
        self.quiz.create_question(question={
            "question_text": self.get_fancy_html(file_or_text),
            "question_type": 'text_only_question'
        })
        print("Created text question for " + file_or_text)


answer_mapping = {
    "text": "answer_text",
    "left": "answer_match_left",
    "right": "answer_match_right",
    "comments": "answer_comments",
    "comments_html": "answer_comments_html",
    "html": "answer_html",
    "weight": "answer_weight",
}


def update_quiz(quiz_to_edit: Quiz, quiz_to_copy: Quiz):
    for quiz_question in quiz_to_edit.get_questions():
        quiz_question.delete()
    quiz_to_edit.edit(quiz={
        "title": quiz_to_copy.title,
        "description": quiz_to_copy.description,
        "quiz_type": quiz_to_copy.quiz_type,
        "time_limit": quiz_to_copy.time_limit,
        "shuffle_answers": quiz_to_copy.shuffle_answers,
        "access_code": quiz_to_copy.access_code,
        "due_at": quiz_to_copy.due_at,
        "published": quiz_to_copy.published,
        "questions": quiz_to_copy.get_questions()
    })
    questions_to_copy = quiz_to_copy.get_questions()
    

    for quiz_question in questions_to_copy:
        answers = []
        for answer in quiz_question.answers:
            new_answer = {}
            for key, value in answer.items():
                if key in answer_mapping:
                    new_answer[answer_mapping[key]] = value
            answers.append(new_answer)

        quiz_to_edit.create_question(question={
            "question_name": quiz_question.question_name,
            "question_text": quiz_question.question_text,
            "question_type": quiz_question.question_type,
            "points_possible": quiz_question.points_possible,
            "answers": answers
        })
    quiz_to_copy.delete()
    print("Updated quiz " + quiz_to_edit.title
          + " by copying from " + quiz_to_copy.title)


class Parser:
    def __init__(self, creator: QuizCreator, text: str):
        self.creator = creator
        self.text = text
        self.settings = {}
        self.instructions = ""
        self.questions = []

    def parse_quiz(self):
        soup = BeautifulSoup(self.text, "html.parser")

        settings = soup.find("settings")
        if settings:
            # settings are stored as attributes in the settings tag
            self.settings = dict(settings.attrs)
            self.instructions = settings.string

        questions = soup.find_all('question')
        index = 1

        for question in questions:
            new_question = {}
            rights = question.css.filter('right')
            wrongs = question.css.filter('wrong')

            # question_processor.process(question)
            #
            # processor = get_quiz_processor[question["type"]]
            # processor.process(question)

            if question["type"] == "multiple-choice":
                new_question["function"] = QuizCreator.create_multiple_choice_question
                new_question["args"] = [
                    question.contents[0],
                    [answer.string for answer in rights + wrongs],
                    rights[0]
                ]
            elif question["type"] == "multiple-answers":
                new_question["function"] = QuizCreator.create_multiple_answers_question
                new_question["args"] = [
                    question.contents[0],
                    [answer.string for answer in rights + wrongs],
                    [range(len(rights))]
                ]
            elif question["type"] == "true-false":
                new_question["function"] = QuizCreator.create_true_false_question
                new_question["args"] = [
                    question.contents[0],
                    rights[0] == "true"
                ]
            elif question["type"] == "multiple-tf":
                new_question["function"] = QuizCreator.create_true_false_series
                new_question["args"] = [
                    question.contents[0],
                    [(right.string, True) for right in rights] + [(wrong.string, False) for wrong in wrongs]
                ]
            elif question["type"] == "text":
                new_question["function"] = QuizCreator.create_text_question
                new_question["args"] = [question.string]

            self.questions.append(new_question)
            index += 1

    def create_quiz(self):
        self.settings["description"] = self.instructions
        self.creator.create_quiz(**self.settings)
        for question in self.questions:
            print(*question["args"])
            question["function"](self.creator, *question["args"])
        return self.creator.quiz


def create_edit(course: Course, quiz_markdown: str):
    creator = QuizCreator(course, quiz_markdown)
    parser = Parser(creator, quiz_markdown)
    parser.parse_quiz()

    if quiz_from_canvas := updater.get_quiz(course, parser.settings['title']):
        update_quiz(quiz_from_canvas, parser.create_quiz())
        print("Updated quiz " + quiz_from_canvas.title)
        return
        # quiz_from_canvas.delete()
        # print("Deleted quiz " + quiz_from_canvas.title)

    quiz = parser.create_quiz()
    print("Created quiz " + quiz.title)


def get_quiz_path():
    path = pathlib.Path(__file__).parent / "markdown-quiz-files"
    while os.path.isdir(path):
        files = os.listdir(path)
        for i, f in enumerate(files):
            print(f"{i}: {f}")
        index = input("Select file: ")
        try:
            index = int(index)
            path = path / files[index]
        except Exception:
            print(f"Enter a number in the range {len(files)}")
    return str(path)


if __name__ == "__main__":
    # Post all the .md (markdown) files inside the [markdown-quiz-files] folder
    print("-" * 50 + "\nCanvas Quiz Generator\n" + "-" * 50)

    canvas = updater.get_canvas_from_secrets()
    course = updater.get_course_via_prompt(canvas)

    for file_name in os.listdir(LOOKUP_FOLDER):
        if file_name.endswith('.md'):
            with open(os.path.join(LOOKUP_FOLDER, file_name), "r") as f:
                print(f"Posting to Canvas ({file_name}) ...")
                create_edit(course, f.read())
