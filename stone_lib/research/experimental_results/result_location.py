import os
from pathlib import Path


class ResearchDataLocation:
    def __init__(self, entry_dir: str):
        self.entry_dir = Path(entry_dir)
        if not self.entry_dir.is_dir():
            raise NotADirectoryError(f"{entry_dir} is not a directory")

    def auto_fetch_location(self, current_file_path: str, depth: int = 2) -> str:
        current_file_path = Path(current_file_path)
        if not current_file_path.is_file():
            raise FileNotFoundError(f"{current_file_path} is not a file")
        depth += 1 # Add 1 to include the file itself
        return os.path.join(self.entry_dir, *current_file_path.parts[-depth:])


if __name__ == "__main__":
    rdl = ResearchDataLocation("/stone_lib/research/experimental_results")
    print("x")
    print(rdl.auto_fetch_location(__file__))