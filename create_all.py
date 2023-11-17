import argparse

from pathlib import Path
from canvas_creator import load_env, create_elements_from_document
from canvasapi import Canvas
from canvasapi.course import Course
import json
import os


def main(api_token, api_url, course_id, time_zone: str, folder: Path):
    print("-" * 50 + "\nCanvas Generator\n" + "-" * 50)

    canvas = Canvas(api_url, api_token)
    course: Course = canvas.get_course(course_id)
    for file_path in folder.iterdir():
        if file_path.is_dir():
            continue
        print(f"Posting to Canvas ({file_path}) ...")
        create_elements_from_document(course, time_zone, file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--folder", type=Path)
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
         folder=args.folder)