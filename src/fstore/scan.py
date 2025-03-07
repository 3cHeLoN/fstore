import os
import pathlib
from typing import Any, Generator


def scantree(path: str) -> Generator:
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry


def scan_files(
    input_folder: pathlib.Path, extension: str = ".jpg", recursive: bool = True
) -> Generator[Any, None, None] | None:
    """Scan files.

    Args:
        input_folder: The input folder.
        extension: The extension to scan.
        recursive: Whether to scan the folder recursively.

    Returns:
        A list of files.
    """
    if recursive:
        return input_folder.rglob("*" + extension, case_sensitive=False)


def scan_files_fast(
    input_folder: str,
    extension: str = ".jpg",
) -> Generator:
    """Scan file types fast.

    Args:
        input_folder: The input folder.
        extension: The file type extension.

    Returns:
        Generator.
    """
    results = scantree(input_folder)
    for result in results:
        if result.name.lower().endswith(extension):
            yield result.path
