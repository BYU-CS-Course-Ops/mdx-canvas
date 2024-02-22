import argparse

from pathlib import Path
from mdxcanvas import post_document
from canvasapi import Canvas
from canvasapi.course import Course
import json
import os


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


def file_sorter(file_path: Path):
    if "modules" in file_path.name.lower():
        return 100  # modules should be last
    elif "Midterm" in file_path.name.lower():
        return 60
    elif "Final" in file_path.name.lower():
        return 40
    elif "assignment" in file_path.name.lower():
        return 30
    elif "quiz" in file_path.name.lower():
        return 20
    elif "homework" in file_path.name.lower():
        return 10
    elif "lab" in file_path.name.lower():
        return 5
    elif "project" in file_path.name.lower():
        return 4
    elif "syllabus" in file_path.name.lower():
        return 3
    elif "header" in file_path.name.lower():
        return 2
    return 90


def create_for_folder(course: Course, time_zone: str, folder: Path):
    for file_path in sorted(folder.iterdir(), key=file_sorter):
        if file_path.is_dir():
            continue
        print(f"Parsing file ({file_path}) ...  ", end="")
        post_document(course, time_zone, file_path)


def main(api_token, api_url, course_id, time_zone: str, folders: list[Path]):
    print("-" * 50 + "\nCanvas Generator\n" + "-" * 50)

    canvas = Canvas(api_url, api_token)
    course: Course = canvas.get_course(course_id)
    for folder in folders:
        create_for_folder(course, time_zone, folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("env", type=Path, default="secrets.env")
    parser.add_argument("course_info", type=Path, default="course_info.json")
    parser.add_argument("folders", type=Path, nargs="+", default=["."])
    args = parser.parse_args()

    load_env(args.env)
    with open(args.course_info) as f:
        course_settings = json.load(f)

    # " -0600" is Mountain Time
    main(api_token=os.getenv("CANVAS_API_TOKEN"),
         api_url=course_settings["CANVAS_API_URL"],
         course_id=course_settings["CANVAS_COURSE_ID"],
         time_zone=course_settings["CANVAS_TIME_ZONE"],
         folders=args.folders)