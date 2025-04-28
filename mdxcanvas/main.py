import argparse
import json
import logging
import os
from pathlib import Path
from typing import TypedDict

from canvasapi import Canvas
from canvasapi.course import Course

from .deploy.canvas_deploy import deploy_to_canvas
from .deploy.file import get_canvas_folder, get_file
from .deploy.groups import deploy_group_weights
from .our_logging import get_logger
from .resources import ResourceManager
from .text_processing.jinja_processing import process_jinja
from .text_processing.markdown_processing import process_markdown
from .util import parse_soup_from_xml
from .xml_processing.inline_styling import bake_css
from .xml_processing.xml_processing import process_canvas_xml, preprocess_xml
from .generate_result import MDXCanvasResult

logger = get_logger()


class CourseInfo(TypedDict):
    CANVAS_API_URL: str
    CANVAS_COURSE_ID: int
    COURSE_NAME: str
    COURSE_CODE: str
    COURSE_IMAGE: Path
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
        global_args: dict = None,
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
            global_args=global_args,
            line_id=line_id
        )

    if '.md' in content_type:
        # Process Markdown
        excluded = ['pre', 'style', 'distractors']
        inline = ['a', 'strong', 'em', 'span', 'file', 'link', 'zip', 'course-link']
        xml_content = process_markdown(content, excluded=excluded, inline=inline)

    else:
        xml_content = content

    # Preprocess XML
    def load_and_process_file_contents(parent: Path, content: str, content_type: list[str], **kwargs) -> str:
        return process_file(resources, parent, content, content_type, global_args=global_args, **kwargs)

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

    # NB: this is a hack, but it makes things MUCH easier down the line when dealing with announcements
    course.canvas = canvas

    return course


def update_course_image(course: Course, course_settings: dict, course_image: Path):
    """
    Updates the course image with the given image file.

    :param course: Course: The Canvas Course object to update.
    :param course_settings: dict: The settings for the course.
    :param course_image: Path: The path to the new course image.
    """
    image_name = course_image.name

    if (file := get_file(course, image_name)) is None:
        logger.info(f'Uploading course image {image_name}')
        folder = get_canvas_folder(course, 'course image')
        response = folder.upload(course_image, name=image_name)
        file_id = response[1]['id']
    else:
        file_id = file.id

    if int(course_settings['image_id']) != file_id:
        logger.info(f'Updating course image to {image_name}')
        course.update(course={'image_id': file_id})


def update_course(course: Course, course_info: CourseInfo):
    """
    Updates the course with the given information.

    :param course: Course: The Canvas Course object to update.
    :param course_info: CourseInfo: The information to update the course with.
    """
    if (course_name := course_info.get('COURSE_NAME')) and course.name != course_name:
        logger.info(f'Updating course name to {course_name}')
        course.update(course={'name': course_name})

    if (course_code := course_info.get('COURSE_CODE')) and course.course_code != course_code:
        logger.info(f'Updating course code to {course_code}')
        course.update(course={'course_code': course_code})

    if course_image := course_info.get('COURSE_IMAGE'):
        update_course_image(course, course.get_settings(), Path(course_image))


def main(
        canvas_api_token: str,
        course_info: CourseInfo,
        input_file: Path,
        args_file: Path = None,
        global_args_file: Path = None,
        line_id: str = None,
        css_file: Path = None,
        dryrun: bool = False,
        output_file: str = None
):
    # Make sure the course actually exists before doing any real effort
    course = get_course(canvas_api_token, course_info['CANVAS_API_URL'], course_info['CANVAS_COURSE_ID'])
    logger = get_logger(course.name)
    logger.info('Connecting to Canvas')

    result = MDXCanvasResult(output_file)

    if global_args_file:
        with open(global_args_file) as f:
            global_args = json.load(f)

        group_weights = global_args.get('group_weights', None)
        if group_weights:
            deploy_group_weights(course, group_weights)
    else:
        global_args = None

    update_course(course, course_info)

    resources = ResourceManager()

    # Load file
    logger.info('Reading file: ' + str(input_file))
    content_type, content = read_content(input_file)
    processed_content = process_file(
        resources,
        input_file.parent,
        content,
        content_type,
        global_args,
        args_file,
        line_id,
        css_file
    )

    # Parse file into XML
    resources = process_canvas_xml(resources, processed_content)

    # Deploy XML
    logger.info('Deploying to Canvas')
    deploy_to_canvas(course, course_info['LOCAL_TIME_ZONE'], resources, result, dryrun=dryrun)

    result.output()


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
    parser.add_argument('--dryrun', '--dry-run', action='store_true')
    parser.add_argument('--output-file', type=str, default=None)
    args = parser.parse_args()

    with open(args.course_info) as f:
        course_settings = json.load(f)

    api_token = os.environ.get("CANVAS_API_TOKEN")
    if api_token is None:
        raise ValueError("Please set the CANVAS_API_TOKEN environment variable")

    if args.debug:
        logger.setLevel(logging.DEBUG)

    main(
        canvas_api_token=api_token,
        course_info=course_settings,
        input_file=args.filename,
        args_file=args.args,
        global_args_file=args.global_args,
        line_id=args.id,
        css_file=args.css,
        dryrun=args.dryrun,
        output_file=args.output_file
    )


if __name__ == '__main__':
    entry()
