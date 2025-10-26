from canvasapi.course import Course

from ..resources import SyllabusData, SyllabusInfo


class SyllabusObj:
    def __init__(self, course_id: int):
        self.course_id = int
        self.uri = f'/courses/{course_id}/assignments/syllabus'


def deploy_syllabus(course: Course, data: SyllabusData) -> tuple[SyllabusInfo, None]:
    course.update(course={'syllabus_body': data['content']})

    syllabus_object_info: SyllabusInfo = {
        'id': str(course.id)
    }

    return syllabus_object_info, None
