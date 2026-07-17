#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import quote
import xml.etree.ElementTree as ET

from kodiwulf_build_repo_core import AddonInfo, parse_addon_zip, pretty_xml


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE_URL = "https://kodiwulf.github.io/repository/"
SKIP_PARTS = {".git", ".drdebug-backups", "__pycache__"}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def category(info: AddonInfo) -> str:
    addon_id = info.addon_id.lower()
    if info.is_repository:
        return "repository"
    if addon_id.startswith("plugin."):
        parts = addon_id.split(".")
        kind = parts[1] if len(parts) > 2 else "other"
        return f"plugins/{kind}"
    if addon_id.startswith("script.module."):
        return "script/module"
    if addon_id.startswith("script."):
        parts = addon_id.split(".")
        kind = parts[1] if len(parts) > 2 else "other"
        return f"script/{kind}"
    if "video" in info.provides:
        return "plugins/video"
    if "audio" in info.provides:
        return "plugins/audio"
    return "script/module"


def candidates(root: Path) -> list[Path]:
    result = []
    for path in root.rglob("*.zip"):
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        if len(rel.parts) == 1 and path.name.startswith("repository.kodiwulf-"):
            continue
        result.append(path)
    return sorted(result)


def choose_source(paths: list[Path], root: Path) -> Path:
    def rank(path: Path) -> tuple[int, int, str]:
        rel = path.relative_to(root)
        in_inbox = bool(rel.parts and rel.parts[0].lower() == "zips")
        return (0 if in_inbox else 1, len(rel.parts), rel.as_posix().lower())
    return sorted(paths, key=rank)[0]


def index_document(title: str, entries: list[tuple[str, str, str]]) -> str:
    buttons = "\n".join(
        f'<a class="entry" href="{html.escape(quote(href, safe="/._-~"))}">{html.escape(name)}</a>'
        for name, version, href in entries
    ) or '<p class="empty">Keine ZIP-Dateien vorhanden.</p>'
    return f"""---
layout: null
---
<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><link rel="stylesheet" href="/repository/assets/theme.css"></head>
<body><main class="shell"><header class="masthead"><div><p class="eyebrow">kodiwulf // install from zip</p><h1 class="title">{html.escape(title)}</h1></div></header><section class="browser"><div class="toolbar"><nav class="breadcrumbs"><a class="crumb" href="/repository/">root</a></nav><span class="count">ZIP archives</span></div><div class="listing">{buttons}</div></section></main></body></html>
"""


def write_react_root(root: Path) -> None:
    items = []
    for zip_path in sorted(root.glob("repository.kodiwulf-*.zip")):
        items.append({"path": zip_path.name, "name": zip_path.name, "url": quote(zip_path.name, safe="/._-~"), "category": "installer"})
    for top in ("repository", "plugins", "script"):
        directory = root / top
        if not directory.is_dir():
            continue
        for zip_path in sorted(directory.rglob("*.zip")):
            rel = zip_path.relative_to(root).as_posix()
            items.append({"path": rel, "name": zip_path.name, "url": quote(rel, safe="/._-~"), "category": top})
    assets = root / "assets"
    assets.mkdir(exist_ok=True)
    (assets / "files.js").write_text("window.KODIWULF_FILES=" + json.dumps(items, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    installer_links = "".join(
        f'<a href="{quote(zip_path.name, safe="/._-~")}">{html.escape(zip_path.name)}</a>'
        for zip_path in sorted(root.glob("repository.kodiwulf-*.zip"))
    )
    root_doc = f"""---
layout: null
---
<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="dark"><title>KodiWulf ZIP Browser</title><link rel="stylesheet" href="assets/theme.css"></head><body><nav class="kodi-static" aria-label="Kodi ZIP index"><a href="repository/">repository/</a><a href="plugins/">plugins/</a><a href="script/">script/</a>{installer_links}</nav><div id="file-browser-root"></div><noscript><p class="noscript">JavaScript wird für den React-Dateibrowser benötigt. Kodi verwendet die statischen Links oben.</p></noscript><script src="https://unpkg.com/react@18/umd/react.production.min.js"></script><script src="https://unpkg.com/react-dom@18/umd/react-dom.production.min.js"></script><script src="https://cdnjs.cloudflare.com/ajax/libs/animejs/3.2.2/anime.min.js"></script><script src="assets/files.js"></script><script src="assets/file-browser.js"></script></body></html>
"""
    # Kodi's basic directory parser can skip every second anchor when links are
    # directly adjacent. Keep real whitespace between all static anchors.
    root_doc = root_doc.replace("</a><a ", "</a>\n<a ")
    (root / "index.html").write_text(root_doc, encoding="utf-8")


def write_metadata(directory: Path, infos: list[AddonInfo]) -> None:
    root = ET.Element("addons")
    for info in sorted(infos, key=lambda item: item.addon_id.lower()):
        root.append(ET.fromstring(info.addon_xml))
    data = pretty_xml(root)
    (directory / "addons.xml").write_bytes(data)
    (directory / "addons.xml.md5").write_text(hashlib.md5(data).hexdigest(), encoding="utf-8")


def make_repo_xml(categories: list[str], base_url: str, version: str) -> bytes:
    dirs = []
    for name in categories:
        url = base_url.rstrip("/") + "/" + name.strip("/") + "/"
        dirs.append(f"""    <dir>
      <info compressed="false">{html.escape(url)}addons.xml</info>
      <checksum>{html.escape(url)}addons.xml.md5</checksum>
      <datadir zip="true">{html.escape(url)}</datadir>
      <hashes>false</hashes>
    </dir>""")
    return (f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<addon id="repository.kodiwulf" name="KodiWulf Repository" version="{html.escape(version)}" provider-name="KodiWulf">
  <extension point="xbmc.addon.repository" name="KodiWulf Repository">
{chr(10).join(dirs)}
  </extension>
  <extension point="xbmc.addon.metadata"><summary lang="de_DE">KodiWulf Add-on Repository</summary><platform>all</platform></extension>
</addon>
""").encode("utf-8")


def write_repo_zip(root: Path, xml: bytes, version: str) -> Path:
    target = root / f"repository.kodiwulf-{version}.zip"
    with tempfile.TemporaryDirectory() as temp:
        addon_dir = Path(temp) / "repository.kodiwulf"
        addon_dir.mkdir()
        (addon_dir / "addon.xml").write_bytes(xml)
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            archive.write(addon_dir / "addon.xml", "repository.kodiwulf/addon.xml")
    return target


def build(root: Path, base_url: str, version: str, apply: bool, backup: Path) -> None:
    by_identity: dict[tuple[str, str], list[tuple[Path, AddonInfo]]] = defaultdict(list)
    invalid: list[tuple[Path, str, str]] = []
    for path in candidates(root):
        try:
            info = parse_addon_zip(path)
        except SystemExit:
            stem = path.stem
            match = re.match(r"((?:plugin|repository|script)\.[A-Za-z0-9._-]+)", stem, re.IGNORECASE)
            addon_id = match.group(1) if match else stem
            if addon_id.lower().startswith("plugin."):
                parts = addon_id.split(".")
                group = f"plugins/{parts[1] if len(parts) > 2 else 'other'}"
            elif addon_id.lower().startswith("repository."):
                group = "repository"
            else:
                group = "script/module"
            invalid.append((path, group, addon_id))
            print(f"WARN: invalid addon.xml; filename classification used: {path.relative_to(root)} -> {group}")
            continue
        by_identity[(info.addon_id, info.version)].append((path, info))

    selected = []
    for items in by_identity.values():
        source = choose_source([path for path, _ in items], root)
        info = next(info for path, info in items if path == source)
        selected.append((source, info, items))

    if not apply:
        for source, info, _ in sorted(selected, key=lambda item: item[1].addon_id.lower()):
            print(f"{source.relative_to(root)} -> {category(info)}/{info.addon_id}/{info.addon_id}-{info.version}.zip")
        print(f"DRY-RUN: {len(selected)} unique add-ons")
        return

    backup.mkdir(parents=True, exist_ok=True)
    grouped: dict[str, list[AddonInfo]] = defaultdict(list)
    final_paths: set[Path] = set()
    for source, info, items in selected:
        group = category(info)
        destination = root / group / info.addon_id / f"{info.addon_id}-{info.version}.zip"
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            if destination.exists() and digest(destination) != digest(source):
                raise RuntimeError(f"conflicting destination: {destination}")
            if not destination.exists():
                shutil.move(str(source), str(destination))
        final_paths.add(destination.resolve())
        grouped[group].append(info)
        for duplicate, _ in items:
            if not duplicate.exists() or duplicate.resolve() in final_paths:
                continue
            rel = duplicate.relative_to(root)
            archived = backup / rel
            archived.parent.mkdir(parents=True, exist_ok=True)
            if archived.exists():
                archived = archived.with_name(archived.stem + "-" + digest(duplicate)[:10] + archived.suffix)
            shutil.move(str(duplicate), str(archived))

    for source, group, addon_id in invalid:
        destination = root / group / addon_id / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != destination.resolve():
            if destination.exists() and digest(destination) != digest(source):
                raise RuntimeError(f"conflicting invalid ZIP destination: {destination}")
            if not destination.exists():
                shutil.move(str(source), str(destination))
        grouped.setdefault(group, [])

    for group, infos in grouped.items():
        directory = root / group
        write_metadata(directory, infos)
        depth = len(Path(group).parts)
        prefix = "../" * depth
        entries = []
        for zip_path in sorted(directory.rglob("*.zip"), key=lambda item: item.name.lower()):
            rel = zip_path.relative_to(directory).as_posix()
            entries.append((zip_path.name, "ZIP", rel))
        (directory / "index.html").write_text(index_document(f"KodiWulf / {group}", entries), encoding="utf-8")

    for parent_name in ("plugins", "script"):
        children = sorted({Path(group).parts[1] for group in grouped if Path(group).parts[0] == parent_name and len(Path(group).parts) > 1})
        parent = root / parent_name
        parent.mkdir(exist_ok=True)
        entries = [(f"{child}/", "Ordner", f"{child}/") for child in children]
        (parent / "index.html").write_text(index_document(f"KodiWulf / {parent_name}", entries), encoding="utf-8")

    repo_xml = make_repo_xml(sorted(grouped), base_url, version)
    repo_zip = write_repo_zip(root, repo_xml, version)
    all_infos = [info for infos in grouped.values() for info in infos]
    write_metadata(root, all_infos)

    write_react_root(root)
    print(f"OK: {len(all_infos)} ZIPs classified; installer: {repo_zip.name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--repo-version", default="0.1.0")
    parser.add_argument("--backup", default=str(ROOT.parent / "repository-zip-backup"))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    build(Path(args.root).resolve(), args.base_url, args.repo_version, args.apply, Path(args.backup).resolve())


if __name__ == "__main__":
    main()
