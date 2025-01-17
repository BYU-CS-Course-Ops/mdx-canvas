from canvasapi.course import Course
from canvasapi.discussion_topic import DiscussionTopic

from .util import get_canvas_object


def get_announcement(course: Course, title: str) -> DiscussionTopic:
    return get_canvas_object(course.get_discussion_topics, 'title', title)


def deploy_announcement(course: Course, announcement_info: dict) -> tuple[DiscussionTopic, str | None]:
    name = announcement_info["name"]

    if canvas_announcement := get_announcement(course, name):
        canvas_announcement.edit(announcement=announcement_info)
    else:
        canvas_announcement = course.create_discussion_topic(announcement=announcement_info)

    return canvas_announcement, None


def lookup_announcement(course: Course, announcement_name: str) -> DiscussionTopic:
    return get_announcement(course, announcement_name)
