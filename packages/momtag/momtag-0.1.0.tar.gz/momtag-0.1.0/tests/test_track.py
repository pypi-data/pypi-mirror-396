# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

import base64
from io import BytesIO

import pytest
from PIL import Image
from mutagen.mp3 import MP3

from momtag.artwork import process_art
from momtag.library import Artist, Album, Track
from momtag.track import track_needs_processing, process_track


@pytest.fixture
def empty_mp3():
    return MP3(
        BytesIO(
            base64.b64decode(
                b'//MUxAAAAANIAAAAAExBTUUzLjEwMFVV//MUxAsAAANIAAAAAFVVVVVVVVVVVVVV//MUxBYAAANIAAAAAFVV'
                b'VVVVVVVVVVVV//MUxCEAAANIAAAAAFVVVVVVVVVVVVVV//MUxCwAAANIAAAAAFVVVVVVVVVVVVVV//MUxDcA'
                b'AANIAAAAAFVVVVVVVVVVVVVV//MUxEIAAANIAAAAAFVVVVVVVVVVVVVV'
            )
        )
    )


@pytest.fixture
def unclaimed_mp3():
    return MP3(
        BytesIO(
            base64.b64decode(
                b'SUQzBABAAAAANwAAAAwBIAUGEAg6MFRJVDIAAAALAAAARGVtbyBUcmFja1RQRTEAAAAMAAAARGVtbyBBcnRp'
                b'c3T/8xTEAAAAA0gAAAAATEFNRTMuMTAwVVX/8xTECwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEFgAAA0gAAAAA'
                b'VVVVVVVVVVVVVVX/8xTEIQAAA0gAAAAAVVVVVVVVVVVVVVX/8xTELAAAA0gAAAAAVVVVVVVVVVVVVVX/8xTE'
                b'NwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEQgAAA0gAAAAAVVVVVVVVVVVVVVU='
            )
        )
    )


@pytest.fixture
def not_us_mp3():
    return MP3(
        BytesIO(
            base64.b64decode(
                b'SUQzBAAAAAAAWlRJVDIAAAAMAAAARGVtbyBUcmFjawBUUEUxAAAADQAAAERlbW8gQXJ0aXN0AFRFTkMAAAAP'
                b'AAADVGVtZXJpdHkgdjMuNwAAAAAAAAAAAAAAAAAAAAAAAAAAAP/zFMQAAAADSAAAAABMQU1FMy4xMDBVVf/z'
                b'FMQLAAADSAAAAABVVVVVVVVVVVVVVf/zFMQWAAADSAAAAABVVVVVVVVVVVVVVf/zFMQhAAADSAAAAABVVVVV'
                b'VVVVVVVVVf/zFMQsAAADSAAAAABVVVVVVVVVVVVVVf/zFMQ3AAADSAAAAABVVVVVVVVVVVVVVf/zFMRCAAAD'
                b'SAAAAABVVVVVVVVVVVVVVQ=='
            )
        )
    )


@pytest.fixture
def completed_mp3():
    return MP3(
        BytesIO(
            base64.b64decode(
                b'SUQzBAAAAAAAWFRJVDIAAAAMAAAARGVtbyBUcmFjawBUUEUxAAAADQAAAERlbW8gQXJ0aXN0AFRFTkMAAAAN'
                b'AAADbW9tdGFnIHYwLjEAAAAAAAAAAAAAAAAAAAAAAAAAAAD/8xTEAAAAA0gAAAAATEFNRTMuMTAwVVX/8xTE'
                b'CwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEFgAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEIQAAA0gAAAAAVVVVVVVV'
                b'VVVVVVX/8xTELAAAA0gAAAAAVVVVVVVVVVVVVVX/8xTENwAAA0gAAAAAVVVVVVVVVVVVVVX/8xTEQgAAA0gA'
                b'AAAAVVVVVVVVVVVVVVU='
            )
        )
    )


@pytest.fixture
def demo_art():
    demo_art = BytesIO()
    process_art(Image.new('RGB', (100, 100))).save(demo_art, format='JPEG')
    return demo_art


def test_empty_track_needs_processing(empty_mp3):
    """Test track_needs_processing returns True when the track has no metadata."""
    assert track_needs_processing(empty_mp3) is True


def test_no_maker_track_needs_processing(unclaimed_mp3):
    """Test track_needs_processing returns True when the track has no maker metadata."""
    assert track_needs_processing(unclaimed_mp3) is True


def test_other_maker_track_needs_processing(not_us_mp3):
    """Test track_needs_processing returns True when the track has a different maker metadata."""
    assert track_needs_processing(not_us_mp3) is True


def test_our_track_doesnt_need_processing(completed_mp3):
    """Test track_needs_processing returns False when the track has our maker metadata."""
    assert track_needs_processing(completed_mp3) is False


def test_process_track(not_us_mp3, demo_art):
    """Test process_track adds the correct metadata to the track."""
    mp3 = not_us_mp3
    track = Track(1, 'Test Track', '01 - Test Track.mp3')
    album = Album(2001, 'Test Album', 'cover.jpg', [track])
    artist = Artist('Test Artist', [album])
    image_data = demo_art.getvalue()
    processed = process_track(mp3, artist, album, track, image_data)

    assert processed.tags is not None
    assert processed.tags.get('TRCK') == '1/1'
    assert processed.tags.get('TIT2') == 'Test Track'
    assert processed.tags.get('TDRC') == '2001'
    assert processed.tags.get('TALB') == 'Test Album'
    assert processed.tags.get('APIC:Cover') is not None
    assert processed.tags.get('APIC:Cover').data == image_data
    assert processed.tags.get('TPE1') == 'Test Artist'
    assert str(processed.tags.get('TENC')).startswith('momtag ')


def test_need_process_need_roundtrip(not_us_mp3, demo_art):
    mp3 = not_us_mp3

    assert track_needs_processing(mp3) is True

    track = Track(1, 'Test Track', '01 - Test Track.mp3')
    album = Album(2001, 'Test Album', 'cover.jpg', [track])
    artist = Artist('Test Artist', [album])
    image_data = demo_art.getvalue()
    processed = process_track(mp3, artist, album, track, image_data)

    assert track_needs_processing(processed) is False


def test_process_track_no_img(not_us_mp3):
    """Test process_track adds metadata except Artwork, when None, to the track."""
    mp3 = not_us_mp3
    track = Track(1, 'Test Track', '01 - Test Track.mp3')
    album = Album(2001, 'Test Album', 'cover.jpg', [track])
    artist = Artist('Test Artist', [album])
    image_data = None
    processed = process_track(mp3, artist, album, track, image_data)

    assert processed.tags is not None
    assert processed.tags.get('TRCK') == '1/1'
    assert processed.tags.get('TIT2') == 'Test Track'
    assert processed.tags.get('TDRC') == '2001'
    assert processed.tags.get('TALB') == 'Test Album'
    assert processed.tags.get('APIC:Cover') is None
    assert processed.tags.get('TPE1') == 'Test Artist'
    assert str(processed.tags.get('TENC')).startswith('momtag ')
