import re
from typing import TypedDict, Iterator


class CanvasResource(TypedDict):
    type: str
    id:   str
    data: dict | None


class ResourceInfo(TypedDict):
    id:  int


class AnnouncementInfo(ResourceInfo):
    id:  int
    url: str | None


class CourseSettingsInfo(ResourceInfo):
    id: int


class AssignmentInfo(ResourceInfo):
    id: int
    uri: str | None
    url: str | None


class FileInfo(ResourceInfo):
    id: int
    uri: str | None


class AssignmentGroupInfo(ResourceInfo):
    id: int


class ModuleInfo(ResourceInfo):
    id: int


class OverrideInfo(ResourceInfo):
    id: int


class PageInfo(ResourceInfo):
    id: int
    url: str | None


class QuizInfo(ResourceInfo):
    id: int
    assignment_id: int
    url: str | None


class SyllabusInfo(ResourceInfo):
    id: int


class CourseSettings(TypedDict):
    name:  str
    code:  str
    image: str


class FileData(TypedDict):
    path:          str
    canvas_folder: str | None
    lock_at:       str | None
    unlock_at:     str | None


class ZipFileData(TypedDict):
    zip_file_name:    str
    content_folder:   str
    additional_files: list[str] | None
    exclude_pattern:  str       | None
    priority_folder:  str       | None
    canvas_folder:    str       | None


class SyllabusData(TypedDict):
    content: str


def iter_keys(text: str) -> Iterator[tuple[str, str, str, str]]:
    for match in re.finditer(fr'@@([^|]+)\|\|([^|]+)\|\|([^@]+)@@', text):
        yield match.group(0), *match.groups()


def get_key(rtype: str, rid: str, field: str):
    return f'@@{rtype}||{rid}||{field}@@'


class ResourceManager(dict[tuple[str, str], CanvasResource]):

    def add_resource(self, resource: CanvasResource, field: str = None) -> str:
        rtype = resource['type']
        rid = resource['id']
        self[rtype, rid] = resource
        return get_key(rtype, rid, field) if field else None
