# # # # # # # # # # # # # # #
# Kodi-Wulf Update Process
# # # # # # # # # # # # # # #

## 1. Place source ZIPs locally

Source ZIPs are local build inputs and should not be committed.

    zips/

The folder is temporary and may be absent while it is empty.

## 2. Rebuild

    python tools/build.py --apply

## 3. Validate

Run:

    python -m py_compile tools/build.py tools/kodiwulf_dark_index.py tools/validate_repo.py
    python tools/validate_repo.py

Expected repository metadata:

    repository.kodi-wulf 1.33.7a: present
    addons.xml.md5: matches addons.xml

## 4. Commit and push

    git add -A -- .
    git commit -m "feat(repo): update Kodi-Wulf packages"
    git push origin main

## 5. Online checks

    curl -L -I "https://kodi-wulf.github.io/repository/"
    curl -L -I "https://kodi-wulf.github.io/repository/addons.xml"
    curl -L -I "https://kodi-wulf.github.io/repository/addons.xml.md5"
    curl -L -I "https://kodi-wulf.github.io/repository/repository.kodi-wulf-v1.33.7a.zip"
