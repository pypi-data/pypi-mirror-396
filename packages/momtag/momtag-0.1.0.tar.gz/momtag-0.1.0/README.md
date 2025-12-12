<!--
SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
SPDX-License-Identifier: CC-BY-4.0
-->

# Mike's Opinionated Music Tagger

_Opinions are like arseholes. Everyone's got one, and they all stink._

![](./tags.png)

## What is this?

A tool for:

- recursing a convention of folders and files
- parsing artist, album, and track details from the folder and file names
- finding and processing cover art files
- applying everything as a standard set of tags to your music files

It basically keeps a small collection of music reasonably and consistently organized.

- Every Artist in your collection gets a folder in your Music library.
  How you name them is up to you.
  If you prefer "Who, The", that's fine.

- Every Album in an Artists catalogue gets a folder in the Artist's folder.
  These are named with:
  - a 4-digit year,
  - a space, a hyphen, and a space,
  - then the Album's title.

- Every Track on an Album gets a file in the Album's folder.
  These are named with:
  - a 1–3-digit track number with zero padding if you like,
  - a space, a hyphen, and a space,
  - then the Track's title.

![](./tree.png)


## Why?

I like to purchase my music as MP3s from stores like Bandcamp.
Not everyone uploads their music with well-formatted metadata, and some music labels seem to see fit to use the metadata tags to advertise things like their websites. 
Our car has a USB port in its infotainment system which handles navigation by folder and file name but then displays the tags on the dash display.
The inconsistency _really_ gets on my nerves, but running adverts on songs I've already paid for is simply unacceptable.

## What is this not?

- **A tool for maintaining your carefully curated library of original files.**

  This will delete all the tags from your files and replace them with a basic, standard set of tags.
  Any special metadata you have saved in there will be lost.
  Keep a copy of your original files somewhere else.

- **A tool for tagging your FLACs and your Ogg Vorbis files.** 

  My car doesn't play Ogg Vorbis, so that won't be supported.
  Honestly, if you can tell the difference between V0 MP3s and FLACs while driving, you're probably doing it wrong, and probably twice.

  You probably want [Strawberry Music Player][strawberry] instead.


## Installation

### Debian

TODO: Once we've built the Debian package.


### For Developers

```shell
# Create a virtual environment to store the dependencies
$ python3 -m venv .venv --prompt "momtag"

# Activate the virtual environment to start using it
. .venv/bin/activate # or .venv/bin/activate.fish

# Install the runtime and development dependencies into the virtual environment
pip install -e .[optional]
```


## Running

### Debian

TODO: Once we've built the Debian package.


### pipx or uvx

TODO: Once we've built the PyPI package.


### For Developers

```shell
# Activate the virtual environment to start using it
. .venv/bin/activate # or .venv/bin/activate.fish

# Run the command.
$ momtag --dry-run --verbose ~/Music

# Or, if you want to debug the application, use the supplied main.py script.
$ python main.py
```


## License

### Documentation

momtag's Documentation (C) 2025 by Mike Coats is licensed under Creative Commons Attribution 4.0 International.


### Source Code

momtag - Mike's Opinionated Music Tagger

Copyright (C) 2025 Mike Coats <i.am@mikecoats.com>

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>.


[navidrome]: https://www.navidrome.org/docs/faq/#-can-you-add-a-browsing-by-folder-optionmode-to-navidrome
[strawberry]: https://www.strawberrymusicplayer.org
