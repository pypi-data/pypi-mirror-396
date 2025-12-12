# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

from io import BytesIO
from pathlib import Path

import click
from PIL import Image
from mutagen.mp3 import MP3

from momtag.artwork import art_needs_processing, process_art
from momtag.library import Artist, find_artists
from momtag.track import track_needs_processing, process_track


def build_library(music_path: Path) -> list[Artist]:
    """Build a model of the music library."""
    artists = find_artists(music_path)
    return artists


def process_library_art(
    music_path: Path, library: list[Artist], dry_run: bool, verbose: bool, force: bool
):
    click.echo('Processing art...') if verbose else None
    for artist in library:
        for album in artist.albums:
            if album.art:
                art_path = music_path / artist.name / f'{album.year} - {album.title}' / album.art
                click.echo(f'Found {art_path} ...') if verbose else None
                im = Image.open(art_path)
                needs_processing = art_needs_processing(im)
                if needs_processing or force:
                    click.echo('  ... which needs processing.') if verbose else None
                    if not dry_run:
                        new_im = process_art(im)
                        new_im.save(art_path, exif=im.getexif())
                        click.echo('  Processed.') if verbose else None


def process_library_tracks(
    music_path: Path, library: list[Artist], dry_run: bool, verbose: bool, force: bool
):
    click.echo('Processing tracks...') if verbose else None
    for artist in library:
        for album in artist.albums:
            img_data = None
            if album.art:
                art_path = music_path / artist.name / f'{album.year} - {album.title}' / album.art
                click.echo(f'Found {art_path} ...') if verbose else None
                im = Image.open(art_path)

                buf = BytesIO()
                im.save(buf, format='JPEG')
                img_data = buf.getvalue()

            for track in album.tracks:
                track_path = (
                    music_path
                    / artist.name
                    / f'{album.year} - {album.title}'
                    / track.original_filename
                )
                click.echo(f'Found {track_path} ...') if verbose else None

                # Open the original file.
                mp3 = MP3(track_path)

                needs_processing = track_needs_processing(mp3)

                if needs_processing or force:
                    click.echo('  ... which needs processing.') if verbose else None
                    if not dry_run:
                        new_track = process_track(mp3, artist, album, track, img_data)
                        new_track.save(track_path)
                        click.echo('  Processed.') if verbose else None


@click.command()
@click.option('--verbose', is_flag=True)
@click.option('--dry-run', is_flag=True)
@click.option('--force', is_flag=True)
@click.argument('music_path', type=click.Path(exists=True, file_okay=False, path_type=Path))
def cli(music_path: Path, verbose=False, dry_run=False, force=False):
    if dry_run and force:
        raise click.UsageError('--dry-run and --force are mutually exclusive.')

    library = build_library(music_path)
    process_library_art(music_path, library, dry_run, verbose, force)
    process_library_tracks(music_path, library, dry_run, verbose, force)
