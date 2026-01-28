from canvasapi.course import Course

from mdxcanvas.resources import AnnouncementInfo
from ..resources import AnnouncementInfo


def deploy_announcement(course: Course, announcement_info: dict) -> AnnouncementInfo:
    announcement_id = announcement_info["canvas_id"]

    if announcement_id:
        canvas_announcement = course.get_discussion_topic(announcement_id)
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

    return announcement_object_info
