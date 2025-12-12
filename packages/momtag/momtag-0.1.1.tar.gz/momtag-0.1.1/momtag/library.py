# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from dataclasses import dataclass
from pathlib import Path
import re


@dataclass
class Track:
    number: int
    title: str
    original_filename: str


@dataclass
class Album:
    year: int
    title: str
    art: str | None
    tracks: list[Track]


@dataclass
class Artist:
    name: str
    albums: list[Album]


def find_artists(music_path: Path) -> list[Artist]:
    """Find all artists in a music folder.

    Args:
        music_path: Path to the music folder.

    Returns:
        A list of Artist objects, sorted by artist name.

    Examples:
        >>> from pathlib import Path  # doctest: +SKIP
        >>> Path('/music/Artist1').mkdir(parents=True)  # doctest: +SKIP
        >>> found_artists = find_artists(Path('/music'))  # doctest: +SKIP
        >>> found_artists[0].name  # doctest: +SKIP
        'Artist1' # doctest: +SKIP
    """
    artists = [
        Artist(artist_dir.name, find_albums(music_path / artist_dir.name))
        for artist_dir in music_path.iterdir()
        if artist_dir.is_dir()
    ]
    return sorted(artists, key=lambda artist: artist.name)


def album_re():
    """Check a folder name for valid Album format.

    Examples:
        >>> match = album_re().match('2018 - Groundbreaking First Album')
        >>> match is not None
        True
    """
    return re.compile(r'^(?P<year>\d{4}) - (?P<title>.+)$')


def find_art(album_path: Path) -> str | None:
    """Search for artwork files in the given album's directory.

    Args:
        album_path: Path to the album directory to search.

    Returns:
        The filename of the first valid artwork file found, or None if no artwork is found.

    Examples:
        >>> from pathlib import Path  # doctest: +SKIP
        >>> Path('/music/Artist1/2001 - Album1/cover.jpg').touch()  # doctest: +SKIP
        >>> find_art(Path('/music/Artist1/2001 - Album1'))  # doctest: +SKIP
        'cover.jpg' # doctest: +SKIP
    """

    # Files we'll accept as valid, in order of preference.
    valid_art_files = [
        'cover.jpg',
        'cover.jpeg',
        'cover.png',
        'folder.jpg',
        'folder.jpeg',
        'folder.png',
    ]

    # For each of our candidate files.
    for file in valid_art_files:
        # Create a candidate file path.
        candidate_art = album_path / file

        # If it exists, return it.
        if candidate_art.is_file():
            return candidate_art.name

    # If none of our candidates exist, return None.
    return None


def find_albums(artist_path: Path) -> list[Album]:
    """Find all albums for an artist in a music folder.

    Args:
        artist_path: Path to the artist's music folder.

    Returns:
        A list of Album objects, sorted by album year and title.

    Examples:
        >>> from pathlib import Path  # doctest: +SKIP
        >>> Path('/music/Artist1/2001 - Album1').mkdir(parents=True)  # doctest: +SKIP
        >>> found_albums = find_albums(Path('/music/Artist1'))  # doctest: +SKIP
        >>> found_albums[0].title  # doctest: +SKIP
        'Album1' # doctest: +SKIP
    """
    candidate_albums = [
        candidate_dir.name for candidate_dir in artist_path.iterdir() if candidate_dir.is_dir()
    ]
    album_matches = [album_re().match(candidate_dir) for candidate_dir in candidate_albums]
    albums = [
        Album(
            int(m.group('year')),
            m.group('title'),
            find_art(artist_path / m.string),
            find_tracks(artist_path / m.string),
        )
        for m in album_matches
        if m
    ]
    return sorted(albums, key=lambda album: f'{album.year}{album.title}')


def track_re():
    """Check a folder name for valid Track format.

    Examples:
        >>> match = track_re().match('1 - Test.mp3')
        >>> match is not None
        True
    """
    return re.compile(r'^(?P<number>\d+) - (?P<title>.+)\.mp3$')


def find_tracks(album_path: Path) -> list[Track]:
    """Find all tracks for an album in a music folder.

    Args:
        album_path: Path to the album's music folder.

    Returns:
        A list of Track objects, sorted by track number and title.

    Examples:
        >>> from pathlib import Path  # doctest: +SKIP
        >>> Path('/music/Artist1/2001 - Album1/01 - Good Ext.mp3').touch()  # doctest: +SKIP
        >>> found_tracks = find_tracks(Path('/music/Artist1/2001 - Album1/'))  # doctest: +SKIP
        >>> found_tracks[0].number  # doctest: +SKIP
        1  # doctest: +SKIP
        >>> found_tracks[0].title  # doctest: +SKIP
        'Good Ext' # doctest: +SKIP
    """
    candidate_tracks = [file.name for file in album_path.iterdir() if file.is_file()]
    track_matches = [track_re().match(file) for file in candidate_tracks]
    tracks = [
        Track(int(m.group('number')), m.group('title'), m.group(0)) for m in track_matches if m
    ]
    return sorted(tracks, key=lambda track: f'{track.number:03d}{track.title}')
