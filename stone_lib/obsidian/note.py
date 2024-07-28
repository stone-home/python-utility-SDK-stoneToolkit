import os
import re
from pathlib import Path
from typing import Tuple, AnyStr
from stone_lib.obsidian.metadata import MetaData
from stone_lib.obsidian.body import Body


class Note:
    FrontMatterReg = "(?s)(^---\n).*?(\n---\n)"

    def __init__(self, path: str):
        """Initialize a note object by inputting a MD file path.

        Args:
            path (str): The path of the MD file.
        """
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
        """Check if the note file exists."""
        return os.path.isfile(self._path)

    @property
    def metadata(self) -> MetaData:
        """Return the metadata of the note."""
        return self._metadata

    @property
    def body(self) -> Body:
        """Return the body of the note."""
        return self._body

    @property
    def file_location(self):
        """Return the file location of the note."""
        return self._path.name

    @classmethod
    def search_front_matter(cls, content: str) -> Tuple[str, str]:
        """A Class method to search the front matter of a note.

        Args:
            content (str): The content of the note.

        Returns:
            Tuple[str, str]: The metadata and the body of the note.

        """
        front_matter = re.search(cls.FrontMatterReg, content)
        metadata = None
        if front_matter:
            metadata = front_matter.group(0)
            content = content.replace(metadata, "")
        return metadata, content

    def save(self, overwrite: bool = False):
        """Save the note to `self.file_location` in the file system.

        Args:
            overwrite (bool, optional): Overwrite the file if it exists. Defaults to False.

        """
        if self._path.is_file() and not overwrite:
            print(f"File {self._path} already exists.")
        else:
            if not self._path.parent.is_dir():
                os.makedirs(self._path.parent, exist_ok=True)
            with open(self._path, "w+", encoding="utf-8") as f:
                f.write(self._metadata.to_string())
                f.write(self._body.to_string())

