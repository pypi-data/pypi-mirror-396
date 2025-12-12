<!--
SPDX-FileCopyrightText: 2025 Mike Coats <i.am@mikecoats.com>
SPDX-License-Identifier: CC-BY-4.0
-->

# Contributing

## Installing

```shell
# Create a virtual environment to isolate the project's dependencies.
$ python3 -m venv .venv --prompt=momtag

# Activate the virtual environment to start using it.
$ . .venv/bin/activate # or .venv/bin/activate.fish

# Install the project's dependencies, including the optional ones like unit-testing, linting and
# formatting.
$ pip install -e .[optional]
```

## Running

```shell
# Make sure you're working within the virtual environment.
$ . .venv/bin/activate # or .venv/bin/activate.fish

# Run the command.
$ momtag --dry-run --verbose ~/Music

# Or, if you want to debug the application, use the supplied main.py script.
$ python main.py
```

## Linting and Testing

```shell
$ pytest
$ ruff format
$ ruff check --fix
$ ty check
$ reuse lint
```

Add yourself to the list of authors in pyproject.toml.

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -9,6 +9,7 @@ readme = "README.md"
 keywords = []
 authors = [
     { name = "Mike Coats", email = "i.am@mikecoats.com" },
+    { name = "Joe Bloggs", email = "joe.bloggs@example.org" },
 ]
 license = "GPL-3.0-or-later"
 license-files = ["LICEN[CS]ES/*"]
```

## Publishing to PyPI

Update the version number in pyproject.toml.

```diff
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -3,7 +3,7 @@

 [project]
 name = "momtag"
-version = "0.1.1"
+version = "1.2.3"
 description = "Mike's Opinionated Music Tagger"
 readme = "README.md"
 keywords = []
```

```shell
# Build the packages for PyPI.
$ python3 -m build

# Upload the packages to PyPI.
$ python3 -m twine upload dist/*
```
