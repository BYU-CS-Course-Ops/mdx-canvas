import argparse
import importlib
import os
import pathlib

import update_canvas as updater

from canvasapi.quiz import Quiz
from canvasapi.course import Course

from datetime import datetime

import markdown as md
import re
from pathlib import Path
from bs4 import BeautifulSoup

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
    files_folder = Path("")
    course = None
    quiz: Quiz = None
    false_regex = ""
    true_regex = ""

    def __init__(self, course: Course, files_folder: Path, false_regex='', true_regex=''):
        self.files_folder = files_folder
        self.course = course
        self.false_regex = false_regex
        self.true_regex = true_regex

    def create_quiz(self, title: str, description: str, time_limit: int, shuffle_answers: bool, access_code: str,
                    quiz_due_date: datetime, published: bool):
        self.quiz = self.course.create_quiz(quiz={
            "title": title,
            "description": self.get_fancy_html(description),
            "quiz_type": "assignment",
            "time_limit": time_limit,
            "shuffle_answers": shuffle_answers,
            "access_code": access_code,
            "due_at": datetime.isoformat(quiz_due_date),
            "published": published
        })

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
        file_object_id = folder_object.upload(self.files_folder / image_name)[1]["id"]
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
    def regex_create_true_false_series(self, preamble: str, questions: list[str]):
        """
        :param preamble: The common text to the series of true/false questions
        :param questions: A list of the markdown files with the questions, names formatted to match the regex if False
        """
        if self.true_regex:
            is_true_tuples = [(question, re.match(self.true_regex, question) != []) for question in questions]
        elif self.false_regex:
            is_true_tuples = [(question, re.match(self.false_regex, question) == []) for question in questions]
        else:
            raise Exception("No regexes defined")
        self.create_true_false_series(preamble, is_true_tuples)

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
        print("Created true/false question: " + description)

    @delete_if_exception
    def regex_create_true_false_question(self, description: str):
        """
        :param description: The file with the question, name formatted to match the regex
        """
        if self.true_regex:
            is_true = re.findall(self.true_regex, description) != []
        elif self.false_regex:
            is_true = re.findall(self.false_regex, description) == []
        else:
            raise Exception("No regexes defined")
        self.create_true_false_question(description, is_true)

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
    def regex_create_multiple_answers_question(self, description: str, answers: list[str]):
        """
        :param description: The file with the question
        :param answers: The list of answer filenames, names formatted to match the regex
        """
        if self.true_regex:
            is_true_indexes = [i for i, answer in enumerate(answers) if re.findall(self.true_regex, answer) != []]
        elif self.false_regex:
            is_true_indexes = [i for i, answer in enumerate(answers) if re.findall(self.false_regex, answer) == []]
        else:
            raise Exception("No regexes defined")
        self.create_multiple_answers_question(description, answers, is_true_indexes)

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
    def regex_create_multiple_choice_question(self, description: str, answers: list[str]):
        """
        :param description: The file with the question
        :param answers: The list of answer filenames, names formatted to match the regex
        """
        if self.true_regex:
            is_true_indexes = [i for i, answer in enumerate(answers) if re.findall(self.true_regex, answer) != []]
        elif self.false_regex:
            is_true_indexes = [i for i, answer in enumerate(answers) if re.findall(self.false_regex, answer) == []]
        else:
            raise Exception("No regexes defined")
        # Assert there is exactly one correct answer for a multiple choice question
        if __debug__:
            if not len(is_true_indexes) == 1: raise AssertionError
        self.create_multiple_choice_question(description, answers, is_true_indexes[0])

    @delete_if_exception
    def create_text_question(self, file_with_text):
        self.quiz.create_question(question={
            "question_text": self.get_fancy_html(file_with_text),
            "question_type": 'text_only_question'
        })
        print("Created text question for " + file_with_text)



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
    for quiz_question in quiz_to_copy.get_questions():
        quiz_question.delete()
    for quiz_question in quiz_to_copy.get_questions():
        answers = []
        for answer in quiz_question.answers:
            new_answer = {}
            for key, value in answer.items():
                if key in answer_mapping:
                    new_answer[answer_mapping[key]] = value
            answers.append(new_answer)

        quiz_to_copy.create_question(question={
            "question_name": quiz_question.question_name,
            "question_text": quiz_question.question_text,
            "question_type": quiz_question.question_type,
            "points_possible": quiz_question.points_possible,
            "answers": answers
        })
    print(quiz_to_edit)
    print(quiz_to_copy)


def create_clone_delete_edit(quiz_script: str, package:str, clone=None, delete=None, edit=None):
    # Use the quiz script to create a quiz and get the quiz object
    # The main function in quiz script returns a quiz object

    canvas = updater.get_canvas_from_secrets()
    course = updater.get_course_via_prompt(canvas)

    # If cloning, we don't need to create a new quiz. Just get the quiz object, and then clone it
    if clone:
        return updater.prompt_to_clone_quiz(course)

    if delete:
        return updater.delete_quizzes(course)

    # Else we need to run the create_quiz function from the quiz script
    quiz = importlib.import_module(quiz_script.strip("."), package=package).create_quiz(course)

    if quiz_from_canvas := updater.get_quiz(course, quiz.title):
        updater.update_quiz(quiz_from_canvas, quiz)
        print("Updated quiz " + quiz.title)
        return

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


if __name__ == '__main__':
    # Parse arguments for quiz creation, cloning, editing, or deletion
    # Quiz script is the only required argument
    parser = argparse.ArgumentParser(description='Create, clone, delete, or edit quizzes.')
    # Create, clone, and edit require a quiz script, but delete does not
    parser.add_argument('quiz_script', nargs='?', help='Path to quiz script')
    parser.add_argument('--clone', action='store_true', help='Clone quizzes')
    parser.add_argument('--delete', action='store_true', help='Delete quizzes')
    parser.add_argument('--edit', action='store_true', help='Edit quizzes')
    args = parser.parse_args()

    if args.quiz_script is None:
        args.quiz_script = get_quiz_path()

    # Assert that the quiz script exists
    elif not os.path.exists(args.quiz_script): raise AssertionError

    create_clone_delete_edit(args.quiz_script, str(Path(__file__).parent.parent), args.clone, args.delete, args.edit)
