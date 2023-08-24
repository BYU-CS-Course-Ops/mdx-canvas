import json
import os

import update_canvas as updater

from canvasapi.quiz import Quiz
from canvasapi.course import Course

import markdown as md
from pathlib import Path
from bs4 import BeautifulSoup

from parser import Parser

LOOKUP_FOLDER = './markdown-quiz-files'
JSON_FOLDER = './json-quiz-files'
IMAGE_FOLDER = './images'

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


def get_canvas_folder(course: Course, folder_name: str, parent_folder_path=""):
    folders = course.get_folders()
    if not any(f.name == folder_name for f in folders):
        print(f"Created {folder_name} folder")
        course.create_folder(name=folder_name, parent_folder_path=parent_folder_path, hidden=True)
    return [f for f in folders if f.name == folder_name][0]


def get_img_html(image_name, alt_text, course, quiz_title: str, image_folder):
    get_canvas_folder(course, "Generated-Quizzes")
    quiz_folder = get_canvas_folder(course, quiz_title, "Generated-Quizzes")

    file_object_id = quiz_folder.upload(image_folder / image_name)[1]["id"]
    html_text = f'<p><img id="{image_name}" src="/courses/{course.id}/files/{file_object_id}/preview" alt="{alt_text}" /></p>'
    return html_text


def link_images_in_canvas(html, quiz_title: str, course: Course, image_folder):
    soup = BeautifulSoup(html, "html.parser")
    matches = soup.find_all('img')
    for img in matches:
        basic_image_html = get_img_html(img["src"], img["alt"], course, quiz_title, image_folder)
        img.replace_with(BeautifulSoup(basic_image_html, "html.parser"))
    html = str(soup)
    return html


def get_html_and_link_images(markdown_or_file: str, quiz_title: str, course: Course, image_folder, files_folder=None, ):
    html = get_fancy_html(markdown_or_file, files_folder)
    html = link_images_in_canvas(html, quiz_title, course, image_folder)
    return html


def get_group_index(course: Course, group: str):
    groups = course.get_assignment_groups()
    group_index = 0
    if group:
        if not any(g.name == group for g in groups):
            print("Created Assignment Group: " + group)
            course.create_assignment_group(name=group)
        group_index = [g.name for g in groups].index(group)
    return group_index


def create_quiz_in_canvas(quiz: dict, course: Course):
    settings = quiz["settings"]
    canvas_quiz = course.create_quiz(quiz=settings)
    replace_questions(canvas_quiz, quiz["questions"])
    print(f"Created quiz {canvas_quiz.title}")


def replace_questions(quiz: Quiz, questions: list[dict]):
    for quiz_question in quiz.get_questions():
        quiz_question.delete()
    for question in questions:
        quiz.create_question(question=question)


def delete_others(course: Course, quiz_from_canvas):
    for quiz in course.get_quizzes():
        if quiz.title == quiz_from_canvas.title and quiz.id != quiz_from_canvas.id:
            quiz.delete()
            print("Deleted quiz " + quiz.title)


def create_or_edit_quiz(course, quiz):
    quiz_name = quiz["settings"]["title"]
    print(f"Creating quiz {quiz_name} ...")
    if quiz_from_canvas := updater.get_quiz(course, quiz_name):
        delete_others(course, quiz_from_canvas)
        quiz_from_canvas.edit(quiz=quiz["settings"])
        replace_questions(quiz_from_canvas, quiz["questions"])
    else:
        create_quiz_in_canvas(quiz, course)


def save_quiz_to_json(quiz, json_folder):
    json_string = json.dumps(quiz, indent=4)
    with open(json_folder / f"{quiz['settings']['title']}.json", "w") as f:
        f.write(json_string)


def create_quizzes_from_document(course: Course, quiz_markdown: str, document_name, json_folder):
    # Provide processing functions, so that the parser needs no access to a canvas course
    parser = Parser(
        html_processor=lambda text: get_html_and_link_images(text, document_name, course, Path(IMAGE_FOLDER)),
        group_indexer=lambda group_name: get_group_index(course, group_name)
    )
    document_object = parser.parse_document(quiz_markdown)

    for quiz_object in document_object:
        save_quiz_to_json(quiz_object, json_folder)
        create_or_edit_quiz(course, quiz_object)


if __name__ == "__main__":
    # Post all the .md (markdown) files inside the [markdown-quiz-files] folder
    print("-" * 50 + "\nCanvas Quiz Generator\n" + "-" * 50)

    canvas = updater.get_canvas_from_secrets()
    canvas_course = updater.get_course_via_prompt(canvas)

    for file_name in os.listdir(LOOKUP_FOLDER):
        if file_name.endswith('.md'):
            with open(os.path.join(LOOKUP_FOLDER, file_name), "r") as document:
                print(f"Posting to Canvas ({file_name}) ...")
                create_quizzes_from_document(canvas_course, document.read(), file_name, Path(JSON_FOLDER))
