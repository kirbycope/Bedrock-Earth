"""Builds Bedrock-Earth.mctemplate from the repository, so nothing is copied into a zip by hand.

The archive is what Minecraft imports when the file is double-clicked: the world template's own files at the
root (manifest.json, level.dat, db/ and the rest) and the packs under behavior_packs/ and resource_packs/,
each with its manifest.json directly inside. The repository root is the template, so only the files git
tracks there go in, and the README, preview image and tools stay out.

The database under db/ is read from git rather than the working tree: with core.autocrlf on, Windows checks
db/CURRENT out with a CRLF ending, and LevelDB refuses a CURRENT that does not end in a bare LF.

The build goes to build/, which git ignores, so the Bedrock-Earth.mctemplate committed at the root of the
repository is never touched by it.

    python tools/build_addon.py            # writes build/Bedrock-Earth.mctemplate
    python tools/build_addon.py --check    # exits 1 if the archive on disk differs from what a build would produce

What Minecraft requires of the zip: entries at the root (no wrapping folder), forward slashes in entry names,
Deflate or Store, no zip64. Images and sounds, already compressed, are stored rather than deflated.
"""

import argparse
import io
import os
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = ["LICENSE", "level.dat", "levelname.txt", "manifest.json", "world_behavior_packs.json", "world_icon.jpeg", "world_resource_packs.json"]
FOLDERS = ["behavior_packs", "db", "resource_packs", "texts"]
FROM_GIT = "db/"   # read from git's index, not the working tree, so line endings stay as committed
OUTPUT = os.path.join(ROOT, "build", "Bedrock-Earth.mctemplate")
STAMP = (2026, 1, 1, 0, 0, 0)   # a fixed timestamp keeps the archive byte-for-byte reproducible, so --check can compare it
STORED = {".png", ".jpg", ".jpeg", ".ogg", ".fsb"}
LIMIT = 100 * 1024 * 1024   # GitHub refuses a file over 100 MB


def tracked() -> list[str]:
    """The template's files git tracks, sorted, those deleted from the working tree left out."""
    out = subprocess.run(["git", "-C", ROOT, "ls-files", "-z", "--", *FILES, *FOLDERS], check=True, capture_output=True).stdout.decode("utf-8")
    return sorted(p for p in out.split("\0") if p and os.path.isfile(os.path.join(ROOT, p)))


def read(path: str) -> bytes:
    if path.startswith(FROM_GIT):
        return subprocess.run(["git", "-C", ROOT, "show", f":{path}"], check=True, capture_output=True).stdout
    with open(os.path.join(ROOT, path), "rb") as handle:
        return handle.read()


def build() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, allowZip64=False) as archive:
        seen: set[str] = set()

        def add_dir(path: str) -> None:
            parts = path.split("/")
            for depth in range(1, len(parts)):
                folder = "/".join(parts[:depth]) + "/"
                if folder in seen: continue
                seen.add(folder)
                info = zipfile.ZipInfo(folder, STAMP)
                info.external_attr = 0o40777 << 16
                archive.writestr(info, b"", zipfile.ZIP_STORED)

        for path in tracked():
            add_dir(path)
            info = zipfile.ZipInfo(path, STAMP)
            info.external_attr = 0o666 << 16
            info.compress_type = zipfile.ZIP_STORED if os.path.splitext(path)[1].lower() in STORED else zipfile.ZIP_DEFLATED
            archive.writestr(info, read(path), compresslevel=9)
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--check", action="store_true", help="report whether the archive is up to date instead of writing it")
    parser.add_argument("--output", default=OUTPUT)
    args = parser.parse_args()

    data = build()
    if len(data) > LIMIT:
        print(f"refusing to write {len(data)} bytes, over GitHub's 100 MB limit", file=sys.stderr)
        return 1
    current = os.path.exists(args.output) and open(args.output, "rb").read() == data
    if args.check:
        print("up to date" if current else f"out of date: {os.path.relpath(args.output, ROOT)}")
        return 0 if current else 1
    os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
    with open(args.output, "wb") as handle:
        handle.write(data)
    print(f"wrote {os.path.relpath(args.output, ROOT)} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
