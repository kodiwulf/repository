#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    if (ROOT / ".nojekyll").exists():
        fail(".nojekyll must not exist because Jekyll rendering is enabled")
    if not (ROOT / "_config.yml").is_file():
        fail("_config.yml is required for Jekyll")

    addons_xml = ROOT / "addons.xml"
    checksum = ROOT / "addons.xml.md5"
    expected = hashlib.md5(addons_xml.read_bytes()).hexdigest()
    if checksum.read_text(encoding="utf-8").strip() != expected:
        fail("addons.xml.md5 does not match addons.xml")

    index = (ROOT / "index.html").read_text(encoding="utf-8")
    browser_data = (ROOT / "assets" / "files.js").read_text(encoding="utf-8")
    root_zips = sorted(ROOT.glob("*.zip"))
    if len(root_zips) != 1 or not root_zips[0].name.startswith("repository.kodiwulf-"):
        fail("repository.kodiwulf must be the only ZIP in repository root")

    for zip_path in root_zips:
        linked_name = quote(zip_path.name, safe="/._-~")
        if linked_name not in browser_data:
            fail(f"root ZIP is not present in React browser data: {zip_path.name}")
    for required in ("react.production.min.js", "react-dom.production.min.js", "anime.min.js", "assets/file-browser.js"):
        if required not in index:
            fail(f"missing React/Anime browser resource: {required}")

    allowed_md5 = {checksum}
    allowed_md5.update(path for path in ROOT.rglob("addons.xml.md5") if (path.parent / "index.html").is_file())
    stray_md5 = [path for path in ROOT.rglob("*.md5") if path not in allowed_md5]
    if stray_md5:
        fail(f"unneeded MD5 sidecar exists: {stray_md5[0].relative_to(ROOT)}")

    classified = list((ROOT / "repository").rglob("*.zip")) + list((ROOT / "plugins").rglob("*.zip")) + list((ROOT / "script").rglob("*.zip"))
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in classified]
    if len(hashes) != len(set(hashes)):
        fail("duplicate ZIP content exists in the public category structure")
    for directory in [ROOT / "repository", *[path for path in (ROOT / "plugins").iterdir() if path.is_dir()], *[path for path in (ROOT / "script").iterdir() if path.is_dir()]]:
        page = directory / "index.html"
        if not page.is_file():
            fail(f"missing Kodi/Jekyll directory index: {directory.relative_to(ROOT)}")
        page_text = page.read_text(encoding="utf-8")
        for zip_path in directory.rglob("*.zip"):
            relative_link = quote(zip_path.relative_to(directory).as_posix(), safe="/._-~")
            if f'href="{relative_link}"' not in page_text:
                fail(f"ZIP is not linked in category index: {zip_path.relative_to(ROOT)}")
    print(f"OK: one root installer and {len(classified)} unique classified ZIP files")


if __name__ == "__main__":
    main()
