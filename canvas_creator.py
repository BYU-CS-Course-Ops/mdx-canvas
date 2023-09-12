import json
import os
import textwrap

import uuid
import argparse


from canvasapi import Canvas
from canvasapi.assignment import Assignment

from canvasapi.quiz import Quiz
from canvasapi.course import Course
from canvasapi.module import Module

import markdown as md
from pathlib import Path
from bs4 import BeautifulSoup

from parser import DocumentParser, make_iso


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
    """
    Retrieves an object representing a digital folder in Canvas. If the folder does not exist, it is created.
    """
    folders = list(course.get_folders())
    if not any(f.name == folder_name for f in folders):
        print(f"Created {folder_name} folder")
        course.create_folder(name=folder_name, parent_folder_path=parent_folder_path, hidden=True)
    return [f for f in folders if f.name == folder_name][0]


def create_resource_folder(course, quiz_title: str):
    """
    Creates a folder in Canvas to store images and other resources.
    """
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
    """
    Returns the html for an image, and the path to the resource so it can later be uploaded to Canvas.
    After uploading, the correct resource id must be substituted for the fake id using a text replace.
    """
    fake_object_id = str(uuid.uuid4())
    html_text = f'<p><img id="{image_name}" src="/courses/{course.id}/files/{fake_object_id}/preview" alt="{alt_text}" /></p>'
    resource = (fake_object_id, str(image_folder / image_name))
    return html_text, resource


def process_images(html, course: Course, image_folder):
    """
    Finds all the images in the html, and replaces them with html that links to the image in Canvas.
    Returns the new html, and a list of resources that need to be uploaded.
    After uploading, the correct object id must be substituted for the fake ids, which are returned in the resources.
    """
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
    """
    Group indexes are numbers that stand for groups like Labs, Projects, etc.
    Since users will provide names for groups, this method is necessary to find indexes.
    """
    groups = course.get_assignment_groups()
    if not group:
        return None

    if not any(g.name == group for g in groups):
        print("Created Assignment Group: " + group)
        course.create_assignment_group(name=group)
    groups = course.get_assignment_groups()
    group_index = [g.name for g in groups].index(group)
    return group_index


def replace_questions(quiz: Quiz, questions: list[dict]):
    for quiz_question in quiz.get_questions():
        quiz_question.delete()
    for question in questions:
        quiz.create_question(question=question)


def get_section_id(course: Course, section_name: str):
    sections = course.get_sections()
    for section in sections:
        if section.name == section_name:
            return section.id
    print(f"Valid section names: {[s.name for s in sections]}")
    return None


def get_page_url(course: Course, page_name: str):
    pages = course.get_pages()
    for page in pages:
        if page.title == page_name:
            return page.url
    print(f"Could not find page {page_name}")
    return None


def get_quiz(course: Course, title: str):
    quizzes = course.get_quizzes()
    for quiz in quizzes:
        if quiz.title == title:
            return quiz
    return None


def get_assignment(course: Course, assignment_name):
    assignments = course.get_assignments()
    for assignment in assignments:
        if assignment.name == assignment_name:
            return assignment
    return None


def get_override(assignment: Assignment, override_name):
    overrides = assignment.get_overrides()
    for override in overrides:
        if override.title == override_name:
            return override
    return None


def get_page(course: Course, name):
    pages = course.get_pages()
    for page in pages:
        if page.title == name:
            return page
    return None


def get_module(course: Course, module_name: str):
    modules = course.get_modules()
    for module in modules:
        if module.name == module_name:
            return module
    return None


def get_module_item(module:Module, item_name):
    module_items = list(module.get_module_items())
    for item in module_items:
        if item.title == item_name:
            return item
    return None


def get_object_id_from_element(course: Course, item):
    if item["type"] == "Quiz":
        quiz = get_quiz(course, item["title"])
        if not quiz:
            return None
        return quiz.id
    elif item["type"] == "Assignment":
        assignment = get_assignment(course, item["title"])
        if not assignment:
            return None
        return assignment.id
    elif item["type"] == "Page":
        page_url = get_page_url(course, item["title"])
        item["page_url"] = page_url


def fix_dates(element):
    if "due_at" in element:
        element["due_at"] = make_iso(element["due_at"])
    if "unlock_at" in element:
        element["unlock_at"] = make_iso(element["unlock_at"])
    if "lock_at" in element:
        element["lock_at"] = make_iso(element["lock_at"])


def create_or_edit_assignment(course, element):
    name = element["name"]
    if canvas_assignment := get_assignment(course, name):
        print(f"Editing assignment {name} ...")
        canvas_assignment.edit(assignment=element["settings"])
    else:
        print(f"Creating assignment {name} ...")
        course.create_assignment(assignment=element["settings"])
    return canvas_assignment


def create_or_edit_quiz(course, element):
    name = element["name"]
    if canvas_quiz := get_quiz(course, name):
        print(f"Editing quiz {name} ...")
        canvas_quiz.edit(quiz=element["settings"])
    else:
        print(f"Creating quiz {name} ...")
        canvas_quiz = course.create_quiz(quiz=element["settings"])
    replace_questions(canvas_quiz, element["questions"])
    return canvas_quiz


def upload_and_link_files(document_object, course, resources: list[tuple]):
    create_resource_folder(course, document_object["name"])
    text = json.dumps(document_object, indent=4)
    for fake_id, full_path in resources:
        resource_id = str(course.upload(full_path)[1]["id"])
        text = text.replace(fake_id, resource_id)
    return json.loads(text)


def delete_module_item_if_exists(module, name):
    for item in module.get_module_items():
        if item.title == name:
            print(f"Deleting module item {name} ...")
            item.delete()


def create_or_edit_module_item_without_id(module: Module, element):
    if element["type"] not in ["ExternalUrl", "SubHeader", "Page"]:
        print(f"Could not find object id for {element['title']}")
        return

    for item in module.get_module_items():
        if item.title == element["title"]:
            print(f"Editing module item {element['title']} in module {module.name} ...")
            item.edit(module_item=element)
            return

    if element["type"] == "Page" and not element["page_url"]:
        print(f"Could not find page url for {element['title']}")
        return

    print(f"Creating module item {element['title']} in module {module.name} ...")
    module.create_module_item(module_item=element)


def create_or_edit_module_item(module: Module, element, object_id, position):
    element["position"] = position
    if not object_id:
        create_or_edit_module_item_without_id(module, element)
        return
    # Create module item if it doesn't exist
    element["content_id"] = object_id
    if module_item := get_module_item(module, element["title"]):
        print(f"Editing module item {element['title']} in module {module.name} ...")
        module_item.edit(module_item=element)
    else:
        print(f"Creating module item {element['title']} in module {module.name} ...")
        module.create_module_item(module_item=element)


def delete_other_module_items(canvas_module, element):
    names = []
    for item in element["items"]:
        names.append(item["title"])
    for item in canvas_module.get_module_items():
        if item.title not in names:
            print(f"Deleting module item {item.title} ...")
            item.delete()


def create_or_update_module_items(course: Course, element, canvas_module):
    if "items" not in element:
        return
    delete_other_module_items(canvas_module, element)
    for index, item in enumerate(element["items"]):
        object_id = get_object_id_from_element(course, item)
        create_or_edit_module_item(canvas_module, item, object_id, index + 1)


def create_or_update_module(course, element):
    name = element["name"]
    if canvas_module := get_module(course, name):
        print(f"Editing module {name} ...")
        canvas_module.edit(module=element["settings"])
    else:
        print(f"Creating module {name} ...")
        canvas_module = course.create_module(module=element["settings"])
    create_or_update_module_items(course, element, canvas_module)
    return canvas_module


def get_assignment_override_pair(course, overrides):
    assignments = course.get_assignments()
    names = [o["title"] for o in overrides]
    pairs = []
    for assignment in assignments:
        if assignment.name in names:
            pairs.append((assignment, overrides[names.index(assignment.name)]))
    return pairs


def create_or_update_override_for_assignment(assignment, override, students, sections, section_ids):
    overrides = []
    if students:
        student_override = override.copy()
        student_override["student_ids"] = students
        student_override["title"] = "".join(students)
        overrides.append(student_override)

    for section, id in zip(sections, section_ids):
        section_override = override.copy()
        section_override["title"] = section
        section_override["course_section_id"] = id
        overrides.append(section_override)

    for override in overrides:
        if canvas_override := get_override(assignment, override["title"]):
            print(f"Editing override {override['title']} ...")
            canvas_override.edit(assignment_override=override)
        else:
            print(f"Creating override {override['title']} ...")
            assignment.create_override(assignment_override=override)


def create_or_update_override(course, element):
    students = element["students"]
    sections = element["sections"]
    section_ids = get_section_ids(course, sections)

    assignment_override_pairs = get_assignment_override_pair(course, element["assignments"])
    if not assignment_override_pairs:
        raise ValueError(f"Could not find any of {element['assignments']} in canvas")
    if not students and not sections:
        raise ValueError("Must provide either students or sections")

    for assignment, override in assignment_override_pairs:
        fix_dates(override)
        create_or_update_override_for_assignment(assignment, override, students, sections, section_ids)


def create_student_overrides(course, students):
    for student in students:
        if not course.get_user(student):
            raise ValueError(f"Could not find student {student}")


def get_section_ids(course, names):
    sections = course.get_sections()
    sections = [s.id for s in sections if s.name in names]
    if not sections:
        raise ValueError(f"Could not find sections {sections}")
    return sections


def create_or_edit_page(course: Course, element):
    name = element["name"]
    if canvas_page := get_page(course, name):
        print(f"Editing page {name} ...")
        canvas_page.edit(wiki_page=element["settings"])
    else:
        print(f"Creating page {name} ...")
        canvas_page = course.create_page(wiki_page=element["settings"])
    return canvas_page


def create_elements_from_document(course: Course, quiz_markdown: str, path_to_resources: Path):
    # Provide processing functions, so that the parser needs no access to a canvas course
    parser = DocumentParser(
        path_to_resources=path_to_resources,
        markdown_processor=lambda text: process_markdown(text, course, path_to_resources),
        group_indexer=lambda group_name: get_group_index(course, group_name)
    )
    document_object = parser.parse(quiz_markdown)

    # Create multiple quizzes or assignments from the document object
    for element in document_object:
        if "resources" in element:
            element = upload_and_link_files(element, course, element["resources"])
        if "settings" in element:
            fix_dates(element["settings"])
        if element["type"] == "quiz":
            create_or_edit_quiz(course, element)
        elif element["type"] == "assignment":
            create_or_edit_assignment(course, element)
        elif element["type"] == "page":
            create_or_edit_page(course, element)
        elif element["type"] == "module":
            create_or_update_module(course, element)
        elif element["type"] == "override":
            create_or_update_override(course, element)
        else:
            raise ValueError(f"Unknown type {element['type']}")


def main(api_url, api_token, course_id, file_path: Path, path_to_resources: Path):
    # Post all the .md (markdown) files inside the [markdown-quiz-files] folder
    print("-" * 50 + "\nCanvas Generator\n" + "-" * 50)

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

