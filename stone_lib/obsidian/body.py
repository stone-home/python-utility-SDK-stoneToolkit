from typing import Optional


class Body:
    def __init__(self, body: Optional[str]):
        """Initializes the Body class.

        Args:
            body (Optional[str]): The body of the note. If None, an empty list is created.
        """
        if body is None:
            self._body = []
        else:
            self._body = body.split("\n")

    def add_line(self, content: str, keyword: Optional[str] = None, insert_after=True):
        """Inserts a line into the body of the note.

        Args:
            content (str): The content to be inserted.
            keyword (Optional[str]): The keyword to search in the body. If None, the content is appended to the end of the body.
            insert_after (bool): If True, the content is inserted after the keyword. If False, the content is inserted before the keyword.

        Examples:
            >>> body = Body("This is the first line.\nThis is the second line.")
            >>> body.add_line("This is the third line.", "second")
            >>> print(body.to_string())
            This is the first line.
            This is the second line.
            This is the third line.

            >>> body = Body("This is the first line.\nThis is the second line.")
            >>> body.add_line("This is the third line.", "second", insert_after=False)
            >>> print(body.to_string())
            This is the first line.
            This is the third line.
            This is the second line.

            >>> body = Body("This is the first line.\nThis is the second line.")
            >>> body.add_line("This is the third line.")
            >>> print(body.to_string())
            This is the first line.
            This is the second line.
            This is the third line.

        Returns:

        """
        index = None
        if keyword is not None:
            index = self.search_line(keyword)
            if insert_after:
                index += 1
            else:
                index -= 1

        if index is None:
            self._body.append(content)
        else:
            self._body.insert(index, content)

    def search_line(self, content: str) -> Optional[int]:
        """Fuzz search for a line in the body of the note.

        Args:
            content (str): The content to search in the body.

        Returns:
            Optional[int]: The index of the line in the body. If the content is not found, returns None.

        """
        for index, line in enumerate(self._body):
            if content in line:
                return index
        return None

    def to_string(self) -> str:
        """Converts the body to a string.

        Returns:
            str: The body as a string.

        """
        return "\n".join(self._body)