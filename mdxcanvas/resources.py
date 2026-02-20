import re
from typing import TypedDict, Iterator, Optional, NotRequired, cast


class CanvasResource(TypedDict):
    type: str
    id: str
    data: dict
    content_path: str


class ResourceInfo(TypedDict):
    id: str


class AnnouncementInfo(ResourceInfo):
    id: str
    url: NotRequired[Optional[str]]
    uri: NotRequired[Optional[str]]  # for course-link
    title: str  # for course-link


class CourseSettingsInfo(ResourceInfo):
    id: str


class AssignmentInfo(ResourceInfo):
    id: str
    url: NotRequired[Optional[str]]
    uri: NotRequired[Optional[str]]  # for course-link
    title: str  # for course-link text


class FileInfo(ResourceInfo):
    id: str
    uri: str
    title: str  # for course-link


class AssignmentGroupInfo(ResourceInfo):
    id: str


class ModuleInfo(ResourceInfo):
    id: str
    title: str  # for course-link
    uri: str
    url: str


class ModuleItemInfo(ResourceInfo):
    id: str
    module_id: str
    uri: str
    url: str


class OverrideInfo(ResourceInfo):
    id: str
    assignment_id: str


class PageInfo(ResourceInfo):
    id: str
    page_url: str  # for module item
    uri: str  # for course-link
    url: NotRequired[Optional[str]]
    title: str  # for course-link text


class QuizInfo(ResourceInfo):
    id: str
    uri: str  # for course-link
    url: NotRequired[Optional[str]]
    title: str  # for course-link text


class QuizQuestionInfo(ResourceInfo):
    id: str
    quiz_id: str
    uri: str
    url: Optional[str]


class QuizQuestionOrderInfo(ResourceInfo):
    quiz_id: str
    uri: str
    url: Optional[str]

class SyllabusInfo(ResourceInfo):
    id: str
    uri: str
    url: str
    title: str  # for course-link title


class CourseSettings(TypedDict):
    name: str
    code: str
    image: str


class FileData(TypedDict):
    path: str
    canvas_folder: NotRequired[Optional[str]]
    lock_at: NotRequired[Optional[str]]
    unlock_at: NotRequired[Optional[str]]


class ZipFileData(TypedDict):
    zip_file_name: str
    content_folder: str
    additional_files: NotRequired[Optional[list[str]]]
    exclude_pattern: NotRequired[Optional[str]]
    priority_folder: NotRequired[Optional[str]]
    canvas_folder: NotRequired[Optional[str]]


class SyllabusData(TypedDict):
    content: str


def iter_keys(text: str) -> Iterator[tuple[str, str, str, str]]:
    for match in re.finditer(r'__@@([^|]+)\|\|(.+?)\|\|([^@]+)@@__', text):
        yield (match.group(0), *cast(tuple[str, str, str], match.groups()))


def get_key(rtype: str, rid: str, field: str):
    return f'__@@{rtype}||{rid}||{field}@@__'


class ResourceManager(dict[tuple[str, str], CanvasResource]):

    def add_resource(self, resource: CanvasResource, field: Optional[str] = None) -> Optional[str]:
        rtype = resource['type']
        rid = resource['id']
        self[rtype, rid] = resource
        return get_key(rtype, rid, field) if field else None
