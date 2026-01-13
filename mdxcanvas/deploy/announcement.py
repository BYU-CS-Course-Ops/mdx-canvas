from canvasapi.course import Course
from canvasapi.discussion_topic import DiscussionTopic

from ..resources import AnnouncementInfo


def get_announcement(course: Course, announcement_id: int) -> DiscussionTopic | None:
    canvas_announcements = course.get_discussion_topics(course_id=course.id, only_announcements=True)
    canvas_announcement = next(
        (a for a in canvas_announcements if a.id == announcement_id), None
    )
    return canvas_announcement


def deploy_announcement(course: Course, announcement_info: dict) -> tuple[AnnouncementInfo, None]:
    announcement_id = announcement_info["canvas_id"]

    if announcement_id:
        canvas_announcement = get_announcement(course, announcement_id)
        canvas_announcement.update(**announcement_info)

    else:
        canvas_announcement = course.create_discussion_topic(**announcement_info)

    announcement_object_info: AnnouncementInfo = {
        'id': canvas_announcement.id,
        'title': canvas_announcement.title,
        'uri': f'/courses/{course.id}/discussion_topics/{canvas_announcement.id}',

        # Following fields have been observed to be missing in some cases
        'url': canvas_announcement.html_url if hasattr(canvas_announcement, 'html_url') else None
    }

    return announcement_object_info, None
