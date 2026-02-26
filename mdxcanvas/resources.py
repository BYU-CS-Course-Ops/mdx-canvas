import re
from typing import NotRequired, Optional, TypedDict, Iterator, cast


#
# Information about deployed resources
#

class ResourceInfo(TypedDict):
    id: str


class AnnouncementInfo(ResourceInfo):
    id: str
    url: str | None
    uri: str | None  # for course-link
    title: str  # for course-link


class CourseSettingsInfo(ResourceInfo):
    id: str


class AssignmentInfo(ResourceInfo):
    id: str
    url: str | None
    uri: str | None  # for course-link
    title: str  # for course-link text


class FileInfo(ResourceInfo):
    id: str
    uri: str
    url: str
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
    url: str | None
    title: str  # for course-link text


class QuizInfo(ResourceInfo):
    id: str
    uri: str  # for course-link
    url: str | None
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


#
# Information needed to deploy a resource
#

class CanvasResource(TypedDict):
    type: str
    id: str
    data: dict | FileData | ZipFileData | QuartoSlidesData | SyllabusData
    content_path: str


class CourseSettings(TypedDict):
    name: str
    code: str
    image: str


class FileData(TypedDict):
    path: str
    checksum_paths: NotRequired[list[str]]
    canvas_folder: str | None
    lock_at: str | None
    unlock_at: str | None
    canvas_id: NotRequired[Optional[str]]


class ZipFileData(TypedDict):
    zip_file_name: str
    zip_contents: dict[str, str]
    checksum_paths: NotRequired[list[str]]
    canvas_folder: str | None
    canvas_id: NotRequired[Optional[str]]


class QuartoSlidesData(TypedDict):
    path: str
    root_path: str
    checksum_paths: NotRequired[list[str]]
    slides_name: str
    canvas_folder: str | None
    lock_at: str | None
    unlock_at: str | None
    canvas_id: NotRequired[Optional[str]]


class SyllabusData(TypedDict):
    content: str
    canvas_id: NotRequired[Optional[str]]


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
