from canvasapi.course import Course
from canvasapi.page import Page

from .util import get_canvas_object, get_canvas_uri
from ..resources import CanvasObjectInfo


def get_page(course: Course, title: str) -> Page:
    return get_canvas_object(course.get_pages, 'title', title)


def deploy_page(course: Course, page_info: dict) -> tuple[CanvasObjectInfo, None]:
    page_id = page_info["canvas_id"]

    # Remove canvas_id before sending to Canvas API
    update_data = page_info.copy()
    update_data.pop('canvas_id', None)

    if page_id:
        canvas_page = course.get_page(page_id)
        canvas_page.edit(wiki_page=update_data)
    else:
        canvas_page = course.create_page(wiki_page=update_data)

    page_object_info: CanvasObjectInfo = {
        'id': canvas_page.page_id,
        'uri': None,
        'url': canvas_page.html_url if hasattr(canvas_page, 'html_url') else None
    }

    return page_object_info, None


def lookup_page(course: Course, page_title: str) -> Page:
    canvas_page = get_page(course, page_title)
    if not canvas_page:
        raise Exception(f'Page {page_title} not found')

    return canvas_page
