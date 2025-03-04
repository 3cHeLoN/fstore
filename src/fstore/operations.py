"""Copy utilities."""

import logging
import pathlib
import shutil
from dataclasses import dataclass
from enum import Enum, auto

import xxhash


class FileCompare(Enum):
    """Compare two files."""

    SAME = auto()
    DIFFERENT = auto()
    NEW = auto()


class FileOperation(Enum):
    """Represent a file operation."""

    COPY = auto()
    MOVE = auto()
    DRYRUN = auto()


@dataclass(frozen=True)
class DataOperation:
    """Represents a file operation."""

    input_file: pathlib.Path
    output_file: pathlib.Path
    type: FileOperation


OPERATION_FROM_STR = {
    "dryrun": FileOperation.DRYRUN,
    "copy": FileOperation.COPY,
    "move": FileOperation.MOVE,
}


def get_file_hash(filename: pathlib.Path) -> str:
    """Obtain a file hash.

    Args:
        filename: The input file.

    Returns:
        Its hash.
    """
    with filename.open(mode="rb") as f:
        checksum = xxhash.xxh3_64_hexdigest(f.read())
    return checksum


def assert_safe_copy(src: pathlib.Path, dst: pathlib.Path) -> FileCompare:
    """Assert whether the copy operation is safe.

    Args:
        src: The source file.
        dst: The destination file.

    Returns:
        Whether the operation can be safely performed.
    """
    if not dst.exists():
        return FileCompare.NEW

    src_hash = get_file_hash(src)
    dst_hash = get_file_hash(dst)
    if src_hash == dst_hash:
        return FileCompare.SAME
    return FileCompare.DIFFERENT


def perform_operations(data_operation_set: set[DataOperation]) -> set[DataOperation]:
    """Perform the operations.

    Args:
        data_operation_set: The set of operations.

    Returns:
        A set of missed files.
    """
    missed_operations = set()

    for data_operation in data_operation_set:
        logging.info(
            "Performing operation %s from %s to %s.",
            str(data_operation.type),
            data_operation.input_file.as_posix(),
            data_operation.output_file.as_posix(),
        )
        files_status = assert_safe_copy(
            src=data_operation.input_file, dst=data_operation.output_file
        )

        if files_status == FileCompare.SAME:
            logging.info(
                "Duplicate exact copy detected at destination %s, SKIPPING",
                data_operation.output_file.as_posix(),
            )
        elif files_status == FileCompare.DIFFERENT:
            logging.warning(
                (
                    "Duplicate file detected at destination %s,"
                    " but target is different, SKIPPING"
                ),
                data_operation.output_file.as_posix(),
            )
            missed_operations.add(data_operation)
        elif files_status == FileCompare.NEW:
            logging.info(
                "Copying file %s to %s.",
                data_operation.input_file.as_posix(),
                data_operation.output_file.as_posix(),
            )

            if data_operation.type == FileOperation.COPY:
                # Create folder structure if needed:
                output_folder = data_operation.output_file.parent
                if not output_folder.exists():
                    output_folder.mkdir(parents=True, exist_ok=False)

                shutil.copy2(
                    src=data_operation.input_file, dst=data_operation.output_file
                )

    return missed_operations
