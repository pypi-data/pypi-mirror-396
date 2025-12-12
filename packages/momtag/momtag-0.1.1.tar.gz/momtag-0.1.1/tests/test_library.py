# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from pathlib import Path

from momtag.library import find_artists, album_re, find_albums, find_art, track_re, find_tracks


def test_find_artists_no_artists(fs):
    """Test find_artists returns an empty list when no artist directories exist."""
    fs.create_file('/music/track.mp3')

    artists = find_artists(Path('/music/'))

    assert len(artists) == 0


def test_find_artists_two_artists(fs):
    """Test find_artists returns correct artist names when multiple artists exist."""
    fs.create_file('/music/artist 1/file_id.diz')
    fs.create_file('/music/artist 2/artist_2.nfo')

    artists = find_artists(Path('/music/'))

    assert len(artists) == 2

    assert artists[0].name == 'artist 1'
    assert len(artists[0].albums) == 0
    assert artists[1].name == 'artist 2'
    assert len(artists[1].albums) == 0


def test_album_re_no_match():
    """Test album_re returns None when the candidate album doesn't match the expected format."""
    match = album_re().match('012 - Broken Year')

    assert match is None


def test_album_re_match():
    """Test album_re returns correct information when the candidate album matches the expected format."""
    match = album_re().match('2018 - Groundbreaking First Album')

    assert match is not None
    assert match.group('year') == '2018'
    assert match.group('title') == 'Groundbreaking First Album'


def test_find_albums_no_albums(fs):
    """Test find_albums returns an empty list when no album directories exist."""
    fs.create_file('/music/artist 1/file_id.diz')

    albums = find_albums(Path('/music/artist 1'))

    assert len(albums) == 0


def test_find_albums_one_correct_album(fs):
    """Test find_albums returns correct album information when one album matches the expected format."""
    fs.create_file('/music/artist 1/99 - album 1/file_id.diz')
    fs.create_file('/music/artist 1/2002 - album 2/file_id.diz')

    albums = find_albums(Path('/music/artist 1'))

    assert len(albums) == 1

    assert albums[0].year == 2002
    assert albums[0].title == 'album 2'


def test_find_albums_two_albums(fs):
    """Test find_albums returns correct album information when multiple albums match the expected format."""
    fs.create_file('/music/artist 1/2001 - album 1/file_id.diz')
    fs.create_file('/music/artist 1/2002 - album 2/file_id.diz')

    albums = find_albums(Path('/music/artist 1'))

    assert len(albums) == 2

    assert albums[0].year == 2001
    assert albums[0].title == 'album 1'
    assert albums[1].year == 2002
    assert albums[1].title == 'album 2'


def test_find_albums_within_artists(fs):
    """Test find_artists returns correct album information when albums exist within artists."""
    fs.create_file('/music/artist 1/2001 - album 1/file_id.diz')

    artists = find_artists(Path('/music/'))

    assert len(artists) == 1
    assert len(artists[0].albums) == 1
    assert artists[0].albums[0].year == 2001
    assert artists[0].albums[0].title == 'album 1'


def test_find_art_no_art(fs):
    """Test find_art returns None when no artwork files exist."""
    fs.create_file('/music/artist/2000 - album/01 - track.mp3')

    assert find_art(Path('/music/artist/2000 - album')) is None


def test_find_art_one_art(fs):
    """Test find_art returns the correct filename when one artwork file exists."""
    fs.create_file('/music/artist/2000 - album/cover.jpg')

    assert find_art(Path('/music/artist/2000 - album')) == 'cover.jpg'


def test_find_art_first_choice_art(fs):
    """Test find_art returns the preferred filename when multiple artwork files exist."""
    fs.create_file('/music/artist/2000 - album/cover.jpeg')
    fs.create_file('/music/artist/2000 - album/folder.png')
    fs.create_file('/music/artist/2000 - album/cover.jpg')

    assert find_art(Path('/music/artist/2000 - album')) == 'cover.jpg'


def test_find_no_art_in_album_without(fs):
    """Test find_albums returns None when albums with no artwork exist."""
    fs.create_file('/music/artist 1/2001 - album 1/file_id.diz')

    albums = find_albums(Path('/music/artist 1'))

    assert albums[0].art is None


def test_find_art_within_albums(fs):
    """Test find_albums returns correct artwork information when albums with artwork exist."""
    fs.create_file('/music/artist/2000 - album/cover.jpg')

    albums = find_albums(Path('/music/artist'))

    assert albums[0].art == 'cover.jpg'


def test_track_re_no_match():
    """Test track_re returns None when the candidate track doesn't match the expected format."""
    match = track_re().match('01 - Broken Extension.flac')

    assert match is None


def test_track_re_match():
    """Test track_re returns correct information when the candidate track matches the expected format."""
    match = track_re().match('01 - Good Ext.mp3')

    assert match is not None
    assert match.group('number') == '01'
    assert match.group('title') == 'Good Ext'


def test_find_tracks_no_tracks(fs):
    """Test find_tracks returns an empty list when no tracks exist."""
    fs.create_file('/music/artist 1/2001 - album 1/file_id.diz')

    tracks = find_tracks(Path('/music/artist 1/2001 - album 1/'))

    assert len(tracks) == 0


def test_find_tracks_one_correct_track(fs):
    """Test find_tracks returns correct track information when one file matches the expected format."""
    fs.create_file('/music/artist 1/2001 - album 1/file_id.diz')
    fs.create_file('/music/artist 1/2001 - album 1/1 - test track.mp3')

    tracks = find_tracks(Path('/music/artist 1/2001 - album 1/'))

    assert len(tracks) == 1

    assert tracks[0].number == 1
    assert tracks[0].title == 'test track'
    assert tracks[0].original_filename == '1 - test track.mp3'


def test_find_tracks_two_tracks(fs):
    """Test find_tracks returns correct track information when multiple files match the expected format."""
    fs.create_file('/music/artist 1/2001 - album 1/1 - test track.mp3')
    fs.create_file('/music/artist 1/2001 - album 1/2 - second track.mp3')

    tracks = find_tracks(Path('/music/artist 1/2001 - album 1/'))

    assert len(tracks) == 2

    assert tracks[0].number == 1
    assert tracks[0].title == 'test track'
    assert tracks[0].original_filename == '1 - test track.mp3'
    assert tracks[1].number == 2
    assert tracks[1].title == 'second track'
    assert tracks[1].original_filename == '2 - second track.mp3'


def test_find_tracks_within_albums(fs):
    """Test find_tracks returns correct track information when tracks exist within albums."""
    fs.create_file('/music/artist 1/2001 - album 1/01 - test track.mp3')

    albums = find_albums(Path('/music/artist 1/'))

    assert len(albums) == 1
    assert len(albums[0].tracks) == 1
    assert albums[0].tracks[0].number == 1
    assert albums[0].tracks[0].title == 'test track'


def test_find_tracks_within_artists(fs):
    """Test find_tracks returns correct track information when tracks exist within albums within artists."""
    fs.create_file('/music/artist 1/2001 - album 1/01 - test track.mp3')

    artists = find_artists(Path('/music/'))

    assert len(artists) == 1
    assert len(artists[0].albums) == 1
    assert len(artists[0].albums[0].tracks) == 1
    assert artists[0].albums[0].tracks[0].number == 1
    assert artists[0].albums[0].tracks[0].title == 'test track'
