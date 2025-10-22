from canvasapi.course import Course

from ..resources import SyllabusData, CanvasObjectInfo


class SyllabusObj:
    def __init__(self, course_id: int):
        self.course_id = int
        self.uri = f'/courses/{course_id}/assignments/syllabus'


def deploy_syllabus(course: Course, data: SyllabusData) -> tuple[CanvasObjectInfo, None]:
    course.update(course={'syllabus_body': data['content']})
    syllabus_obj = SyllabusObj(course.id)

    syllabus_object_info: CanvasObjectInfo = {
        'id': str(course.id),
        'uri': syllabus_obj.uri,
        'url': None
    }

    return syllabus_object_info, None


def lookup_syllabus(course: Course, _: str) -> SyllabusObj:
    return SyllabusObj(course.id)
