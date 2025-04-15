import re
from typing import TypedDict, Iterator


class CanvasResource(TypedDict):
    type: str
    name: str
    data: dict | None


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
    for match in re.finditer(fr'@@([^|]+)\|\|([^|]+)\|\|([^@]+)@@', text):
        yield match.group(0), *match.groups()


def get_key(rtype: str, name: str, field: str):
    return f'@@{rtype}||{name}||{field}@@'


class ResourceManager(dict[tuple[str, str], CanvasResource]):

    def add_resource(self, resource: CanvasResource, field: str = None) -> str:
        rtype = resource['type']
        rname = resource['name']
        self[rtype, rname] = resource
        return get_key(rtype, rname, field) if field else None
