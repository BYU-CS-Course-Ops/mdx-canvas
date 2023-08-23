import json
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

from parser import Parser

LOOKUP_FOLDER = './markdown-quiz-files'
JSON_FOLDER = './json-quiz-files'

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



def get_fancy_html(markdown_or_file: str, files_folder=None):
    if markdown_or_file.endswith('.md'):
        text = readfile(files_folder / markdown_or_file)

        html = md.markdown(text, extensions=['fenced_code'])
        return html
    else:
        return md.markdown(markdown_or_file, extensions=['fenced_code'])

def get_img_html(image_name, alt_text, course: Course, quiz_title: str, image_folder):
    folders = course.get_folders()
    if not any(f.name == "Generated-Quizzes" for f in folders):
        print("Created Quizzes Folder")
        course.create_folder(name="Generated-Quizzes", parent_folder_path="", hidden=True)

    if not any(f.name == quiz_title for f in folders):
        print(f"Created {quiz_title} folder")
        folder_object = course.create_folder(name=quiz_title, parent_folder_path="Generated-Quizzes",
                                             hidden=True)
    else:
        folder_object = [f for f in folders if f.name == quiz_title][0]
    file_object_id = folder_object.upload(image_folder / image_name)[1]["id"]
    html_text = f'<p><img id="{image_name}" src="/courses/{course.id}/files/{file_object_id}/preview" alt="{alt_text}" /></p>'
    return html_text


def link_images_in_canvas(html, quiz, files_folder):
    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all('img'):
        basic_image_html = get_img_html(img["src"], img["alt"], course, quiz, files_folder)
        img.replace_with(BeautifulSoup(basic_image_html, "html.parser"))
    html = str(soup)
    return html


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







    def create_matching_question(self, description: str, matches: list[tuple[str, str]], distractors: list[str] = []):
        """
        :param description: The question text
        :param matches: A list of tuples of the form (answer_left, answer_right)
        :param distractors: A list of distractors, strings that are not in the list of matches
        """
        self.quiz.create_question(question={
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
    print(f"\nUpdated quiz {quiz_to_edit.title} by copying from {quiz_to_copy.title}")


def create_quiz(quiz: dict, course: Course):
    settings = quiz["settings"]
    canvas_quiz = course.create_quiz(quiz=settings)
    for question in quiz["questions"]:
        print(question)
        try:
            canvas_quiz.create_question(question=question)
        except Exception as e:
            print(e)
            canvas_quiz.delete()
            raise e
    return canvas_quiz


def delete_others(course:Course, quiz_from_canvas):
    for quiz in course.get_quizzes():
        if quiz.title == quiz_from_canvas.title and quiz.id != quiz_from_canvas.id:
            quiz.delete()
            print("Deleted quiz " + quiz.title)


def create_edit(course: Course, quiz_markdown: str, json_folder):
    parser = Parser(quiz_markdown, course)
    document_object = parser.parse_document()

    for quiz_json in document_object:
        quiz_name = quiz_json["settings"]["title"]
        with open(json_folder / f"{quiz_name}.json", "w") as f:
            json.dump(quiz_json, f, indent=4)
        print(f"Creating quiz {quiz_name} ...")
        if quiz_from_canvas := updater.get_quiz(course, quiz_name):
            delete_others(course, quiz_from_canvas)
            quiz = create_quiz(quiz_json, course)
            update_quiz(quiz_from_canvas, quiz)
            continue

        quiz = create_quiz(quiz_json, course)
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
                create_edit(course, f.read(), Path(JSON_FOLDER))
