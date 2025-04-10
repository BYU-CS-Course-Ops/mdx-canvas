import hashlib
import json
import requests
from pathlib import Path
from tempfile import TemporaryDirectory

from canvasapi.course import Course

from .file import get_file, deploy_file
from ..resources import FileData

MD5_FILE_NAME = '_md5sums.json'


def compute_md5(obj: dict):
    if 'path' in obj:  # e.g. FileData
        path = Path(obj['path'])
        hashable = path.name.encode() + path.read_bytes()
    else:
        hashable = json.dumps(obj).encode()

    return hashlib.md5(hashable).hexdigest()


class MD5Sums:
    def __init__(self, course: Course):
        self._course = course

    def _download_md5s(self):
        md5_file = get_file(self._course, MD5_FILE_NAME)
        if md5_file is None:
            self._md5s = {}
        else:
            self._md5s = {
                tuple(k.split('|')): v
                for k, v in json.loads(requests.get(md5_file.url).text).items()
            }

    def _save_md5s(self):
        with TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / MD5_FILE_NAME
            tmpfile.write_text(json.dumps({'|'.join(k): v for k, v in self._md5s.items()}))
            deploy_file(self._course, FileData(
                path=str(tmpfile.absolute()),
                canvas_folder="_md5s"
            ))

    def get(self, item, *args, **kwargs):
        return self._md5s.get(item, *args, **kwargs)

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
