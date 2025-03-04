import pathlib

from PIL import Image
from PIL.ExifTags import TAGS


def get_exif_date(
    image_path: pathlib.Path,
) -> tuple[int | None, int | None, int | None]:
    """Obtain exif date.

    Args:
        image_path: The file of the image.

    Returns:
        The year, month and  date in integers.
    """
    # Open the image file
    with Image.open(image_path) as img:
        # Get the EXIF data
        exif_data = img._getexif()

        if exif_data is not None:
            # Iterate through the EXIF data
            for tag, value in exif_data.items():
                tag_name = TAGS.get(tag, tag)
                if tag_name == "DateTimeOriginal":
                    # Extract the date and time
                    date_time_str = value
                    # Split the date and time string
                    date_part, time_part = date_time_str.split(" ")
                    year, month, day = date_part.split(":")
                    return int(year), int(month), int(day)

    return None, None, None


def get_supported_extensions() -> list[str]:
    """Get the list of supported extensions.

    Returns:
        The list of supported extensions.
    """
    # Get the list of supported extensions
    return list(Image.registered_extensions().keys())


def collect_additional_files(filename: pathlib.Path) -> set[pathlib.Path]:
    """Collect other files with the same stem.

    Args:
        filename: The filename.

    Returns:
        A list of all obtained files.
    """
    return set(filename.parent.glob(filename.stem + "*"))
