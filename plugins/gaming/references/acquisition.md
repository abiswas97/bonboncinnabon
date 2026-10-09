# Acquiring games, art and documents

Search before downloading: files the owner gave, then the library, then the profile's `extra_sources`. Download only what is still missing and within the owner's request.

## Rules

- **Ask before downloading.** Name each file, its source and its size. Once the owner approves a known list, download it with a script, with a bounded number in parallel, rather than one by one.
- **Respect access rules.** Never bypass paywalls, patron-only restrictions or sign-in walls.
- **Keep sign-ins out of files.** Sign-ins stay temporary and in memory. For example, Internet Archive accepts login cookies for restricted items or S3-style keys. Load them for the session only (for instance through the `internetarchive` library's in-memory auth config); never write a credentials file.
- **Keep originals.** Keep the downloaded originals (zips, disc archives) under `Archives/<system>/` when the game file was extracted or converted from them.

## Checking what arrived

- **Zips:** test zips before extracting (`verify_rom.py` does this, with or without `--dat`), then verify the extracted file against the DAT where a catalogue covers it.
- **7z:** macOS `bsdtar` reads 7z archives only from a seekable file. Download first, then extract; do not stream.
- **Integrity is not identity.** A file that downloaded intact can still be the wrong edition. The DAT match and the reviewer decide identity.

## Reference catalogues (DATs)

- **Where they come from.** No-Intro covers cartridge systems and Redump covers disc systems. The libretro database (https://github.com/libretro/libretro-database, folders `metadat/no-intro` and `metadat/redump`) republishes them in clrmamepro format, which `verify_rom.py` reads.
- **Where to keep them.** Store the DATs you use under `<root>/Tools/DATs/`, with their source and date in the run ledger.
- **What a match proves.** A DAT match proves the dump identity only. Achievement systems hash some games differently, so check their own hash list when that matters to the owner.

## Artwork and documents

- **Prefer established sources:**
  - artwork: scraper databases or the frontend's own scraper
  - documents: preservation scans
- **Record provenance.** Record each file's source URL in the ledger and manifest.
- **Hack and translation documents** come from the hack's own release or repository, and are classified as `Documentation`.
