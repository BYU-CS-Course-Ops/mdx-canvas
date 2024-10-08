import argparse
import json
import logging
import os
import sys
from pathlib import Path

from canvasapi import exceptions
from canvasapi.paginated_list import PaginatedList

from mdxcanvas.main import CourseInfo
from mdxcanvas.main import get_course

logger = logging.getLogger('mdxcanvas')

def get_item_name(item):
    if hasattr(item, 'title'):
        return item.title
    elif hasattr(item, 'name'):
        return item.name
    elif hasattr(item, 'display_name'):
        return item.display_name
    elif hasattr(item, 'filename'):
        return item.filename
    else:
        return str(item)

def get_item_type(item):
    if hasattr(item, 'is_quiz_assignment'):
        if item.is_quiz_assignment:
            return 'Quiz'
        else:
            return 'Assignment'


def delete_item(item, item_name):
    try:
        item.delete()
    except exceptions.BadRequest as e:
        if "Can't delete the root folder" in str(e):
            logger.info(f'Skipping root folder: {item_name}')
        else:
            logger.warning(f'Failed to delete {item.type}: {item_name}')


def remove(items: PaginatedList, item_type=None):
    for item in items:
        # Conditions to help with the removal of files and folders
        if hasattr(item, 'get_folders'):
            sub_folders = item.get_folders()
            if item.parent_folder_id is None:
                continue
            remove(sub_folders, 'Folder')
        if hasattr(item, 'get_files'):
            files = item.get_files()
            remove(files, 'File')

        if item_type is None:
            item_type = get_item_type(item)
        item_name = get_item_name(item)

        logger.info(f'Deleting {item_type}: {item_name}')
        delete_item(item, item_name)


def main(
        canvas_api_token: str,
        course_info: CourseInfo
):
    logger.info('Connecting to Canvas...')

    course = get_course(canvas_api_token,
                        course_info['CANVAS_API_URL'],
                        course_info['CANVAS_COURSE_ID'])

    assignments = course.get_assignments()
    remove(assignments)

    assignment_groups = course.get_assignment_groups()
    remove(assignment_groups, 'Assignment Group')

    pages = course.get_pages()
    remove(pages, 'Page')

    modules = course.get_modules()
    remove(modules, 'Module')

    files = course.get_folders()
    remove(files, 'Folder')


def entry():
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-info", type=Path)
    parser.add_argument('-y', action='store_true')
    args = parser.parse_args()

    with open(args.course_info) as f:
        course_settings = json.load(f)

    api_token = os.environ.get("CANVAS_API_TOKEN")
    if api_token is None:
        raise ValueError("Please set the CANVAS_API_TOKEN environment variable")

    logger.setLevel(logging.INFO)

    if not args.y:
        confirm = input('Are you sure you want to delete all course content? ([y]/n): ')
        if confirm.lower() != 'y':
            print('Exiting...')
            return

    main(
        canvas_api_token=api_token,
        course_info=course_settings
    )


if __name__ == '__main__':
    sys.argv = [
        'main.py',
        '-y',
        '--course-info',
        '../demo_course/testing_course_info.json'
    ]

    entry()