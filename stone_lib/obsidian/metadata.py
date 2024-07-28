import yaml
from typing import Optional, Any
from stone_lib.utilis import zettelkasten_id, time_now


class MetaData:
    MandatoryKeys = ["id", "create", "title", "type", "year", "tags", "url", "aliases"]

    def __init__(self, metadata: Optional[str]):
        """Initializes the metadata object. If metadata is None, it will create a new metadata object with default values.

        Args:
            metadata (Optional[str]): Metadata in yaml format or string format.

        Examples:
            >>> metadata = MetaData("---\nid: 123\n---\n")
            or
            >>> metadata = MetaData("id: 123\nname: test")


        """
        if metadata is None:
            metadata = {}
        else:
            if "---\n" in metadata:
                metadata = metadata.replace("---\n", "")
            metadata = yaml.load(metadata, Loader=yaml.FullLoader)
        self._metadata = metadata
        self._mandatory_keys_check()

    def __getitem__(self, key: str) -> Any:
        """get the value of the key from metadata.

        Args:
            key (str): key to get the value from internal variable, metadata.

        Examples:
            >>> metadata = MetaData("---\nid: 123\n---\n")
            >>> metadata["id"]
            123

        Returns:
            Any: value of the key.

        """
        return self._metadata[key]

    def __setitem__(self, key: str, value: Any, force: bool = False):
        """Set a value to the key in metadata. If force is True, it will overwrite the value of the key.

        Args:
            key (str): key to set the value.
            value (Any): value to set.
            force (bool): If True, it will overwrite the value of the key.

        Examples:
            >>> metadata = MetaData("---\nid: 123\n---\n")
            >>> metadata["id"] = "456"
            >>> metadata["id"]
            456
            or
            >>> metadata = MetaData("---\nid:\n- 1\n-2\n---\n")
            >>> metadata["id"] = 3
            >>> metadata["id"]
            [1, 2, 3]

        """

        if force:
            self._metadata[key] = value
        else:
            if isinstance(self._metadata[key], list):
                self._metadata[key].append(value)
            else:
                self._metadata[key] = value

    def __delitem__(self, key: str):
        """Delete the key from metadata. If the key is mandatory, it will raise an error.

        Args:
            key (str): key to delete from metadata.

        """
        if key in self.MandatoryKeys:
            raise KeyError(f"Key {key} is mandatory, can not be deleted.")
        del self._metadata[key]

    def __str__(self) -> str:
        """Return the metadata in yaml format.

        Examples:
            >>> metadata = MetaData("---\nid: 123\n---\n")
            >>> print(metadata)
            id: 123

        Returns:

        """
        return yaml.dump(self._metadata, allow_unicode=True)

    def __repr__(self) -> str:
        """Return the metadata in yaml format.

        Examples:
            >>> metadata = MetaData("---\nid: 123\n---\n")
            >>> print(repr(metadata))
            id: 123

        Returns:

        """
        return yaml.dump(self._metadata, allow_unicode=True)

    def _mandatory_keys_check(self):
        """Check if the mandatory keys are present in the metadata. If not, it will add the default values."""
        _id = zettelkasten_id()
        for m_key in self.MandatoryKeys:
            if m_key not in self._metadata.keys():
                if m_key == "id":
                    self._metadata["id"] = _id
                elif m_key == "create":
                    self._metadata["create"] = time_now(iso8601=True)
                elif m_key == "type":
                    self._metadata["type"] = "unknown"
                elif m_key == "aliases":
                    self._metadata["aliases"] = [self._metadata.get("id", _id)]
                elif m_key in ["tags"]:
                    self._metadata[m_key] = []
                else:
                    self._metadata[m_key] = ""

    def add_tag(self, tag: str, force=False):
        """Insert a tag to the metadata.

        Args:
            tag (str): tag to insert.
            force (bool): If True, it will overwrite the tag.

        """
        self["tags"] = tag, force

    def add_alias(self, alias: str, force=False):
        """Insert an alias to the metadata.

        Args:
            alias (str): alias to insert.
            force (bool): If True, it will overwrite the alias.

        """
        self["aliases"] = alias, force

    def modify_name(self, name: str):
        """Modify the title of the metadata.

        Args:
            name (str): title
        """
        self["title"] = name

    def modify_year(self, year: str):
        """Modify the year of the metadata.

        Args:
            year (str): year

        """
        self["year"] = year

    def modify_url(self, url: str):
        """Modify the url of the metadata.

        Args:
            url (str): url
        """
        self["url"] = url

    def modify_type(self, note_type: str):
        """Modify the type of the metadata.

        Args:
            note_type (str): type of the note.
        """
        self["type"] = note_type

    def add_metadata(self, key: str, value: Any):
        """Insert a new key-value pair to the metadata.

        Args:
            key (str): key to insert.
            value (Any): value to insert.

        """
        if key in self._metadata.keys():
            raise KeyError(f"Key {key} already exists.")
        self[key] = value

    def to_string(self):
        """Return the metadata in yaml format.

        Returns:
            str: metadata in yaml format
        """

        return f"""---\n{yaml.dump(self._metadata, allow_unicode=True)}---\n"""
