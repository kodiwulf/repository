#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def render_index() -> bytes:
    document = (ROOT / "index.html").read_text(encoding="utf-8")
    document = re.sub(r"\A---\s*\nlayout: null\s*\n---\s*\n", "", document)
    document = re.sub(
        r"\{\{\s*'(/[^']+)'\s*\|\s*relative_url\s*\}\}",
        lambda match: match.group(1),
        document,
    )
    tree = json.loads((ROOT / "_data" / "repository_tree.json").read_text(encoding="utf-8"))
    links = "".join(f'<a href="/{item["href"]}">{item["name"]}/</a>' for item in tree["roots"])
    document = re.sub(
        r"\{% for node in site\.data\.repository_tree\.roots %\}.*?\{% endfor %\}",
        links,
        document,
        flags=re.DOTALL,
    )
    return document.encode("utf-8")


class PreviewHandler(SimpleHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802 - stdlib API
        if self.path in {"/", "/index.html"}:
            payload = render_index()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()


def main() -> None:
    parser = argparse.ArgumentParser(description="Preview the Jekyll entry page without a Ruby installation")
    parser.add_argument("--port", type=int, default=8767)
    args = parser.parse_args()
    handler = lambda *items, **kwargs: PreviewHandler(*items, directory=str(ROOT), **kwargs)
    print(f"Kodi-Wulf preview: http://127.0.0.1:{args.port}/")
    ThreadingHTTPServer(("127.0.0.1", args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
