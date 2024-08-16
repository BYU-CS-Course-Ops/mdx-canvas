from canvasapi.course import Course
from canvasapi.page import Page

from .util import get_canvas_object, get_canvas_uri


def get_page(course: Course, title: str) -> Page:
    return get_canvas_object(course.get_pages, 'title', title)


def deploy_page(course: Course, page_info: dict) -> str:
    name = page_info['title']

    if canvas_page := get_page(course, name):
        canvas_page.edit(wiki_page=page_info)
    else:
        canvas_page = course.create_page(wiki_page=page_info)

    return get_canvas_uri(canvas_page)


def lookup_page(course: Course, page_title: str) -> str:
    canvas_page = get_page(course, page_title)
    if not canvas_page:
        raise Exception(f'Quiz {page_title} not found')

    return get_canvas_uri(canvas_page)
