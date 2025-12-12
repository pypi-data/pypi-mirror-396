# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from mutagen.id3 import TPE1, TDRC, TALB, TRCK, TIT2, APIC, PictureType, TENC, ID3
from mutagen.mp3 import MP3

from momtag.library import Artist, Album, Track


def track_needs_processing(mp3: MP3) -> bool:
    """Check if a track needs to be processed based on the TENC ID3 tag.

    Args:
        mp3: MP3 to check for a processing need.

    Returns:
        True if the track needs processing, False if it has already been processed.
    """

    # If the file exists without any tags, we must process it.
    if mp3.tags is None:
        return True

    # If the file has tags, but no "TENC" tag, we should process it.
    if 'TENC' not in mp3.tags:
        return True

    # If the file has tags, and the "TENC" tag is only set to "momtag", we don't need to process it.
    if len(mp3.tags.get('TENC').text) == 1 and mp3.tags.get('TENC').text[0].startswith('momtag '):
        return False

    return True


def process_track(
    mp3: MP3, artist: Artist, album: Album, track: Track, image_data: bytes | None
) -> MP3:
    """Add metadata to an MP3 file, including cover art.

    Args:
        mp3: MP3 file to process.
        artist: Artist to tag the track with.
        album: Album to tag the track with.
        track: Track to tag the file with.
        image_data: Cover art to add to the file.

    Returns:
        The processed MP3 file.

    Examples:
        >>> mp3 = # Loaded with Mutagen from somewhere # doctest: +SKIP
        >>> track = Track(1, 'Test Track', '01 - Test Track.mp3')  # doctest: +SKIP
        >>> album = Album(2001, 'Test Album', 'cover.jpg', [track])  # doctest: +SKIP
        >>> artist = Artist('Test Artist', [album])  # doctest: +SKIP
        >>> image_data = # Loaded with Pillow from somewhere # doctest: +SKIP
        >>> processed = process_track(mp3, artist, album, track, image_data)  # doctest: +SKIP
        >>> str(processed.tags.get('TENC'))  # doctest: +SKIP
        'momtag 0.1' # doctest: +SKIP
    """
    # If the file already has tags, delete them.
    if mp3.tags is not None:
        mp3.tags.clear()

    # If the file has no tags, add them.
    if mp3.tags is None:
        mp3.add_tags()

    # If by this point the file still has no tags, we can't process it.'
    if not isinstance(mp3.tags, ID3):
        return mp3

    mp3.tags.add(TPE1(encoding=3, text=artist.name))
    mp3.tags.add(TDRC(encoding=3, text=str(album.year)))
    mp3.tags.add(TALB(encoding=3, text=album.title))
    mp3.tags.add(TRCK(encoding=3, text=f'{track.number}/{len(album.tracks)}'))
    mp3.tags.add(TIT2(encoding=3, text=track.title))

    if image_data is not None:
        # Add our cover art.
        mp3.tags.add(
            APIC(
                encoding=3,
                mime='image/jpeg',
                type=PictureType.COVER_FRONT,
                desc='Cover',
                data=image_data,
            )
        )

    # Add our processing tag.
    mp3.tags.add(TENC(encoding=3, text='momtag 0.1'))

    # Return the processed track.
    return mp3
