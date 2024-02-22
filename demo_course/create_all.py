import argparse

from pathlib import Path
from mdxcanvas import post_document, get_course
import json
import os
from dotenv import load_dotenv


def file_sorter(file_path: Path):
    # Modules should be created last,
    # so it can organize the modules after the assignments are created.
    # Other files can be ordered as you desire.
    order = [
        ("header", 2),
        ("syllabus", 3),
        ("project", 4),
        ("lab", 5),
        ("homework", 10),
        ("quiz", 20),
        ("assignment", 30),
        ("Final", 40),
        ("Midterm", 60),
        ("modules", 100),
    ]
    for name, value in order:
        if name.lower() in file_path.name.lower():
            return value

    return 90


def create_for_folder(course, time_zone: str, folder: Path):
    for file_path in sorted(folder.iterdir(), key=file_sorter):
        if file_path.is_dir():
            continue
        print(f"Parsing file ({file_path}) ...  ", end="")
        post_document(course, time_zone, file_path)


def main(api_url, api_token, course_id, time_zone: str, folders: list[Path]):
    print("-" * 50 + "\nCanvas Generator\n" + "-" * 50)

    for folder in folders:
        create_for_folder(get_course(api_url, api_token, course_id), time_zone, folder)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("folders", type=Path, nargs="+", default=[Path.cwd()])
    parser.add_argument("--env", type=Path, default=".env")
    parser.add_argument("--course_info", type=Path, default="testing_course_info.json")
    args = parser.parse_args()

    load_dotenv(args.env)
    with open(args.course_info) as f:
        course_settings = json.load(f)

    main(api_url=course_settings["CANVAS_API_URL"],
         api_token=os.getenv("CANVAS_API_TOKEN"),
         course_id=course_settings["CANVAS_COURSE_ID"],
         time_zone=course_settings["LOCAL_TIME_ZONE"],
         folders=args.folders)

