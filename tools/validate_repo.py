#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import quote


ROOT = Path(__file__).resolve().parents[1]
TECHNICAL_ROOTS = {".github", "Repository", "_data", "_layouts", "_site", "assets", "node_modules", "tools"}
LEGACY_MIRROR_BRANCHES = {("repository", "plugins"), ("repository", "repository"), ("repository", "script")}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def is_visible(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if path.suffix.lower() == ".zip" and len(relative.parts) == 2 and relative.parts[0] == "repository" and path.name.startswith("repository.kodiwulf-"):
        return False
    if relative.parts and relative.parts[0] == "Repository":
        return False
    return not (len(relative.parts) > 1 and (relative.parts[0], relative.parts[1]) in LEGACY_MIRROR_BRANCHES)


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
    tree_path = ROOT / "_data" / "repository_tree.json"
    if not tree_path.is_file():
        fail("Jekyll navigation data is missing: _data/repository_tree.json")
    tree = json.loads(tree_path.read_text(encoding="utf-8"))
    public_roots = sorted(
        path for path in ROOT.iterdir()
        if path.is_dir() and not path.name.startswith(".") and path.name not in TECHNICAL_ROOTS
    )
    root_zips = sorted(ROOT.glob("*.zip"))
    if len(root_zips) != 1 or not root_zips[0].name.startswith("repository.kodiwulf-"):
        fail("repository.kodiwulf must be the only ZIP in repository root")

    for zip_path in root_zips:
        linked_name = quote(zip_path.name, safe="/._-~")
        if linked_name not in browser_data:
            fail(f"root ZIP is not present in React browser data: {zip_path.name}")
    for required in ("bootstrap@5.3.8", "jquery-3.7.1.min.js", "vue@3", "anime.min.js", "d3@7", "assets/app.js", "assets/svelte-status.js"):
        if required not in index:
            fail(f"missing frontend resource: {required}")
    for href in (*(quote(path.name, safe="._-~") + "/" for path in public_roots), quote(root_zips[0].name, safe="/._-~")):
        if f'href="{href}"' not in index:
            fail(f"missing static Kodi root link: {href}")
    data_names = {item["name"] for item in tree.get("roots", [])}
    if data_names != {path.name for path in public_roots}:
        fail("Jekyll root navigation does not match public root directories")
    if "site.data.repository_tree.menu" not in index:
        fail("root index does not render the generated Jekyll menu")

    allowed_md5 = {checksum}
    allowed_md5.update(path for path in ROOT.rglob("addons.xml.md5") if (path.parent / "index.html").is_file())
    stray_md5 = [path for path in ROOT.rglob("*.md5") if path not in allowed_md5]
    if stray_md5:
        fail(f"unneeded MD5 sidecar exists: {stray_md5[0].relative_to(ROOT)}")

    classified = [zip_path for directory in public_roots for zip_path in directory.rglob("*.zip") if is_visible(zip_path)]
    hashes = [hashlib.sha256(path.read_bytes()).hexdigest() for path in classified]
    if len(hashes) != len(set(hashes)):
        fail("duplicate ZIP content exists in the public category structure")
    required_indexes = [ROOT / "repository"]
    for parent_name in ("plugin", "plugins", "script"):
        parent = ROOT / parent_name
        if parent.is_dir():
            required_indexes.extend(path for path in parent.iterdir() if path.is_dir())
    required_indexes.extend(path for path in public_roots if path.name not in {"repository", "plugin", "plugins", "script"})
    for directory in required_indexes:
        page = directory / "index.html"
        if not page.is_file():
            fail(f"missing Kodi/Jekyll directory index: {directory.relative_to(ROOT)}")
        page_text = page.read_text(encoding="utf-8")
        for zip_path in (path for path in directory.rglob("*.zip") if is_visible(path)):
            relative_link = quote(zip_path.relative_to(directory).as_posix(), safe="/._-~")
            if f'href="{relative_link}"' not in page_text:
                fail(f"ZIP is not linked in category index: {zip_path.relative_to(ROOT)}")
    print(f"OK: one root installer and {len(classified)} unique classified ZIP files")


if __name__ == "__main__":
    main()
