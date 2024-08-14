from typing import TypedDict


class CanvasResource(TypedDict):
    type: str
    name: str
    data: dict | None


class FileData(TypedDict):
    path: str
    canvas_folder: str | None


class ZipFileData(TypedDict):
    zip_file_name: str
    content_folder: str
    exclude_pattern: str | None
    priority_folder: str | None
    canvas_folder: str | None


def _get_key(rtype: str, name: str):
    return f'@@{rtype}:{name}@@'


class ResourceManager(dict[str, CanvasResource]):

    def add_resource(self, resource: CanvasResource) -> str:
        self[key := _get_key(resource['type'], resource['name'])] = resource
        return key
