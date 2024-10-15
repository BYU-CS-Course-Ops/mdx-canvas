import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import TypedDict

from canvasapi import Canvas
from canvasapi.course import Course

from mdxcanvas.xml_processing.inline_styling import bake_css
from mdxcanvas.util import parse_soup_from_xml
from .deploy.canvas_deploy import deploy_to_canvas
from .resources import ResourceManager
from .xml_processing.xml_processing import process_canvas_xml, preprocess_xml
from mdxcanvas.text_processing.markdown_processing import process_markdown
from mdxcanvas.text_processing.jinja_processing import process_jinja


class CourseInfo(TypedDict):
    CANVAS_API_URL: str
    CANVAS_COURSE_ID: int
    LOCAL_TIME_ZONE: str


def read_content(input_file: Path) -> tuple[list[str], str]:
    return input_file.suffixes, input_file.read_text()


def is_jinja(content_type):
    return content_type[-1] == '.jinja'


def _post_process_content(xml_content: str, global_css: str) -> str:
    # - bake in CSS styles
    soup = parse_soup_from_xml(xml_content)
    xml_postprocessors = [
        lambda s: bake_css(s, global_css)
    ]
    for xml_post in xml_postprocessors:
        soup = xml_post(soup)

    return str(soup)


def process_file(
        resources: ResourceManager,
        parent_folder: Path,
        content: str,
        content_type: list[str],
        global_args_file: Path = None,
        args_file: Path = None,
        line_id: str = None,
        css_file: Path = None
) -> str:
    """
    Read a file and fully process the text content
    Process Markdown.
    Process content-modifying XML tags (e.g. img, or file, or zip, or include)
    Post-process the content (whole XML in, whole XML out, e.g. bake CSS)
    """
    if is_jinja(content_type):
        content = process_jinja(
            content,
            args_path=args_file,
            global_args_path=global_args_file,
            line_id=line_id
        )

    # Process Markdown
    excluded = ['pre', 'style']

    logging.info('Processing Markdown')
    xml_content = process_markdown(content, excluded=excluded)

    # Preprocess XML
    logging.info('Processing XML')

    def load_and_process_file_contents(parent: Path, content: str, content_type: list[str], **kwargs) -> str:
        return process_file(resources, parent, content, content_type, global_args_file=global_args_file, **kwargs)

    xml_content = preprocess_xml(parent_folder, xml_content, resources, load_and_process_file_contents)

    # Post-process the XML
    global_css = css_file.read_text() if css_file is not None else ''
    return _post_process_content(xml_content, global_css)


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
    logging.info('Connecting to Canvas')
    course = get_course(canvas_api_token, course_info['CANVAS_API_URL'], course_info['CANVAS_COURSE_ID'])

    resources = ResourceManager()

    # Load file
    logging.info('Reading file: ' + str(input_file))
    content_type, content = read_content(input_file)
    processed_content = process_file(
        resources,
        input_file.parent,
        content,
        content_type,
        global_args_file,
        args_file,
        line_id,
        css_file
    )

    # Parse file into XML
    resources = process_canvas_xml(resources, processed_content)

    # Deploy XML
    logging.info('Deploying to Canvas')
    deploy_to_canvas(course, course_info['LOCAL_TIME_ZONE'], resources)


def entry():
    parser = argparse.ArgumentParser()
    # Time zone identifiers: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    # Use the time zone of the canvas course
    parser.add_argument("--course-info", type=Path, default="canvas_course_info.json")
    parser.add_argument("filename", type=Path)
    parser.add_argument("--args", type=Path, default=None)
    parser.add_argument("--global-args", type=Path, default=None)
    parser.add_argument("--id", type=str, default=None)
    parser.add_argument("--css", type=Path, default=None)
    parser.add_argument('--debug', action='store_true')
    args = parser.parse_args()

    with open(args.course_info) as f:
        course_settings = json.load(f)

    api_token = os.environ.get("CANVAS_API_TOKEN")
    if api_token is None:
        raise ValueError("Please set the CANVAS_API_TOKEN environment variable")

    logger = logging.getLogger('logger')
    logger.setLevel(logging.INFO)
    if args.debug:
        logger.setLevel(logging.DEBUG)

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
        '../scratch/sample-content.canvas.md.xml',
        '--course-info',
        '../demo_course/testing_course_info.json'
    ]

    # sys.argv = [
    #     'main.py',
    #     '../scratch/sample-template.canvas.md.xml.jinja',
    #     '--args',
    #     '../scratch/sample-template.args.md',
    #     '--course-info',
    #     '../demo_course/testing_course_info.json'
    # ]

    entry()
