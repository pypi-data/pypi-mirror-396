<!--

Copyright (C) 2025 Tomasz Buczyński

This file is a manual for zim-dictionary-server and it is released under the same license as this program.

zim-dictionary-server is free software:
you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
either version 3 of the License, or (at your option) any later version.

zim-dictionary-server is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with zim-dictionary-server.
If not, see <https://www.gnu.org/licenses/>.

-->

# Introduction

**ZIM** is an open file format defined by the [OpenZIM](https://wiki.openzim.org/) project,
designed to store website content and allow offline access to it.
ZIM files, also referred to as ZIM *archives*, can be read with [Kiwix](https://kiwix.org/), a free and open-source offline web browser.
There are [ZIM archives with content of various websites](https://library.kiwix.org/) available to download,
and in particular there are ZIM archives for dictionaries, with [Wiktionary](https://www.wiktionary.org/) as a notable example.

This program, **zim-dictionary-server**, is an alternative to Kiwix specialized for dictionaries.
It runs an HTTP server providing contents of ZIM archives in a way optimized for convenient dictionary lookup.
It opens all `.zim` files in a specified directory and, for each term lookup, finds entries with matching titles in all of these archives simultaneously.

# Command-line interface

Run `zim-dictionary-server -h` to display the usage of the command line interface.

# Term lookup

A term can be looked up by simply giving it in the URL path, e.g.: `http://localhost:1111/apple`

The displayed page can contain multiple entries, each embedded in a separate `<iframe>`.
JavaScript needs to be enabled in the web browser to let the page run a script which adjusts the sizes of these `<iframe>`s to their content
and which makes links inside these `<iframe>`s open in the current tab instead of changing `<iframe>` content.

The looked up term can be given in an upper-case form, in which case the corresponding lower-case form is also looked up.
If an inflection database or an inflection script is provided,
the term can also be given in an inflected form, in which case the canonical form is also looked up.
(There can be multiple terms sharing the same inflected form, in which case all of them are looked up.)

# Inflection

A ZIM archive can be associated with an inflection database and/or an inflection script,
provided as, respectively, an `.inflection.db` file and/or an `.inflection.py` file corresponding to the `.zim` file.

An **inflection database** must be an SQLite database with an `inflection` table with `term` and `form` columns containing only text values.
The table should not have duplicate rows, and it should not have rows in which `term` is equal to `form`.
The database should also have an index on the `form` column.

An **inflection script** must be a Python module with `terms_inflected_into` function, taking a single string argument and returning a list of strings.
The returned list should not have duplicate elements, and it should not contain the string given as the argument.
The function is assumed to return the same result for multiple calls with the same argument, and it is assumed to be thread-safe.
The module is executed on server startup with ZIM archive directory as the working directory.
If the module has a `setup` object, then it is assumed to be a function taking no arguments, and it is called right after executing the module.

# Security

**Warning:** This program uses Python module [`http.server`](https://docs.python.org/3/library/http.server.html),
which is not recommended for production in terms of security.
