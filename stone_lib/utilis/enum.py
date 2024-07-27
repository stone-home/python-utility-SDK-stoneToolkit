from enum import Enum, EnumMeta
from typing import List, Optional


class EnumManipulator:
    def __init__(self, input_enum: EnumMeta):
        self._enum = input_enum

    def get_enums(self) -> EnumMeta:
        return self._enum

    def get_keys(self) -> List[str]:
        return self.get_enums()._member_names_

    def get_enum(self, key_name: str) -> Optional[Enum]:
        key = None
        for _key in self.get_keys():
            if key_name.lower() == str(_key).lower():
                key = self.get_enums()[_key]
                break
        return key

    def check_key(self, key_name: str) -> bool:
        return False if self.get_enum(key_name) is None else True

    def get_value(self, key_name: str):
        key = self.get_enum(key_name)
        value = None
        if key is not None:
            value = key.value
        return value

    def filter_by_tag(self, tag_name: str) -> list:
        keys = self.get_keys()
        result = []
        for key in keys:
            tags = self.get_enums()[key].value["tags"]
            if tag_name in tags:
                result.append(key)
        return result