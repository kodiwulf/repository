# # # # # # # # # # # # # # #
# KodiWulf Update Process
# # # # # # # # # # # # # # #

## 1. Place source ZIPs locally

Source ZIPs are local build inputs and should not be committed.

    incoming/

The folder is temporary and may be absent while it is empty.

## 2. Rebuild

    python tools/build.py --apply

## 3. Validate

Run:

    python -m py_compile tools/build.py tools/kodiwulf_dark_index.py tools/validate_repo.py
    python tools/validate_repo.py

Expected repository metadata:

    Add-ons: 18
    repository.kodiwulf 0.1.0: present
    addons.xml.md5: matches addons.xml

## 4. Commit and push

    git add -A -- .
    git commit -m "fix(repo): update KodiWulf docs"
    git push origin main

## 5. Online checks

    curl -L -I "https://kodiwulf.github.io/repository/"
    curl -L -I "https://kodiwulf.github.io/repository/addons.xml"
    curl -L -I "https://kodiwulf.github.io/repository/addons.xml.md5"
    curl -L -I "https://kodiwulf.github.io/repository/repository.kodiwulf-0.1.0.zip"
