# # # # # # # # # # # # # #
# KodiWulf Repository #
# # # # # # # # # # # # # #

KodiWulf repository skeleton for Kodi add-ons, modeled after a classic web-served Kodi repository layout.

Reference layout checked: the example repository exposes add-on folders plus `addons.xml` and `addons.xml.md5` at the web root, and contains a repository add-on folder with `addon.xml`, `icon.png`, and a versioned repository ZIP.

## Public URLs after GitHub Pages is enabled

```text
https://n-e-o-w-u-l-f.github.io/kodiwulf-repo/addons.xml
https://n-e-o-w-u-l-f.github.io/kodiwulf-repo/addons.xml.md5
https://n-e-o-w-u-l-f.github.io/kodiwulf-repo/repository.kodiwulf/repository.kodiwulf-0.0.1.zip
```

## Install in Kodi

1. Download `repository.kodiwulf/repository.kodiwulf-0.0.1.zip`.
2. Kodi → Add-ons → Install from zip file.
3. Select the ZIP.
4. Then use “Install from repository” → “KodiWulf Repository”.

## Local build

```bash
python3 tools/build_repo.py
```

## Structure

```text
kodiwulf-repo/
├── addons.xml
├── addons.xml.md5
├── repository.kodiwulf/
│   ├── addon.xml
│   ├── icon.png
│   ├── fanart.jpg
│   └── repository.kodiwulf-0.0.1.zip
├── tools/
│   └── build_repo.py
├── .github/workflows/
│   └── build.yml
├── CHANGES.md
├── UPDATE_PROCESS.md
├── README.md
└── .gitignore
```
# kodiwulf-repo
