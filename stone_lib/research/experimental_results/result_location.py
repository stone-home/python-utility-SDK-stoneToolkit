import os
from pathlib import Path


class ResearchDataLocation:
    def __init__(self, entry_dir: str):
        """Manage the location of the research data

        Args:
            entry_dir (str): The entry directory of the research data
        """
        self.entry_dir = Path(entry_dir)
        if not self.entry_dir.is_dir():
            raise NotADirectoryError(f"{entry_dir} is not a directory")

    def auto_fetch_location(self, current_path: str, depth: int = 2) -> str:
        """Automatically fetch the location of the result file based on the current file path

        Args:
            current_path (str): The current file path
            depth (int): The depth of the file from the entry directory

        Returns:
            str: The location of the result file

        """
        current_path = Path(current_path)
        if current_path.is_file():
            depth += 1  # Add 1 to include the file itself
            path_suffix = current_path.parts[-depth:-1]
        else:
            path_suffix = current_path.parts[-depth:]
        return os.path.join(self.entry_dir, *path_suffix)
