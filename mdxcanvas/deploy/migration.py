from canvasapi.course import Course
from canvasapi.discussion_topic import DiscussionTopic
from canvasapi.assignment import Assignment, AssignmentOverride
from canvasapi.file import File
from canvasapi.quiz import Quiz

from .course_settings import CourseObj
from .syllabus import SyllabusObj

from .util import get_canvas_object, ResourceNotFoundException
from ..resources import AnnouncementInfo, AssignmentInfo, FileInfo, AssignmentGroupInfo, ModuleInfo, OverrideInfo, \
    PageInfo, QuizInfo, SyllabusInfo, CourseSettings, CourseSettingsInfo


# ============================== Announcements ==============================
def get_announcement(course: Course, title: str) -> DiscussionTopic:
    # NB: the `course` object here was modified in main.py to have a `canvas` field
    # That's why the following code works
    return get_canvas_object(
        lambda: course.get_discussion_topics(course_id=course.id, only_announcements=True),
        'title', title
    )


def lookup_announcement(course: Course, announcement_name: str) -> AnnouncementInfo:
    announcement = get_announcement(course, announcement_name)
    if not announcement:
        raise ResourceNotFoundException(f'Announcement {announcement_name} not found')

    announcement_info = AnnouncementInfo(
        id=str(announcement.id),
        url=getattr(announcement, 'html_url', None)
    )

    return announcement_info


# ============================== Assignments ==============================
def get_assignment(course: Course, name: str) -> Assignment:
    return get_canvas_object(course.get_assignments, 'name', name)


def lookup_assignment(course: Course, assignment_name: str) -> AssignmentInfo:
    assignment = get_assignment(course, assignment_name)
    if not assignment:
        raise ResourceNotFoundException(f'Assignment {assignment_name} not found')

    assignment_info = AssignmentInfo(
        id=str(assignment.id),
        uri=getattr(assignment, 'html_url', None),
        url=getattr(assignment, 'html_url', None)
    )

    return assignment_info


# ============================== Course Settings ==============================
def lookup_settings(course: Course, _: str) -> CourseSettingsInfo:
    return CourseSettingsInfo(
        id=str(course.id),
    )


# ============================== Files ==============================
def get_file(course: Course, name: str) -> File:
    return get_canvas_object(course.get_files, 'display_name', name)


def lookup_file(course: Course, name: str) -> FileInfo:
    file = get_file(course, name)
    if not file:
        raise ResourceNotFoundException(f'File {name} not found')

    file_info = FileInfo(
        id=str(file.id),
        uri=f'/files/{file.id}'
    )

    return file_info


# ============================== Assignment Groups ==============================
def lookup_group(course: Course, name: str) -> AssignmentGroupInfo:
    group = get_canvas_object(course.get_assignment_groups, 'name', name)
    if not group:
        raise ResourceNotFoundException(f'Assignment group {name} not found')

    group_info = AssignmentGroupInfo(
        id=str(group.id)
    )

    return group_info


# ============================== Modules ==============================
def lookup_module(course: Course, name: str) -> ModuleInfo:
    module = get_canvas_object(course.get_modules, 'name', name)
    if not module:
        raise ResourceNotFoundException(f'Module {name} not found')

    module_info = ModuleInfo(
        id=str(module.id)
    )

    return module_info


# ============================== Overrides ==============================
def get_override(assignment: Assignment, section_id: int) -> AssignmentOverride:
    return get_canvas_object(assignment.get_overrides, 'course_section_id', section_id)


def get_assignment_and_section(course: Course, name: str) -> tuple[Assignment, int]:
    assignment_name, section_id = name.split('|')
    assignment = get_assignment(course, assignment_name)
    return assignment, int(section_id)


def lookup_override(course: Course, override_name: str) -> OverrideInfo:
    assignment, section_id = get_assignment_and_section(course, override_name)
    override = get_override(assignment, section_id)
    if not override:
        raise ResourceNotFoundException(f'Override {override_name} not found')

    override_info = OverrideInfo(
        id=str(override.id)
    )

    return override_info


# ============================== Pages ==============================
def get_page(course: Course, title: str):
    return get_canvas_object(course.get_pages, 'title', title)

def lookup_page(course: Course, page_title: str) -> PageInfo:
    canvas_page = get_page(course, page_title)
    if not canvas_page:
        raise ResourceNotFoundException(f'Page {page_title} not found')

    page_info = PageInfo(
        id=str(canvas_page.page_id),
        url=getattr(canvas_page, 'url', None)
    )

    return page_info


# ============================== Quizzes ==============================
def get_quiz(course: Course, title: str) -> Quiz:
    return get_canvas_object(course.get_quizzes, "title", title)

def lookup_quiz(course: Course, quiz_name: str) -> QuizInfo:
    canvas_quiz = get_quiz(course, quiz_name)
    if not canvas_quiz:
        raise ResourceNotFoundException(f'Quiz {quiz_name} not found')

    quiz_info = QuizInfo(
        id=str(canvas_quiz.id),
        url=getattr(canvas_quiz, 'html_url', None)
    )

    return quiz_info


# ============================== Syllabus ==============================
def lookup_syllabus(course: Course, _: str) -> SyllabusInfo:
    return SyllabusInfo(
        id=str(course.id),
    )


# ============================== Zips ==============================
lookup_zip = lookup_file


# ============================== Resource Lookup Map ==============================
RESOURCE_LOOKUP_MAP = {
    'announcement': lookup_announcement,
    'assignment': lookup_assignment,
    'course_settings': lookup_settings,
    'file': lookup_file,
    'assignment_group': lookup_group,
    'module': lookup_module,
    'override': lookup_override,
    'page': lookup_page,
    'quiz': lookup_quiz,
    'syllabus': lookup_syllabus,
    'zip': lookup_zip
}


def lookup_resource(course: Course, resource_type: str, resource_name: str):
    if resource_type not in RESOURCE_LOOKUP_MAP:
        raise Exception(f'Lookup unsupported for resource of type {resource_type}')

    lookup_function = RESOURCE_LOOKUP_MAP[resource_type]
    return lookup_function(course, resource_name)
