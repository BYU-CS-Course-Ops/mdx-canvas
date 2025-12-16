import hashlib
import json
import requests
from pathlib import Path
from tempfile import TemporaryDirectory

from canvasapi.course import Course

from .file import get_file, deploy_file
from ..resources import FileData

from ..our_logging import get_logger

logger = get_logger()

from .migration import lookup_resource

MD5_FILE_NAME = '_md5sums.json'


def compute_md5(obj: dict):
    if 'path' in obj:  # e.g. FileData
        path = Path(obj['path'])
        hashable = path.name.encode() + path.read_bytes()
    else:
        hashable = json.dumps(obj, sort_keys=True).encode()

    return hashlib.md5(hashable).hexdigest()


class MD5Sums:
    """
    Format:

    --- OLD ---

    {
        "quiz|Homework 0 - Getting Started": "baa3c952dd35fe6064f624a6e07db7dd",
        "page|Lab 0": "d4fca52c8f3407cab31c8ad8013f8985"
    }

    --- NEW ---

    {
        "{rtype}|{rid}": {
            "canvas_info": {
                "id": <str>,
                "uri": <str | None>,
                "url": <str | None>
            },
            "checksum": <str>
        }
    }

    """
    def __init__(self, course: Course):
        self._course = course

    def _download_md5s(self):
        md5_file = get_file(self._course, MD5_FILE_NAME)
        if md5_file is None:
            self._md5s = {}
        else:
            self._md5s = {
                tuple(k.split('|', maxsplit=1)): v
                for k, v in json.loads(requests.get(md5_file.url).text).items()
            }
        self._migrate()
        self._save_md5s()

    def _save_md5s(self):
        with TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / MD5_FILE_NAME
            tmpfile.write_text(json.dumps({'|'.join(k): v for k, v in self._md5s.items()}))
            deploy_file(self._course, FileData(
                path=str(tmpfile.absolute()),
                canvas_folder="_md5s"
            ))

    def _migrate(self):
        for key, value in list(self._md5s.items()):
            if isinstance(value, str):
                rtype, rid = key
                try:
                    canvas_info = lookup_resource(self._course, rtype, rid)
                except Exception as ex:
                    logger.info(f"Failed to lookup resource for migration of MD5 entry {key}: {ex}")
                    continue

                self._md5s[key] = {
                    'canvas_info': canvas_info,
                    'checksum': value
                }
                logger.info(f"Successfully migrated MD5 entry {key}: {value}")

    def get(self, item, *args, **kwargs):
        return self._md5s.get(item, *args, **kwargs)

    def get_checksum(self, item):
        entry = self.get(item)
        return entry.get('checksum', None) if entry else None

    def has_canvas_info(self, item):
        return item in self._md5s

    def get_canvas_info(self, item):
        return self.get(item, {}).get('canvas_info', None)

    def __getitem__(self, item):
        # Act like a dictionary
        return self._md5s[item]

    def __setitem__(self, key, value):
        self._md5s[key] = value

    def __enter__(self):
        self._download_md5s()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._save_md5s()
