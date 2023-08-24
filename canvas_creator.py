import json
import os
import textwrap

import uuid
import argparse

from canvasapi import Canvas

from canvasapi.quiz import Quiz
from canvasapi.course import Course

import markdown as md
from pathlib import Path
from bs4 import BeautifulSoup

from parser import DocumentParser

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


def load_env(file_name):
    with open(file_name) as file:
        for line in file:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            key, value = line.split('=')
            os.environ[key] = value


def readfile(filepath: Path):
    with open(filepath) as file:
        return file.read()


def get_fancy_html(markdown_or_file: str, files_folder=None):
    if markdown_or_file.endswith('.md'):
        markdown_or_file = readfile(files_folder / markdown_or_file)

    dedented = textwrap.dedent(markdown_or_file)
    fenced = md.markdown(dedented, extensions=['fenced_code'])
    return fenced

def get_canvas_folder(course: Course, folder_name: str, parent_folder_path=""):
    folders = list(course.get_folders())
    if not any(f.name == folder_name for f in folders):
        print(f"Created {folder_name} folder")
        course.create_folder(name=folder_name, parent_folder_path=parent_folder_path, hidden=True)
    return [f for f in folders if f.name == folder_name][0]


def create_resource_folder(course, quiz_title: str):
    folders = list(course.get_folders())
    generated_folder_name = "Generated-Content"
    if not any(f.name == generated_folder_name for f in folders):
        print("Created Content Folder")
        course.create_folder(name=generated_folder_name, parent_folder_path="", hidden=True)

    if not any(f.name == quiz_title for f in folders):
        print(f"Created {quiz_title} folder")
        course.create_folder(name=quiz_title, parent_folder_path=generated_folder_name,
                                                  hidden=True)

def get_img_html(image_name, alt_text, course, image_folder: Path):
    fake_object_id = str(uuid.uuid4())
    html_text = f'<p><img id="{image_name}" src="/courses/{course.id}/files/{fake_object_id}/preview" alt="{alt_text}" /></p>'
    resource = (fake_object_id, str(image_folder / image_name))
    return html_text, resource


def process_images(html, course: Course, image_folder):
    soup = BeautifulSoup(html, "html.parser")
    matches = soup.find_all('img')
    resources = []
    for img in matches:
        basic_image_html, resource = get_img_html(img["src"], img["alt"], course, image_folder)
        img.replace_with(BeautifulSoup(basic_image_html, "html.parser"))
        resources.append(resource)
    return str(soup), resources


def process_markdown(markdown_or_file: str, course: Course, image_folder, files_folder=None):
    html = get_fancy_html(markdown_or_file, files_folder)
    return process_images(html, course, image_folder)


def get_group_index(course: Course, group: str):
    groups = course.get_assignment_groups()
    group_index = 0
    if group:
        if not any(g.name == group for g in groups):
            print("Created Assignment Group: " + group)
            course.create_assignment_group(name=group)
        group_index = [g.name for g in groups].index(group)
    return group_index


def replace_questions(quiz: Quiz, questions: list[dict]):
    for quiz_question in quiz.get_questions():
        quiz_question.delete()
    for question in questions:
        quiz.create_question(question=question)


def get_quiz(course: Course, title: str):
    quizzes = course.get_quizzes()
    for quiz in quizzes:
        if quiz.title == title:
            return quiz
    return None


def create_or_edit_quiz(course, quiz):
    quiz_name = quiz["settings"]["title"]
    if canvas_quiz := get_quiz(course, quiz_name):
        print(f"Editing quiz {quiz_name} ...")
        canvas_quiz.edit(quiz=quiz["settings"])
    else:
        print(f"Creating quiz {quiz_name} ...")
        canvas_quiz = course.create_quiz(quiz=quiz["settings"])
    replace_questions(canvas_quiz, quiz["questions"])


def save_quiz_to_json(quiz, json_folder):
    json_string = json.dumps(quiz, indent=4)
    with open(json_folder / f"{quiz['settings']['title']}.json", "w") as f:
        f.write(json_string)


def link_resources(document_object, course, resources: list[tuple]):
    create_resource_folder(course, document_object["settings"]["title"])
    text = json.dumps(document_object, indent=4)
    for fake_id, full_path in resources:
        resource_id = str(course.upload(full_path)[1]["id"])
        text = text.replace(fake_id, resource_id)
    return json.loads(text)


def create_elements_from_document(course: Course, quiz_markdown: str, path_to_resources: Path):
    # Provide processing functions, so that the parser needs no access to a canvas course
    parser = DocumentParser(
        path_to_resources=path_to_resources,
        markdown_processor=lambda text: process_markdown(text, course, path_to_resources),
        group_indexer=lambda group_name: get_group_index(course, group_name)
    )
    document_object = parser.parse(quiz_markdown)

    for element in document_object:
        element = link_resources(element, course, element["resources"])
        create_or_edit_quiz(course, element)


def main(api_url, api_token, course_id, file_path: Path, path_to_resources: Path):
    # Post all the .md (markdown) files inside the [markdown-quiz-files] folder
    print("-" * 50 + "\nCanvas Quiz Generator\n" + "-" * 50)

    canvas = Canvas(api_url, api_token)
    course: Course = canvas.get_course(course_id)

    if not file_path.suffix == ".md":
        raise ValueError("File must be a markdown file")

    print(f"Posting to Canvas ({file_path}) ...")
    create_elements_from_document(course, file_path.read_text(), path_to_resources)



if __name__ == "__main__":
    load_env("secrets.env")

    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", type=Path)
    parser.add_argument("--resources", type=Path)
    args = parser.parse_args()

    api_token = os.getenv("CANVAS_API_TOKEN")
    api_url: str = "https://byu.instructure.com/"
    course_id: int = 20736

    main(api_url, api_token, course_id, args.file_path, args.resources)

