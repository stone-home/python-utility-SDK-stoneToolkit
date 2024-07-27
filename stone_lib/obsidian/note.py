import os
import re
from pathlib import Path
from typing import Tuple, AnyStr
from stone_lib.obsidian.metadata import MetaData
from stone_lib.obsidian.body import Body


class Note:
    ForntMatterReg = "(?s)(^---\n).*?(\n---\n)"

    def __init__(self, path: str):
        self._path = Path(path)
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                _metadata, _body = self.search_front_matter(content)
        else:
            _metadata, _body = None, None
        self._metadata = MetaData(_metadata)
        self._body = Body(_body)

    @property
    def exist(self):
        return os.path.isfile(self._path)

    @property
    def metadata(self) -> MetaData:
        return self._metadata

    @property
    def body(self) -> Body:
        return self._body

    @property
    def file_location(self):
        return self._path.name

    @classmethod
    def search_front_matter(cls, content: str) -> Tuple[str, str]:
        front_matter = re.search(cls.ForntMatterReg, content)
        metadata = None
        if front_matter:
            metadata = front_matter.group(0)
            content = content.replace(metadata, "")
        return metadata, content

    def save(self, overwrite: bool = False):
        if self._path.is_file() and not overwrite:
            print(f"File {self._path} already exists.")
        else:
            if not self._path.parent.is_dir():
                os.makedirs(self._path.parent, exist_ok=True)
            with open(self._path, "w+", encoding="utf-8") as f:
                f.write(self._metadata.toString())
                f.write(self._body.toString())

