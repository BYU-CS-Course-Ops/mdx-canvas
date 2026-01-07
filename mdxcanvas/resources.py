import re
from typing import TypedDict, Iterator


class CanvasResource(TypedDict):
    type: str
    id: str
    data: dict
    content_path: str


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
    uri: str
    url: str


class OverrideInfo(ResourceInfo):
    id: str


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
    canvas_folder: str | None
    lock_at: str | None
    unlock_at: str | None


class ZipFileData(TypedDict):
    zip_file_name: str
    content_folder: str
    additional_files: list[str] | None
    exclude_pattern: str | None
    priority_folder: str | None
    canvas_folder: str | None


class SyllabusData(TypedDict):
    content: str


def iter_keys(text: str) -> Iterator[tuple[str, str, str, str]]:
    for match in re.finditer(fr'__@@([^|]+)\|\|([^|]+)\|\|([^@]+)@@__', text):
        yield match.group(0), *match.groups()


def get_key(rtype: str, rid: str, field: str):
    return f'__@@{rtype}||{rid}||{field}@@__'


class ResourceManager(dict[tuple[str, str], CanvasResource]):

    def add_resource(self, resource: CanvasResource, field: str = None) -> str:
        rtype = resource['type']
        rid = resource['id']
        self[rtype, rid] = resource
        return get_key(rtype, rid, field) if field else None
