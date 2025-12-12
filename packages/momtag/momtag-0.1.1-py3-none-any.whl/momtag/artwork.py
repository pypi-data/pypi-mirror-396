# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from PIL import Image, ExifTags


def art_needs_processing(art: Image.Image) -> bool:
    """Check if artwork needs to be processed based on EXIF software tag.

    Args:
        art: Image to check for a processing need.

    Returns:
        True if the image needs processing, False if it has already been processed.

    Examples:
        A new image with no EXIF tags needs processing:
        >>> im = Image.new('RGB', (100, 100))
        >>> art_needs_processing(im)
        True
    """
    exif = art.getexif()

    # If the art file has our tag, it doesn't need processing.
    if ExifTags.Base.Software in exif and exif[ExifTags.Base.Software].startswith('momtag '):
        return False

    return True


def square_off_art(art: Image.Image) -> Image.Image:
    """Crop artwork to make it square by removing excess width or height from the edges.

    Args:
        art: Image to crop if needed.

    Returns:
        The cropped image if it was rectangular, or the original image if it was already square.

    Examples:
        A wide image is cropped from the center:
        >>> square_off_art(Image.new('RGB', (200, 100))).size
        (100, 100)
    """

    # Grab the image's dimensions.
    width, height = art.size

    # If the image is already square, return it unchanged.
    if width == height:
        return art

    # If the image is wider than it is tall...
    if width > height:
        # Calculate the offset to center the image horizontally.
        x_offset = (width - height) // 2

        # Crop the image out of the middle.
        return art.crop((x_offset, 0, x_offset + height, height))

    # If the image is taller than it is wide...
    # Calculate the offset to center the image vertically.
    y_offset = (height - width) // 2

    # Crop the image out of the middle.
    return art.crop((0, y_offset, width, y_offset + width))


def scale_art(art: Image.Image) -> Image.Image:
    """Resize artwork to standard dimensions if it exceeds standard sizes.

    Args:
        art: Image to resize if needed.

    Returns:
        The resized image if it exceeded standard sizes, or the original image if no resizing was
        needed.

    Examples:
        An image between standard sizes is resized to the next smaller size:
        >>> scale_art(Image.new('RGB', (700, 700))).size
        (600, 600)
    """

    # Sizes we're happy with, in order of preference.
    standard_sizes = [
        800,
        600,
        300,
        200,
    ]

    # If the image is already in one of our standard sizes, return it unchanged.
    if art.size[0] in standard_sizes:
        return art

    # For each of our standard sizes...
    for candidate_size in standard_sizes:
        # If the image is larger than our candidate size...
        if art.size[0] > candidate_size:
            # Resize it to the candidate size and return it.
            art.thumbnail((candidate_size, candidate_size))
            return art

    # If our image is smaller than any of our standard sizes, return it unchanged.
    return art


def tag_art(art: Image.Image) -> Image.Image:
    """Tag an image with our application's name in the EXIF Software field.

    Args:
        art: Image to tag.

    Returns:
        The tagged image, with our application name set in its EXIF Software field.

    Examples:
        Set a tag with our app's name:
        >>> tag_art(Image.new('RGB', (100, 100))).getexif()[ExifTags.Base.Software].startswith(
        ...     'momtag '
        ... )
        True
    """

    # Grab the bag of tags.
    exif = art.getexif()

    # Set our app's name in the Software field.
    exif[ExifTags.Base.Software] = 'momtag 0.1'

    # Return the image with the updated tags.
    return art


def process_art(art: Image.Image) -> Image.Image:
    """Apply standard artwork processing steps: squaring, resizing, and tagging.

    Args:
        art: Image to process.

    Returns:
        The processed image, with all standard transformations applied.

    Examples:
        A rectangular image is made square, resized only if needed, and tagged:
        >>> im = Image.new('RGB', (250, 125))
        >>> processed = process_art(im)
        >>> processed.size
        (125, 125)
        >>> processed.getexif()[ExifTags.Base.Software].startswith('momtag ')
        True
    """

    # Square off the image, if needed.
    squared = square_off_art(art)

    # Resize the image, if needed.
    sized = scale_art(squared)

    # Tag the image with our app's name.
    tagged = tag_art(sized)

    # Return the processed image.
    return tagged
