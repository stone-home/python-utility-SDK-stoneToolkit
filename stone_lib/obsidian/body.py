from typing import Optional


class Body:
    def __init__(self, body: Optional[str]):
        if body is None:
            self._body = []
        else:
            self._body = body.split("\n")

    def add_line(self, line: str, keyword: Optional[str] = None, insert_after=True):
        index = None
        if keyword is not None:
            index = self.search_line(keyword)
            if insert_after:
                index += 1
            else:
                index -= 1

        if index is None:
            self._body.append(line)
        else:
            self._body.insert(index, line)

    def search_line(self, content: str) -> Optional[int]:
        for index, line in enumerate(self._body):
            if content in line:
                return index
        return None

    def toString(self) -> str:
        return "\n".join(self._body)