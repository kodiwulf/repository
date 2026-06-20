#!/usr/bin/env python3
# name: kodiwulf_build_repo.py
# status: wrapper around kodiwulf_build_repo_core.py
# purpose: Run KodiWulf repository generator, then normalize public index.html links/markers
# risk: LOW/MEDIUM inside repository tree only
# destructive: no deletion; backs up index.html before edits

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

BEGIN = "<!-- DRDEBUG-KODIWULF-INDEX:BEGIN -->"
END = "<!-- DRDEBUG-KODIWULF-INDEX:END -->"


def parse_root(args: list[str]) -> Path:
    for i, arg in enumerate(args):
        if arg == "--root" and i + 1 < len(args):
            return Path(args[i + 1]).expanduser().resolve()
        if arg.startswith("--root="):
            return Path(arg.split("=", 1)[1]).expanduser().resolve()
    return Path.cwd().resolve()


def has_apply(args: list[str]) -> bool:
    return "--apply" in args or any(arg == "--apply=true" for arg in args)


def backup_file(path: Path) -> Path:
    backup_dir = path.parent / ".drdebug-backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    backup = backup_dir / f"{path.name}.wrapper-public-index.{stamp}.bak"
    shutil.copy2(path, backup)
    return backup


def normalize_public_index(index_path: Path) -> bool:
    if not index_path.exists():
        print(f"[WARN] index.html nicht gefunden: {index_path}", file=sys.stderr)
        return False

    text = index_path.read_text(encoding="utf-8")
    original = text

    # Öffentliche Website/Kodi-Dateibrowser-Links:
    # Quelle bleibt ZIPs/, aber sichtbare Download-Ziele sind Repository/, Videos/, Program/.
    replacements = {
        "ZIPs/REPOSITORY/": "Repository/",
        "ZIPs/VIDEO/": "Videos/",
        "ZIPs/PROGRAMM/": "Program/",
        "ZIPs/REPOSITORY": "Repository",
        "ZIPs/VIDEO": "Videos",
        "ZIPs/PROGRAMM": "Program",
        "plugin/repository/": "Repository/",
        "plugin/video/": "Videos/",
        "plugin/program/": "Program/",
        "plugin/repository": "Repository",
        "plugin/video": "Videos",
        "plugin/program": "Program",
        "aus ZIPs/ rekursiv gelesen": "aus Repository/, Videos/ und Program/ erzeugt",
        "aus plugin/* gespiegelt": "aus Repository/, Videos/ und Program/ erzeugt",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Falls der Core-Generator Marker entfernt, sauber neu markieren.
    # Erst beschädigte/halb vorhandene Marker entfernen, dann genau einmal um <main> legen.
    text = text.replace(BEGIN, "").replace(END, "")
    text = re.sub(r"\n{3,}", "\n\n", text)

    if "<main" in text and "</main>" in text:
        text = re.sub(r"(<main\b[^>]*>)", BEGIN + "\n" + r"\1", text, count=1)
        text = re.sub(r"(</main>)", r"\1" + "\n" + END, text, count=1)
    elif "</body>" in text:
        text = text.replace("</body>", BEGIN + "\n" + END + "\n</body>", 1)
    else:
        text = text.rstrip() + "\n" + BEGIN + "\n" + END + "\n"

    if text != original:
        backup = backup_file(index_path)
        index_path.write_text(text, encoding="utf-8")
        print(f"[OK] public index normalized: {index_path}")
        print(f"[OK] index backup: {backup}")
        return True

    print(f"[OK] public index already normalized: {index_path}")
    return False


def main() -> int:
    here = Path(__file__).resolve().parent
    core = here / "kodiwulf_build_repo_core.py"

    if not core.exists():
        print(f"ERROR: Core generator fehlt: {core}", file=sys.stderr)
        return 2

    args = sys.argv[1:]
    rc = subprocess.call([sys.executable, str(core), *args])
    if rc != 0:
        return rc

    if has_apply(args):
        root = parse_root(args)
        normalize_public_index(root / "index.html")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
