# zim-dictionary-server

Serves contents of [ZIM](https://en.wikipedia.org/wiki/ZIM_(file_format)) archives in a way optimized for convenient dictionary lookup.

- Allows looking up a term in multiple ZIM archives simultaneously.
- Automatically looks up the lower-case form of a term given in an upper-case form.
- Allows looking up a term by any of its inflected forms, provided an inflection database or an inflection script.
  (This is useful for quickly copying the term from some text.)

See the [manual](MANUAL.md) for more information.

One notable dictionary available in the ZIM format is [Wiktionary](https://www.wiktionary.org/),
which can be downloaded from the [Wikimedia downloads page](https://dumps.wikimedia.org/)
or from the [Kiwix Library](https://library.kiwix.org/).
Wiktionary ZIM archives can be trimmed and reduced in size
with [wiktionary-zim-trimmer](https://codeberg.org/tomekb234/wiktionary-zim-trimmer).

An inflection database in a format expected by this program can be generated from Wiktionary data
with [wiktionary-inflection-index](https://codeberg.org/tomekb234/wiktionary-inflection-index).
The database may be inconveniently large for some heavily inflected languages (e.g. Finnish),
in which case using an inflection script instead may be a better option.

## Dependencies

- Python 3
- SQLite (optional)
- [python-libzim](https://github.com/openzim/python-libzim), version 3.8 or any compatible

## Installation

This program is distributed on [PyPI](https://pypi.org/),
and the easiest method of installing it is to use [pipx](https://pipx.pypa.io/) —
simply enter the following in the terminal:

```
pipx install zim-dictionary-server
```

You can also manually install the dependencies and run [`zim_dictionary_server.py`](zim_dictionary_server.py) directly.

## Usage

See the [manual](MANUAL.md) for instructions.

For convenience, you may want to add the server as a search engine in your web browser.

You may also want to configure your desktop environment to bind a shortcut for a script which looks up the currently selected text.
Such a script may look for example like this:

```sh
#! /bin/bash

query=$(wl-paste --primary | python -c "from urllib.parse import quote; print(quote(input()))")

url="http://localhost:1111/$query"

if curl --head --fail --no-show-headers --silent "$url"; then
    exec firefox "$url"
else
    notify-send "Not found"
fi
```

## License

This program is released under the GNU Affero General Public License, version 3 or later.
See [LICENSE](LICENSE) for more details.
