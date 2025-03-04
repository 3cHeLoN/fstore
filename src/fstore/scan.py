import pathlib
from typing import Any, Generator


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
