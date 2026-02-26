import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import requests
from canvasapi.course import Course

from .file import get_file, deploy_file
from ..our_logging import get_logger
from ..resources import FileData

logger = get_logger()

MD5_FILE_NAME = '_md5sums.json'


def _compute_checksum_of_path(resource_path: Path) -> bytes:
    """Compute checksum of file-tree identified by path"""

    if resource_path.is_file():
        return hashlib.md5(resource_path.read_bytes()).hexdigest().encode()

    if resource_path.is_dir():
        file_digests = []
        for file_path in sorted(p for p in resource_path.glob('*')):
            file_digests.append(_compute_checksum_of_path(file_path))

        return hashlib.md5(b''.join(file_digests)).hexdigest().encode()

    raise FileNotFoundError(f'Path does not exist or is not a file/directory: {resource_path}')


def compute_md5(obj: dict):
    hashable = b''

    paths = obj.get('checksum_paths', [])
    for path in paths:
        hashable += _compute_checksum_of_path(Path(path))

    hashable += json.dumps(obj, sort_keys=True).encode()

    return hashlib.md5(hashable).hexdigest()


class MD5Sums:
    """
    Format:
    {
        "mdxcanvas_version": <str>,
        "resources": {
            "{rtype}|{rid}": {
                "canvas_info": {
                    "id":  <str>,
                    "uri": <str | None>,
                    "url": <str | None>
                },
                "checksum": <str>
            }
        }
    }
    """

    def __init__(self, course: Course):
        self._version = None
        self._course = course

    def _download_md5s(self):
        md5_file = get_file(self._course, MD5_FILE_NAME)
        if md5_file is None:
            self._version = None
            self._md5s = {}
        else:
            data = json.loads(requests.get(md5_file.url).text)
            if 'resources' in data:
                # New nested format
                self._version = data.get('mdxcanvas_version')
                self._md5s = {
                    tuple(k.split('|', maxsplit=1)): v
                    for k, v in data['resources'].items()
                }
            else:
                # Old flat format — no version existed in this format
                self._version = None
                self._md5s = {
                    tuple(k.split('|', maxsplit=1)): v
                    for k, v in data.items()
                }
        self._save_md5s()

    def _save_md5s(self):
        data = {
            'mdxcanvas_version': self._version,
            'resources': {'|'.join(k): v for k, v in self._md5s.items()}
        }
        with TemporaryDirectory() as tmpdir:
            tmpfile = Path(tmpdir) / MD5_FILE_NAME
            tmpfile.write_text(json.dumps(data))
            deploy_file(self._course, FileData(
                path=(p := str(tmpfile.absolute())),
                checksum_paths=[p],
                canvas_folder="_md5s",
                lock_at=None, unlock_at=None
            ))

    def items(self):
        return self._md5s.items()

    def get(self, item, *args, **kwargs):
        return self._md5s.get(item, *args, **kwargs)

    def add_mdxcanvas_version(self, version):
        self._version = version

    def get_mdxcanvas_version(self):
        return self._version

    def has_mdxcanvas_version(self):
        return self._version is not None

    def get_canvas_info(self, item):
        return self.get(item, {}).get('canvas_info', None)

    def has_canvas_info(self, item):
        return self.get_canvas_info(item) is not None

    def get_checksum(self, item):
        entry = self.get(item)
        return entry.get('checksum', None) if entry else None

    def has_checksum(self, item):
        return self.get_checksum(item) is not None

    def remove(self, item):
        if item in self._md5s:
            del self._md5s[item]

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
