import argparse
import logging
import pathlib
from itertools import chain

from fstore.exceptions import UnsupportedExtension, UnsupportedOperation
from fstore.operations import (
    OPERATION_FROM_STR,
    DataOperation,
    FileOperation,
    perform_operations,
)
from fstore.scan import scan_files
from fstore.util import (
    collect_additional_files,
    get_exif_date,
    get_supported_extensions,
)


def main() -> None:
    """The main script."""
    parser = argparse.ArgumentParser("Find and archive photo's.")
    parser.add_argument(
        "--input-folder",
        type=pathlib.Path,
        required=True,
        help="The input folder to scan for photo's.",
    )
    parser.add_argument(
        "--output-folder",
        type=pathlib.Path,
        required=True,
        help="The output folder to move the photo's.",
    )
    parser.add_argument(
        "--extensions",
        type=str,
        default=".jpg,.png,.bmp",
        required=False,
        help="The comma-separated list of image extensions to include.",
    )
    parser.add_argument(
        "--operation",
        default="dryrun",
        required=False,
        help="Pass the operation to perform.",
    )
    args = parser.parse_args()

    supported_extensions = get_supported_extensions()

    if args.operation not in ["dryrun", "copy", "move"]:
        raise UnsupportedOperation(
            f"The operation `{args.operation}` is not supported."
        )

    extensions = args.extensions.split(",")
    for ext in extensions:
        if ext.lower() not in supported_extensions:
            raise UnsupportedExtension(
                f"The extension `{ext}` is not supported by pillow."
            )

    file_list = chain(*[scan_files(args.input_folder, ext) for ext in extensions])

    skipped_set = set()
    collected_set = set()

    for filename in file_list:
        file_set = collect_additional_files(filename)

        year, month, day = get_exif_date(filename)
        if year is None or month is None or day is None:
            logging.warn("Skipping file %s", filename.as_posix())
            skipped_set.add(filename)
            continue

        target_folder = args.output_folder / str(year) / str(month)
        include_files_in_collection(
            collection=collected_set,
            include_set=file_set,
            output_folder=target_folder,
            operation=OPERATION_FROM_STR[args.operation],
        )

    missed_operations = perform_operations(data_operation_set=collected_set)

    if missed_operations:
        logging.warning("THERE WHERE MISSED FILES, ARCHIVE INCOMPLETE")
        for data_operation in missed_operations:
            logging.warning("File %s was not copied", data_operation.input_file)


def include_files_in_collection(
    collection: set[DataOperation],
    include_set: set[pathlib.Path],
    output_folder: pathlib.Path,
    operation: FileOperation = FileOperation.DRYRUN,
) -> None:
    """Add files to the collection.

    Args:
        collection: The collection to add the files.
        include_set: The files to include in the collection.
        output_folder: The output directory.
        operation: The file operation to perform.
    """
    for filename in include_set:
        target_file = output_folder / filename.name
        logging.info("Located file %s.", filename)
        collection.add(DataOperation(filename, target_file, operation))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
