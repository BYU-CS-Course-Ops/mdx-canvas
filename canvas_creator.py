import json
import os
import textwrap

import uuid
import argparse

from canvasapi import Canvas
from canvasapi.assignment import Assignment, AssignmentGroup

from canvasapi.quiz import Quiz
from canvasapi.course import Course
from canvasapi.module import Module

import markdown as md
from pathlib import Path
from bs4 import BeautifulSoup

from parser import DocumentParser, make_iso


def load_env(file_name):
    """
    Loads all environment variables from a file.
    """
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
    """
    Converts markdown to html, and adds syntax highlighting to code blocks.
    """
    if markdown_or_file.endswith('.md'):
        markdown_or_file = readfile(files_folder / markdown_or_file)

    dedented = textwrap.dedent(markdown_or_file)
    fenced = md.markdown(dedented, extensions=['fenced_code'])
    return fenced


def print_red(string):
    print(f"\033[91m{string}\033[00m")


def get_canvas_folder(course: Course, folder_name: str, parent_folder_path=""):
    """
    Retrieves an object representing a digital folder in Canvas. If the folder does not exist, it is created.
    """
    folders = list(course.get_folders())
    if not any(f.name == folder_name for f in folders):
        print(f"Created {folder_name} folder")
        course.create_folder(name=folder_name, parent_folder_path=parent_folder_path, hidden=True)
    return [f for f in folders if f.name == folder_name][0]


def create_resource_folder(course, quiz_title: str, course_folders):
    """
    Creates a folder in Canvas to store images and other resources.
    """
    generated_folder_name = "Generated-Content"
    if not any(f.name == generated_folder_name for f in course_folders):
        print("Created Content Folder")
        course.create_folder(name=generated_folder_name, parent_folder_path="", hidden=True)

    if not any(f.name == quiz_title for f in course_folders):
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
    """
    Converts markdown to html, and adds syntax highlighting to code blocks.
    Then, finds all the images in the html, and replaces them with html that links to the image in Canvas.
    """
    html = get_fancy_html(markdown_or_file, files_folder)
    return process_images(html, course, image_folder)


def get_group_id(course: Course, group_name: str, names_to_ids: dict[str, int]):
    """
    Group ids are numbers that stand for groups like Labs, Projects, etc.
    Since users will provide names for groups, this method is necessary to find ids.
    """
    if not group_name:
        return None

    if group_name not in names_to_ids:
        print("Created Assignment Group: " + group_name)
        course.create_assignment_group(name=group_name)
        for g in course.get_assignment_groups():
            if g.name not in names_to_ids:
                names_to_ids[g.name] = g.id

    return names_to_ids[group_name]


def replace_questions(quiz: Quiz, questions: list[dict]):
    """
    Deletes all questions in a quiz, and replaces them with new questions.
    """
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
    print_red(f"Could not find page {page_name}")
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


def get_module(course: Course, module_name: str):
    modules = course.get_modules()
    for module in modules:
        if module.name == module_name:
            return module
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


def get_module_item(module: Module, item_name):
    module_items = module.get_module_items()
    for item in module_items:
        if item.title == item_name:
            return item
    return None


def get_object_id_from_element(course: Course, item):
    if item["type"] == "Quiz":
        if not (quiz := get_quiz(course, item["title"])):
            return None
        return quiz.id
    elif item["type"] == "Assignment":
        if not (assignment := get_assignment(course, item["title"])):
            return None
        return assignment.id
    elif item["type"] == "Page":
        page_url = get_page_url(course, item["title"])
        item["page_url"] = page_url


def fix_dates(element, time_zone):
    if "due_at" in element:
        element["due_at"] = make_iso(element["due_at"], time_zone)
    if "unlock_at" in element:
        element["unlock_at"] = make_iso(element["unlock_at"], time_zone)
    if "lock_at" in element:
        element["lock_at"] = make_iso(element["lock_at"], time_zone)


def create_or_edit_assignment(course, element):
    name = element["name"]
    if canvas_assignment := get_assignment(course, name):
        print(f"Editing canvas assignment {name} ...  ", end="")
        canvas_assignment.edit(assignment=element["settings"])
    else:
        print(f"Creating canvas assignment {name} ...  ", end="")
        course.create_assignment(assignment=element["settings"])
    print("Done")
    return canvas_assignment


def create_or_edit_quiz(course, element):
    name = element["name"]
    if canvas_quiz := get_quiz(course, name):
        print(f"Editing canvas quiz {name} ...  ", end="")
        canvas_quiz.edit(quiz=element["settings"])
    else:
        print(f"Creating canvas quiz {name} ...  ", end="")
        canvas_quiz = course.create_quiz(quiz=element["settings"])
    replace_questions(canvas_quiz, element["questions"])
    print("Done")
    return canvas_quiz


def upload_and_link_files(document_object, course, resources: list[tuple], course_folders):
    """
    Uploads all the files in the resources list, and replaces the fake ids in the document with the real ids.
    """
    create_resource_folder(course, document_object["name"], course_folders)
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


def create_or_edit_module_item(module: Module, element, object_id, position):
    """
    Creates a module item with an object id, like an assignment or a quiz.
    """
    element["position"] = position
    if not object_id:
        create_or_edit_module_item_without_id(module, element)
    else:
        create_or_edit_module_item_with_id(module, element, object_id)


def create_or_edit_module_item_with_id(module: Module, element, object_id):
    """
    Create module item if it doesn't exist, otherwise edit it.
    """
    element["content_id"] = object_id
    if module_item := get_module_item(module, element["title"]):
        print(f"Editing module item {element['title']} in module {module.name} ...  ", end="")
        module_item.edit(module_item=element)
    else:
        print(f"Creating module item {element['title']} in module {module.name} ...  ", end="")
        module.create_module_item(module_item=element)
    print("Done")


def create_or_edit_module_item_without_id(module: Module, element):
    """
    Creates a module item without an object id, like a page or a header.
    """
    if element["type"] not in ["ExternalUrl", "SubHeader", "Page"]:
        print_red(f"{element['title']} does not exist, no id found when creating module.")
        return

    for item in module.get_module_items():
        if item.title == element["title"]:
            print(f"Editing module item {element['title']} in module {module.name} ...  ", end="")
            item.edit(module_item=element)
            print("Done")
            return

    if element["type"] == "Page" and not element["page_url"]:
        print(f"Could not find page url for {element['title']}")
        return

    print(f"Creating module item {element['title']} in module {module.name} ...  ", end="")
    module.create_module_item(module_item=element)
    print("Done")


def delete_module_items_from_element(canvas_module, element):
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
    delete_module_items_from_element(canvas_module, element)
    for index, item in enumerate(element["items"]):
        object_id = get_object_id_from_element(course, item)
        create_or_edit_module_item(canvas_module, item, object_id, index + 1)


def create_or_update_module(course, element):
    name = element["name"]
    if canvas_module := get_module(course, name):
        print(f"Editing canvas module {name} ...  ", end="")
        canvas_module.edit(module=element["settings"])
    else:
        print(f"Creating canvas module {name} ...  ", end="")
        canvas_module = course.create_module(module=element["settings"])
    print()
    create_or_update_module_items(course, element, canvas_module)
    return canvas_module


def get_assignment_override_pairs(course, overrides):
    """
    Searches for canvas assignments with names that match the override names.
    """
    assignments = course.get_assignments()
    pairs = []
    for assignment in assignments:
        for override in overrides:
            if assignment.name == override["title"]:
                pairs.append((assignment, override))
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
            print(f"Editing override {override['title']} ...  ", end="")
            canvas_override.edit(assignment_override=override)
        else:
            print(f"Creating override {override['title']} ...  ", end="")
            assignment.create_override(assignment_override=override)
        print("Done")


def create_or_update_override(course, override, time_zone):
    students = override["students"]
    sections = override["sections"]
    section_ids = get_section_ids(course, sections)
    assignment_names = [a['title'] for a in override["assignments"]]

    assignment_override_pairs = get_assignment_override_pairs(course, override["assignments"])
    if not assignment_override_pairs:
        print_red(f"Could not find {assignment_names} in canvas for override {override['sections']}")
        return
    if not students and not sections:
        raise ValueError("Must provide either students or sections")

    for assignment, override in assignment_override_pairs:
        fix_dates(override, time_zone)
        create_or_update_override_for_assignment(assignment, override, students, sections, section_ids)


def get_section_ids(course, names):
    sections = course.get_sections()
    sections = [s.id for s in sections if s.name in names]
    if not sections:
        raise ValueError(f"Could not find sections {sections}")
    return sections


def create_or_edit_page(course: Course, element):
    name = element["name"]
    if canvas_page := get_page(course, name):
        print(f"Editing canvas page {name} ...  ", end="")
        canvas_page.edit(wiki_page=element["settings"])
    else:
        print(f"Creating canvas page {name} ...  ", end="")
        canvas_page = course.create_page(wiki_page=element["settings"])
    print("Done")
    return canvas_page


def create_elements_from_document(course: Course, time_zone: str, file_path: Path):
    if "canvas" not in file_path.__str__():
        print_red("Error: File must be a canvas file")
        return

    assignment_groups = list(course.get_assignment_groups())
    names_to_ids = {g.name: g.id for g in assignment_groups}

    # Provide processing functions, so that the parser needs no access to a canvas course
    parser = DocumentParser(
        path_to_resources=file_path.parent,
        path_to_canvas_files=file_path.parent,
        markdown_processor=lambda text: process_markdown(text, course, file_path.parent),
        time_zone=time_zone,
        group_identifier=lambda group_name: get_group_id(course, group_name, names_to_ids),
    )
    document_object = parser.parse(file_path.read_text())

    course_folders = list(course.get_folders())

    # Create multiple quizzes or assignments from the document object
    for element in document_object:
        if "resources" in element:
            element = upload_and_link_files(element, course, element["resources"], course_folders)
        if "settings" in element:
            fix_dates(element["settings"], time_zone)
        if element["type"] == "quiz":
            create_or_edit_quiz(course, element)
        elif element["type"] == "assignment":
            create_or_edit_assignment(course, element)
        elif element["type"] == "page":
            create_or_edit_page(course, element)
        elif element["type"] == "module":
            create_or_update_module(course, element)
        elif element["type"] == "override":
            create_or_update_override(course, element, time_zone)
        else:
            raise ValueError(f"Unknown type {element['type']}")


def main(api_token, api_url, course_id, time_zone: str, file_path: Path):
    print("-" * 50 + "\nCanvas Generator\n" + "-" * 50)

    canvas = Canvas(api_url, api_token)
    course: Course = canvas.get_course(course_id)

    print(f"Parsing file ({file_path}) ...  ", end="")
    create_elements_from_document(course, time_zone, file_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file_path", type=Path)
    parser.add_argument("--resources", type=Path)
    parser.add_argument("--env", type=Path, default="secrets.env")
    parser.add_argument("--course_info", type=Path, default="course_info.json")
    args = parser.parse_args()

    load_env(args.env)
    with open(args.course_info) as f:
        course_settings = json.load(f)

    # " -0600" is Mountain Time
    main(api_token=os.getenv("CANVAS_API_TOKEN"),
         api_url=course_settings["CANVAS_API_URL"],
         course_id=course_settings["CANVAS_COURSE_ID"],
         time_zone=course_settings["CANVAS_TIME_ZONE"],
         file_path=args.file_path)
