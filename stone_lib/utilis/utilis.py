import uuid
import datetime
import os
from typing import List, Optional


def zettelkasten_id() -> str:
    _id = uuid.uuid4().hex
    return f"{_id[:9]}.{_id[-11:]}"


def unique_id() -> str:
    return uuid.uuid4().hex


def time_now_iso8601() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


def timestamp2iso8601(timestamp: int) -> str:
    return datetime.datetime.utcfromtimestamp(timestamp).isoformat() + "Z"


def fetch_file_paths(directory) -> List[str]:
    file_paths = []
    # Walk through the directory and its subdirectories
    for root, _, files in os.walk(directory):
        for file in files:
            # Join the root path with the file name to get the absolute path
            file_path = os.path.join(root, file)
            file_paths.append(str(file_path))

    return file_paths


def filter_files(part_file_name: str, directory: str, fuzz: bool = True) -> List[str]:
    file_paths = fetch_file_paths(directory)
    if fuzz:
        return [str(file_path) for file_path in file_paths if part_file_name in os.path.basename(str(file_path))]
    else:
        return [str(file_path) for file_path in file_paths if part_file_name == os.path.basename(str(file_path))]


def list_directories(path) -> Optional[List[str]]:
    """List all directories in the specified path."""
    # Ensure the path exists
    if not os.path.exists(path):
        print("The specified path does not exist.")
        return None

    # List all entries in the path
    entries = os.listdir(path)
    directories = [entry for entry in entries if os.path.isdir(os.path.join(path, entry))]

    return directories
