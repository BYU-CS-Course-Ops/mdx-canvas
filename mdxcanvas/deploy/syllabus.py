from canvasapi.course import Course

from ..resources import SyllabusData


class SyllabusObj:
    def __init__(self, course_id: int):
        self.course_id = int
        self.uri = f'/courses/{course_id}/assignments/syllabus'


def deploy_syllabus(course: Course, data: SyllabusData) -> tuple[SyllabusObj, str|None]:
    course.update(course={'syllabus_body': data['content']})
    return SyllabusObj(course.id), None


def lookup_syllabus(course: Course, _: str) -> SyllabusObj:
    return SyllabusObj(course.id)
