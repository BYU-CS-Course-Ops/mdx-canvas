from canvasapi.course import Course

from ..resources import SyllabusData, SyllabusInfo


def deploy_syllabus(course: Course, data: SyllabusData) -> tuple[SyllabusInfo, None]:
    course.update(course={'syllabus_body': data['content']})

    syllabus_object_info: SyllabusInfo = {
        'id': str(course.id),
        'title': 'Syllabus',
        'uri': f'/courses/{course.id}/assignments/syllabus',
        'url': f'{course.canvas._Canvas__requester.original_url}/courses/{course.id}/assignments/syllabus'
    }

    return syllabus_object_info, None
