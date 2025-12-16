#! /usr/bin/env python3
#
# zim-dictionary-server
#
# Copyright (C) 2025 Tomasz Buczyński
#
# This program is free software:
# you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along with this program.
# If not, see <https://www.gnu.org/licenses/>.

"""Serves contents of ZIM archives in a way optimized for convenient dictionary lookup."""

__version__ = "1.0.1"

import sys
import io
import os
import os.path
import contextlib
import importlib.util
import random
import re
import argparse
import urllib.parse
import html
import http
import http.server
import libzim.reader

with contextlib.suppress(ImportError):
    import sqlite3

repository_url = "https://codeberg.org/tomekb234/zim-dictionary-server"

# Default options

default_dir  = "~/.dict"
default_host = "127.0.0.1"
default_port = 1111
default_content_prefix = "/_content"

# Command-line argument parsing function

def parse_args():
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=f"The program's manual is available in the project's repository: {repository_url}"
    )

    parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-d", "--dir", metavar="PATH", help=f"Path of a directory with ZIM archives to serve (default: {default_dir})")
    parser.add_argument("-H", "--host",           default=default_host, help="Host to bind the server to (default: %(default)s)")
    parser.add_argument("-p", "--port", type=int, default=default_port, help="Port to bind the server to (default: %(default)s)")
    parser.add_argument("-C", "--content-prefix", default=default_content_prefix, metavar="RESOURCE-PATH",
                        help="Resource path prefix to use for ZIM archive content (default: %(default)s)")
    parser.add_argument("-l", "--log", action="store_true", help="Enable logging into to the standard error stream")

    return parser.parse_args()

# Resources embedded in the served HTML

style_css = """\
body { margin: 0; }
iframe { width: 100%; border: none; }"
"""

frame_script_js = """\
for (const frame of document.querySelectorAll("iframe")) {
    frame.onload = () => {
        const document = frame.contentDocument;

        const base = document.createElement("base");
        base.target = "_parent";
        document.head.appendChild(base);

        new ResizeObserver(() => {
            frame.height = 0;
            frame.height = document.documentElement.scrollHeight + 1;
        }).observe(document.documentElement);
    };
}
"""

icon_svg = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
    <rect x="10" y="0"  width="80" height="100" fill="dimgray"/>
    <rect x="20" y="90" width="70" height="10"  fill="silver"/>
    <text x="15" y="55" font-family="FreeSans, Helvetica, Arial" font-size="55" fill="white">A</text>
    <text x="50" y="75" font-family="FreeSans, Helvetica, Arial" font-size="55" fill="white">Z</text>
</svg>
"""

# Main server setup function

def setup_server(dir, host, port, content_prefix, enable_logging):
    # Open all ZIM archives, inflection databases and inflection scripts in the specified directory.

    archives = {}
    inflection_dbs = {}
    inflection_scripts = {}

    with contextlib.chdir(dir):
        for file in os.scandir():
            if match := re.fullmatch(r"(.*)\.zim", file.name):
                archives[match[1]] = libzim.reader.Archive(file.path)

            elif match := re.fullmatch(r"(.*)\.inflection.db", file.name):
                if "sqlite3" in globals():
                    inflection_dbs[match[1]] = sqlite3.connect("file:{}?mode=ro".format(urllib.parse.quote(file.path)), uri=True, check_same_thread=False)
                else:
                    raise Exception("Found an .inflection.db file but SQLite is not available")

            elif match := re.fullmatch(r"(.*)\.inflection.py", file.name):
                spec = importlib.util.spec_from_file_location("inflection", file.path)
                module = importlib.util.module_from_spec(spec)
                inflection_scripts[match[1]] = module

                spec.loader.exec_module(module)

                if hasattr(module, "setup"):
                    module.setup()

    if not archives:
        raise Exception("No .zim files found")

    # Obtain archive titles.

    archive_titles = {}

    for name, archive in archives.items():
        try:
            archive_titles[name] = archive.get_metadata("Title").decode(errors="replace")
        except RuntimeError:
            archive_titles[name] = name

    # ZIM archive access functions

    def look_up(term):
        result = []
        lower = term.lower()

        for name, archive in sorted(archives.items()):
            def look_up_in_archive_exact(term):
                with contextlib.suppress(KeyError):
                    result.append((name, term, archive.get_entry_by_title(term).path))

            def look_up_in_archive(term):
                look_up_in_archive_exact(term)

                terms = []

                if inflection_db := inflection_dbs.get(name):
                    terms.extend(term for (term,) in inflection_db.execute("select term from inflection where form = ?", (term,)))

                if inflection_script := inflection_scripts.get(name):
                    terms.extend(inflection_script.terms_inflected_into(term))

                terms.sort()

                for term in terms:
                    look_up_in_archive_exact(term)

            look_up_in_archive(term)

            if lower != term:
                look_up_in_archive(lower)

        return result

    def get_archive_content(name, path):
        try:
            archive = archives[name]
        except KeyError:
            return None

        try:
            item = archive.get_entry_by_path(path).get_item()
            return item.mimetype, item.content
        except KeyError:
            return None

    # Page generation functions

    def page_writer():
        page = io.StringIO()

        def write(text):
            page.write(text)
            page.write("\n")

        def get_bytes():
            return page.getvalue().encode()

        return write, get_bytes

    def generate_main_page():
        write, get_bytes = page_writer()

        write("<!doctype html>")
        write("<html lang=en>")

        write("<head>")
        write("<title>Dictionary</title>")
        write("<link rel=icon href='data:image/svg+xml,\n{}'>".format(icon_svg))
        write("</head>")

        write("<body>")
        write("<h1>Dictionary</h1>")

        write("<p>Archives served:</p>")
        write("<ul>")

        for name in sorted(archives):
            write("<li>{}</li>".format(html.escape(archive_titles[name])))

        write("</ul>")

        write("<p>A term can be looked up by simply giving it in the URL path, e.g.: <a href=/apple title='Example lookup'>/apple</a></p>")
        write("<noscript><p><strong>JavaScript needs to be enabled for lookup pages to display correctly.</strong></p></noscript>")
        write("<p><a href='{}'>Server's source code</a></p>".format(html.escape(repository_url)))

        return get_bytes()

    def generate_lookup_page(term):
        result = look_up(term)

        if not result:
            return None

        write, get_bytes = page_writer()

        write("<!doctype html>")
        write("<html>")

        write("<head>")
        write("<title>{}</title>".format(html.escape(term)))
        write("<link rel=icon href='data:image/svg+xml,\n{}'>".format(icon_svg))
        write("<style>\n{}</style>".format(style_css))
        write("</head>")

        write("<body>")
        write("<noscript><p style='text-align: center;'><strong>JavaScript needs to be enabled for this page to display correctly.</strong></p></noscript>")

        for name, title, path in result:
            write("<iframe src='{}/{}/{}' title='{} — {}'></iframe>".format(
                html.escape(content_prefix),
                html.escape(name),
                html.escape(path),
                html.escape(title),
                html.escape(archive_titles[name]),
            ))

        write("<script>\n{}</script>".format(frame_script_js))

        return get_bytes()

    # Generate random ETag for client-side caching.

    etag = "\"{}\"".format(random.randbytes(8).hex())

    # HTTP request handler

    class Handler(http.server.BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self):
            if etag in self.headers.get("If-None-Match", "").split(", "):
                self.send_not_modified()
                return

            if not self.path.startswith("/"):
                self.send_bad_request()
            elif self.path == "/":
                self.do_display_main_page()
            elif self.path.startswith(content_prefix):
                self.do_get_archive_content()
            else:
                self.do_look_up()

        do_HEAD = do_GET

        def do_display_main_page(self):
            page = generate_main_page()
            self.send_ok("text/html; charset=utf-8", page)

        def do_look_up(self):
            term = urllib.parse.unquote(self.path[1:])
            page = generate_lookup_page(term)

            if page is not None:
                self.send_ok("text/html; charset=utf-8", page)
            else:
                self.send_not_found()

        def do_get_archive_content(self):
            match = re.fullmatch(content_prefix + r"/([^/]*)/(.*)", self.path)

            if not match:
                self.send_bad_request()
                return

            name = urllib.parse.unquote(match[1])
            path = urllib.parse.unquote(match[2])
            result = get_archive_content(name, path)

            if result is not None:
                self.send_ok(*result)
            else:
                self.send_not_found()

        def send_ok(self, mime_type, content):
            self.send_response(http.HTTPStatus.OK)
            self.send_header("ETag", etag)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", len(content))
            self.end_headers()

            if self.command != "HEAD":
                self.wfile.write(content)

        def send_not_modified(self):
            self.send_response(http.HTTPStatus.NOT_MODIFIED)
            self.send_header("ETag", etag)
            self.end_headers()

        def send_not_found(self):
            self.send_response(http.HTTPStatus.NOT_FOUND)
            self.send_header("Content-Length", 0)
            self.end_headers()

        def send_bad_request(self):
            self.send_response(http.HTTPStatus.BAD_REQUEST)
            self.send_header("Content-Length", 0)
            self.end_headers()

        def log_message(self, *message):
            if enable_logging:
                super().log_message(*message)

    # Create and return an HTTP server.

    return http.server.ThreadingHTTPServer((host, port), Handler)

# Command-line interface entry point function

def cli():
    # Parse command-line arguments.

    args = parse_args()

    dir = args.dir or os.path.expanduser(default_dir)
    host = args.host
    port = args.port
    content_prefix = urllib.parse.quote(args.content_prefix)
    enable_logging = args.log

    # Setup and run the server.

    server = setup_server(dir, host, port, content_prefix, enable_logging)

    print("Serving at http://{}:{}".format(host, port))

    server.serve_forever()

if __name__ == "__main__":
    cli()
