# # # # # # # # # #
# CHANGES
# # # # # # # # # #

## 1.33.7a - 2026-07-19

- Renamed the generated repository add-on to `repository.kodi-wulf` / `Kodi-Wulf`.
- Added `icon.png` and `fanart.png` to the installable repository ZIP.
- Added the German How-To-Use page for Kodi's file manager workflow.
- Imported and classified all ZIP packages from the local `zips/` inbox.

## 0.1.1 - 2026-06-20

- Stabilized generated addons.xml whitespace and MD5 output.
- Added idempotent metadata helper: tools/kodiwulf_addons_xml.py.
- Added idempotent dark index helper: tools/kodiwulf_dark_index.py.
- Fixed the generated metadata so repository.kodiwulf 0.1.0 remains included.
- Kept addons.xml at 18 add-ons.
- Updated README.md, UPDATE_PROCESS.md and index.md for the current Kodi 21 Omega layout.
- Updated the active generator default base URL to GitHub Pages.

## 0.1.0 - 2026-06-20

- Rebuilt KodiWulf as a static Kodi 21 Omega repository.
- Added generated repository.kodiwulf 0.1.0 install ZIP.
- Added browser-friendly Program, Repository and Videos ZIP folders.
- Refreshed addons.xml and addons.xml.md5.
- Added tools/kodiwulf_build_repo.py as the active repository generator.
