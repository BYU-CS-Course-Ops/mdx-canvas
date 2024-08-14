import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import TypedDict

from canvasapi import Canvas
from canvasapi.course import Course

from .deploy.canvas_deploy import deploy_to_canvas
from .resources import CanvasResource
from .xml_processing import process_xml
from .markdown_processing import process_markdown
from .jinja_processing import process_jinja


class CourseInfo(TypedDict):
    CANVAS_API_URL: str
    CANVAS_COURSE_ID: int
    LOCAL_TIME_ZONE: str


def read_content(input_file: Path) -> tuple[list[str], str]:
    return input_file.suffixes, input_file.read_text()


def is_jinja(content_type):
    return content_type[-1] == 'jinja'


def process_file(
        input_file: Path,
        tmpdir: Path,
        args_file: Path = None,
        global_args_file: Path = None,
        line_id: str = None,
        css_file: Path = None
) -> dict[str, CanvasResource]:
    content_type, content = read_content(input_file)

    if is_jinja(content_type):
        if args_file is None:
            raise Exception('--args-file is required if input file is .jinja')
        content = process_jinja(
            content,
            args_path=args_file,
            global_args_path=global_args_file,
            line_id=line_id
        )

    # Process Markdown
    excluded = ['pre']
    xml_content = process_markdown(content, excluded=excluded)

    # Process XML
    global_css = css_file.read_text() if css_file is not None else ''
    resources = process_xml(input_file.parent, xml_content, global_css)

    return resources


def get_course(api_token: str, api_url: str, canvas_course_id: int) -> Course:
    """
    Returns a Canvas Course object for the given API URL, API token, and course ID.

    :param api_url: str: The URL for the Canvas API.
    :param api_token: str: The authentication token for the Canvas API.
    :param canvas_course_id: int: The ID of the Canvas course.
    :return: Course: A Canvas Course object.
    """
    canvas = Canvas(api_url, api_token)
    course: Course = canvas.get_course(canvas_course_id)
    return course


def main(
        canvas_api_token: str,
        course_info: CourseInfo,
        input_file: Path,
        args_file: Path = None,
        global_args_file: Path = None,
        line_id: str = None,
        css_file: Path = None,
):
    # Make sure the course actually exists before doing any real effort
    course = get_course(canvas_api_token, course_info['CANVAS_API_URL'], course_info['CANVAS_COURSE_ID'])

    with tempfile.TemporaryDirectory() as tmpdirname:
        tmpdir = Path(tmpdirname)

        # Load file
        resources = process_file(input_file, tmpdir, args_file, global_args_file, line_id, css_file)

        # Deploy
        deploy_to_canvas(course, course_info['LOCAL_TIME_ZONE'], resources)


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

    main(
        canvas_api_token=api_token,
        course_info=course_settings,
        input_file=args.filename,
        args_file=args.args,
        global_args_file=args.global_args,
        line_id=args.id,
        css_file=args.css
    )


if __name__ == '__main__':
    sys.argv = [
        'main.py',
        '../scratch/simple-quiz.canvas.md.xml',
        '--course-info',
        '../demo_course/testing_course_info.json'
    ]
    entry()
