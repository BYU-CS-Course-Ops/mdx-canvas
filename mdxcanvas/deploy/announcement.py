from canvasapi.course import Course
from canvasapi.discussion_topic import DiscussionTopic

from .util import get_canvas_object
from ..resources import CanvasObjectInfo


def get_announcement(course: Course, title: str) -> DiscussionTopic:
    # NB: the `course` object here was modified in main.py to have a `canvas` field
    # That's why the following code works
    return get_canvas_object(
        lambda: course.canvas.get_announcements(context_codes=[f'course_{course.id}']),
        'title', title
    )


def deploy_announcement(course: Course, announcement_info: dict) -> tuple[CanvasObjectInfo, None]:
    announcement_id = announcement_info["canvas_id"]

    # Remove canvas_id before sending to Canvas API
    update_data = announcement_info.copy()
    update_data.pop('canvas_id', None)

    canvas_announcement: DiscussionTopic
    if announcement_id:
        canvas_announcements = course.canvas.get_announcements(context_codes=[f'course_{course.id}'])
        canvas_announcement = next(
            (a for a in canvas_announcements if a.id == announcement_id), None
        )
        canvas_announcement.update(**update_data)
    else:
        canvas_announcement = course.create_discussion_topic(**update_data)

    announcement_object_info: CanvasObjectInfo = {
        'id':  canvas_announcement.id,
        'uri': None,
        'url': canvas_announcement.html_url
    }

    return announcement_object_info, None


def lookup_announcement(course: Course, announcement_name: str) -> DiscussionTopic:
    return get_announcement(course, announcement_name)
