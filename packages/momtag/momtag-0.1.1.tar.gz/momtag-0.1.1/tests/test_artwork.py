# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from PIL import Image, ExifTags

from momtag.artwork import art_needs_processing, square_off_art, scale_art, tag_art, process_art


def test_empty_art_needs_processing():
    """Test art_needs_processing returns True when the image has no EXIF tags."""
    im = Image.new('RGB', (100, 100))

    assert art_needs_processing(im) is True


def test_other_art_needs_processing():
    """Test art_needs_processing returns True when the image has a different software tag."""
    im = Image.new('RGB', (100, 100))
    im.getexif()[ExifTags.Base.Software] = 'PotatoShopPro v13.0.1'

    assert art_needs_processing(im) is True


def test_our_art_doesnt_need_processing():
    """Test art_needs_processing returns False when the image has our software tag."""
    im = Image.new('RGB', (100, 100))
    im.getexif()[ExifTags.Base.Software] = 'momtag 0.1.0'

    assert art_needs_processing(im) is False


def test_square_off_square_art():
    """Test square_off_art returns the same image when it's already square."""
    im = Image.new('RGB', (100, 100))
    square = square_off_art(im)

    assert square is im


def test_square_off_wide_art():
    """Test square_off_art returns a cropped image when it's wider than it is tall."""
    im = Image.new('RGB', (200, 100))
    square = square_off_art(im)

    assert square.size == (100, 100)


def test_square_off_tall_art():
    """Test square_off_art returns a cropped image when it's taller than it is wide."""
    im = Image.new('RGB', (100, 200))
    square = square_off_art(im)

    assert square.size == (100, 100)


def test_scale_small_art():
    """Test scale_art returns the same image when it's already small enough."""
    im = Image.new('RGB', (150, 150))
    scaled = scale_art(im)

    assert scaled is im


def test_scale_standard_art():
    """Test scale_art returns the same image when it's already small enough."""
    im = Image.new('RGB', (600, 600))
    scaled = scale_art(im)

    assert scaled is im


def test_scale_between_sizes_art():
    """Test scale_art returns a scaled image when it's between the standard sizes."""
    im = Image.new('RGB', (700, 700))
    scaled = scale_art(im)

    assert scaled.size == (600, 600)


def test_scale_large_art():
    """Test scale_art returns a scaled image when it's larger than the standard sizes."""
    im = Image.new('RGB', (1000, 1000))
    scaled = scale_art(im)

    assert scaled.size == (800, 800)


def test_tag_art_new_image():
    """Test tag_art adds an EXIF tag to a new image."""
    im = Image.new('RGB', (100, 100))

    assert ExifTags.Base.Software not in im.getexif()

    tagged_im = tag_art(im)

    assert ExifTags.Base.Software in tagged_im.getexif()
    assert tagged_im.getexif()[ExifTags.Base.Software].startswith('momtag ')


def test_tag_art_overwrite_image():
    """Test tag_art overwrites an existing EXIF tag on an image."""
    im = Image.new('RGB', (100, 100))
    im.getexif()[ExifTags.Base.Software] = 'PotatoShopPro v13.0.1'

    assert im.getexif()[ExifTags.Base.Software].startswith('momtag ') is False

    tagged_im = tag_art(im)

    assert tagged_im.getexif()[ExifTags.Base.Software].startswith('momtag ')


def test_process_art_rectangular():
    im = Image.new('RGB', (250, 125))
    processed = process_art(im)

    assert processed.size == (125, 125)
    assert processed.getexif()[ExifTags.Base.Software].startswith('momtag ')


def test_process_art_large_square():
    im = Image.new('RGB', (1000, 1000))
    processed = process_art(im)

    assert processed.size == (800, 800)
    assert processed.getexif()[ExifTags.Base.Software].startswith('momtag ')
