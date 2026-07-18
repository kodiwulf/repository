![KodiWulf Repository Banner](bg.png)

# # # # # # # # # # # # #
# KodiWulf Repository
# # # # # # # # # # # # #

KodiWulf is a static Kodi 21 Omega repository served through GitHub Pages.

## Public URL

    https://kodi-wulf.github.io/repository/

## Install from ZIP

Use this ZIP in Kodi:

Add this file source in Kodi:

    https://kodi-wulf.github.io/repository/

Then install:

    repository.kodiwulf-0.1.0.zip

The same root URL serves the Jekyll website and Kodi's folder browser. The root
page uses React for ZIP-only navigation, Anime.js for restrained transitions,
and one shared dark console theme for all generated directory pages.

After installation, Kodi reads:

    https://kodi-wulf.github.io/repository/addons.xml
    https://kodi-wulf.github.io/repository/addons.xml.md5

## Current repository state

    repository.kodiwulf 0.1.0
    Kodi target: Kodi 21 Omega
    Add-ons in addons.xml: 18

## Published structure

    repository.kodiwulf-*.zip  Only ZIP allowed in the root
    repository/<addon.id>/     Repository ZIPs
    plugins/<type>/<addon.id>/ Plugin ZIPs, for example plugins/audio/
    script/<type>/<addon.id>/  Script ZIPs, for example script/module/
    incoming/*.zip             Optional temporary import inbox
    addons.xml     Kodi repository metadata
    addons.xml.md5 Kodi repository checksum
    index.html     GitHub Pages landing page

## Local source ZIP layout

New ZIPs can be placed temporarily in `incoming/` (or anywhere outside the
published category folders). `tools/build.py` reads `addon.xml`, moves each ZIP
to its canonical category, updates Kodi metadata, and removes the empty inbox.

## Rebuild

    python tools/build.py --apply

The active generator also runs:

    tools/kodiwulf_addons_xml.py
    tools/kodiwulf_dark_index.py

Only install Kodi add-ons and repositories you trust.
