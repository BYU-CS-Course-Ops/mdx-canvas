from canvasapi.course import Course
from canvasapi.discussion_topic import DiscussionTopic

from .util import get_canvas_object


def get_announcement(course: Course, title: str) -> DiscussionTopic:
    # NB: the `course` object here was modified in main.py to have a `canvas` field
    # That's why the following code works
    return get_canvas_object(
        lambda: course.canvas.get_announcements(context_codes=[f'course_{course.id}']),
        'title', title
    )


def deploy_announcement(course: Course, announcement_info: dict) -> tuple[DiscussionTopic, str | None]:
    title = announcement_info["title"]

    canvas_announcement: DiscussionTopic
    if canvas_announcement := get_announcement(course, title):
        canvas_announcement.update(**announcement_info)
    else:
        canvas_announcement = course.create_discussion_topic(**announcement_info)

    return canvas_announcement, None


def lookup_announcement(course: Course, announcement_name: str) -> DiscussionTopic:
    return get_announcement(course, announcement_name)
