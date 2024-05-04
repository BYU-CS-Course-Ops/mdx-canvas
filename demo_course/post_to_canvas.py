import argparse

from pathlib import Path
from mdxcanvas import post_document, get_course
import json
import os
from dotenv import load_dotenv


def main(api_url, api_token, course_id, time_zone: str, file_path: Path):
    print("-" * 50 + "\nCanvas Generator\n" + "-" * 50)

    post_document(get_course(api_url, api_token, course_id), time_zone, file_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=Path)
    parser.add_argument("--env", type=Path, default=".env")
    parser.add_argument("--course-info", type=Path, default="testing_course_info.json")
    args = parser.parse_args()

    load_dotenv(args.env)
    with open(args.course_info) as f:
        course_settings = json.load(f)

    main(api_url=course_settings["CANVAS_API_URL"],
         api_token=os.getenv("CANVAS_API_TOKEN"),
         course_id=course_settings["CANVAS_COURSE_ID"],
         time_zone=course_settings["LOCAL_TIME_ZONE"],
         file_path=args.filename)
