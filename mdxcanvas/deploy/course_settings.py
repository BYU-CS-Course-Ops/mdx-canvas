from canvasapi.course import Course

from ..resources import CourseSettings, CanvasObjectInfo


class CourseObj:
    def __init__(self, course_id: int):
        self.course_id = int
        self.uri = f'/courses/{course_id}'


def deploy_settings(course: Course, data: CourseSettings) -> tuple[CanvasObjectInfo, None]:

    course.update(course={
        'name': data['name'],
        'course_code': data['code'],
        'image_id': int(data['image']) if data.get('image') else None
        # TODO: syllabus field
    })
    course_obj = CourseObj(course.id)

    settings_object_info: CanvasObjectInfo = {
        'id': str(course.id),
        'uri': course_obj.uri,
        'url': None
    }

    return settings_object_info, None


def lookup_settings(course: Course, _: str) -> CourseObj:
    return CourseObj(course.id)
