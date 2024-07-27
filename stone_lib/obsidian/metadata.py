import yaml
from typing import Optional
from stone_lib.utilis import zettelkasten_id, time_now_iso8601


class MetaData:
    MandatoryKeys = ["id", "create", "title", "type", "year", "tags", "url", "aliases"]

    def __init__(self, metadata: Optional[str]):
        if metadata is None:
            metadata = {}
        else:
            if "---\n" in metadata:
                metadata = metadata.replace("---\n", "")
            metadata = yaml.load(metadata, Loader=yaml.FullLoader)
        self._metadata = metadata
        self._mandatory_keys_check()

    def __getitem__(self, key):
        return self._metadata[key]

    def __setitem__(self, key, value, force=False):
        if force:
            self._metadata[key] = value
        else:
            if isinstance(self._metadata[key], list):
                self._metadata[key].append(value)
            else:
                self._metadata[key] = value

    def __delitem__(self, key):
        if key in self.MandatoryKeys:
            raise KeyError(f"Key {key} is mandatory, can not be deleted.")
        del self._metadata[key]

    def __str__(self):
        return yaml.dump(self._metadata, allow_unicode=True)

    def __repr__(self):
        return yaml.dump(self._metadata, allow_unicode=True)

    def _mandatory_keys_check(self):
        _id = zettelkasten_id()
        for m_key in self.MandatoryKeys:
            if m_key not in self._metadata.keys():
                if m_key == "id":
                    self._metadata["id"] = _id
                elif m_key == "create":
                    self._metadata["create"] = time_now_iso8601()
                elif m_key == "type":
                    self._metadata["type"] = "unknown"
                elif m_key == "aliases":
                    self._metadata["aliases"] = [self._metadata.get("id", _id)]
                elif m_key in ["tags"]:
                    self._metadata[m_key] = []
                else:
                    self._metadata[m_key] = ""

    def add_tag(self, tag: str, force=False):
        self["tags"] = tag, force

    def add_alias(self, alias: str, force=False):
        self["aliases"] = alias, force

    def modify_name(self, name: str):
        self["title"] = name

    def modify_year(self, year: str):
        self["year"] = year

    def modify_url(self, url: str):
        self["url"] = url

    def modify_type(self, note_type: str):
        self["type"] = note_type

    def add_metadata(self, key: str, value):
        if key in self._metadata.keys():
            raise KeyError(f"Key {key} already exists.")
        self[key] = value

    def toString(self):
        return f"""---\n{yaml.dump(self._metadata, allow_unicode=True)}---\n"""
