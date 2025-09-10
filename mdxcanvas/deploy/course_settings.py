from canvasapi.course import Course

from ..resources import CourseSettings


class CourseObj:
    def __init__(self, course_id: int):
        self.course_id = int
        self.uri = f'/courses/{course_id}'


def deploy_settings(course: Course, data: CourseSettings) -> tuple[CourseObj, str | None]:

    course.update(course={
        'name': data['name'],
        'course_code': data['code'],
        'image_id': int(data['image']) if data.get('image') else None
    })
    return CourseObj(course.id), None


def lookup_settings(course: Course, _: str) -> CourseObj:
    return CourseObj(course.id)
