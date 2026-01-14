import json
import logging
from typing import Callable

from canvasapi.course import Course

from .checksums import MD5Sums

from ..resources import (
    AnnouncementInfo,
    AssignmentInfo,
    AssignmentGroupInfo,
    CourseSettingsInfo,
    FileInfo,
    ModuleInfo,
    ModuleItemInfo,
    OverrideInfo,
    PageInfo,
    QuizInfo,
    SyllabusInfo,
)

logger = logging.getLogger(__name__)

ATTRS = lambda cls: set(cls.__annotations__.keys())

RESOURCE_INFO = {
    'announcement': ATTRS(AnnouncementInfo),
    'assignment': ATTRS(AssignmentInfo),
    'assignment_group': ATTRS(AssignmentGroupInfo),
    'course_settings': ATTRS(CourseSettingsInfo),
    'file': ATTRS(FileInfo),
    'module': ATTRS(ModuleInfo),
    'module_item': ATTRS(ModuleItemInfo),
    'override': ATTRS(OverrideInfo),
    'page': ATTRS(PageInfo),
    'quiz': ATTRS(QuizInfo),
    'syllabus': ATTRS(SyllabusInfo),
}

ATTR_GETTERS: dict[str, Callable[[Course, list[tuple[str, str, dict]]], dict[tuple[str, str], dict]]] = {}


def migration(rtype: str, attr: str):
    def decorator(func: Callable[[Course, list[tuple[str, str, dict]]], dict[tuple[str, str], dict]]):
        ATTR_GETTERS[attr] = func
        return func

    return decorator


def update_resource_info(course: Course, md5s: MD5Sums) -> dict:
    copy_md5s = md5s.copy()

    # Map out all resources that are missing expected attributes in their canvas_info and need to be updated
    to_update: dict[str, list[tuple[str, str, dict]]] = {}

    for (rtype, rid), info in copy_md5s.items():
        if rtype not in RESOURCE_INFO:
            continue

        canvas_info = info.get('canvas_info', {})

        current_attrs = set(canvas_info.keys())
        expected_attrs = RESOURCE_INFO[rtype]

        if missing_attrs := expected_attrs - current_attrs:
            for missing_attr in missing_attrs:
                to_update[missing_attr] = to_update.get(missing_attr, [])
                to_update[missing_attr].append((rtype, rid, canvas_info))

    attr_values = {}
    for missing_attr, resources in to_update.items():
        if missing_attr_getter := ATTR_GETTERS.get(missing_attr):
            missing_attr_vals = missing_attr_getter(course, resources)

            # Union the newly found attribute values into the overall attr_values dict
            attr_values |= missing_attr_vals

    for (rtype, rid), canvas_info in attr_values.items():
        if (rtype, rid) in copy_md5s:
            copy_md5s[(rtype, rid)]['canvas_info'] |= canvas_info

    return copy_md5s


# Import modules to register @migration decorated functions
from . import module, override  # noqa: F401


if __name__ == '__main__':
    import os
    from ..main import get_course
    from ..deploy.checksums import MD5Sums

    canvas_api_token = os.environ.get("CANVAS_API_TOKEN")

    course = get_course(canvas_api_token, "https://byu.instructure.com/", 20736)

    with MD5Sums(course) as md5s:
        curr_md5s = md5s.copy()

        result = {}
        for key, value in curr_md5s.items():
            result['|'.join(key)] = value

        with open('current_md5s.json', 'w') as f:
            json.dump(result, f, indent=4)

    with MD5Sums(course) as md5s:
        updated_md5s = update_resource_info(course, md5s)

        result = {}
        for key, value in updated_md5s.items():
            result['|'.join(key)] = value

        with open('updated_md5s.json', 'w') as f:
            json.dump(result, f, indent=4)

    print("Migration completed successfully")
