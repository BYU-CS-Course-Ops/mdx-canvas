import argparse

from pathlib import Path
from .canvas_creator import post_document, get_course
import json
import os


def main(api_url, api_token, course_id, time_zone: str,
         file_path: Path, args_path: Path, global_args_path: Path, line_id: str,
         css_path: Path):
    print("-" * 50 + "\nCanvas MDX\n" + "-" * 50)

    post_document(get_course(api_url, api_token, course_id), time_zone,
                  file_path, args_path, global_args_path, line_id,
                  css_path)


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-info", type=Path, default="canvas_course_info.json")
    parser.add_argument("filename", type=Path)
    parser.add_argument("--args", type=Path, default=None)
    parser.add_argument("--global-args", type=Path, default=None)
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--css", type=Path, default=None)
    args = parser.parse_args()

    with open(args.course_info) as f:
        course_settings = json.load(f)

    api_token = os.environ.get("CANVAS_API_TOKEN")
    if api_token is None:
        raise ValueError("Please set the CANVAS_API_TOKEN environment variable")

    main(api_url=course_settings["CANVAS_API_URL"],
         api_token=api_token,
         course_id=course_settings["CANVAS_COURSE_ID"],
         time_zone=course_settings["LOCAL_TIME_ZONE"],
         file_path=args.filename,
         args_path=args.args,
         global_args_path=args.global_args,
         line_id=args.id,
         css_path=args.css
         )


if __name__ == '__main__':
    entry()
