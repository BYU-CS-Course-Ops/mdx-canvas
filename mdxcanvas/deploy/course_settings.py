from canvasapi.course import Course

from ..resources import CourseSettings, CourseSettingsInfo


class CourseObj:
    def __init__(self, course_id: int):
        self.course_id = int
        self.uri = f'/courses/{course_id}'


def deploy_settings(course: Course, data: CourseSettings) -> tuple[CourseSettingsInfo, None]:

    course.update(course={
        'name': data['name'],
        'course_code': data['code'],
        'image_id': int(data['image']) if data.get('image') else None
        # TODO: syllabus field
    })

    settings_object_info: CourseSettingsInfo = {
        'id': str(course.id)
    }

    return settings_object_info, None
