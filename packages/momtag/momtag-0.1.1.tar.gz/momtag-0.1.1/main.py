# SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
# SPDX-License-Identifier: GPL-3.0-or-later

"""The dev-mode-only entry point.

It's useful if you need to run the CLI from an IDE for debugging and introspection. Most people
should be running the "momtag" command that pip/pyproject installs. I'm pretty sure this file
shouldn't even be packaged, and it certainly shouldn't be generally accessible by users. It's a
hack, really.
"""

from pathlib import Path

from momtag.momtag import cli

if __name__ == '__main__':
    cli(
        [
            '--verbose',
            '--dry-run',
            str(Path.home() / 'Music'),
        ]
    )
