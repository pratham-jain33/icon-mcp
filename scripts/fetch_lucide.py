"""Fetch the pinned Lucide release and bundle it into the icon_mcp package.

Downloads lucide-static from the npm registry at LUCIDE_VERSION, extracts
the SVG files into icon_mcp/icons/, and builds icon_mcp/icon_index.json
(name -> tags) from the shipped tags.json. Run from the repo root:

    python scripts/fetch_lucide.py

Re-running with a bumped LUCIDE_VERSION refreshes the whole bundle.
"""

import hashlib
import io
import json
import shutil
import sys
import tarfile
import urllib.request
from pathlib import Path

LUCIDE_VERSION = "1.50.0"
TARBALL_URL = (
    "https://registry.npmjs.org/lucide-static/-/lucide-static-{}.tgz".format(
        LUCIDE_VERSION
    )
)

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "icon_mcp"
ICONS_DIR = PKG / "icons"


def main() -> None:
    print("Downloading lucide-static v{} ...".format(LUCIDE_VERSION))
    with urllib.request.urlopen(TARBALL_URL) as resp:
        data = resp.read()
    print("Downloaded {:.1f} MB".format(len(data) / 1e6))

    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
        members = tar.getmembers()
        by_name = {m.name: m for m in members}

        # -- SVG files ---------------------------------------------------
        svg_members = [
            m for m in members
            if m.name.startswith("package/icons/") and m.name.endswith(".svg")
        ]
        if ICONS_DIR.exists():
            shutil.rmtree(ICONS_DIR)
        ICONS_DIR.mkdir(parents=True)
        for m in svg_members:
            src = tar.extractfile(m)
            assert src is not None
            dest = ICONS_DIR / Path(m.name).name
            dest.write_bytes(src.read())

        # -- tags.json ---------------------------------------------------
        tags_member = by_name.get("package/tags.json")
        tags = {}
        if tags_member is not None:
            src = tar.extractfile(tags_member)
            assert src is not None
            tags = json.load(src)

        # -- Lucide license (ISC requires the notice to ship with copies) --
        lic_member = by_name.get("package/LICENSE")
        if lic_member is not None:
            src = tar.extractfile(lic_member)
            assert src is not None
            (PKG / "LUCIDE_LICENSE").write_bytes(src.read())

    # -- Build the index: every icon name, with tags where Lucide has them.
    # Some SVGs are deprecated aliases with no tags entry; detect aliases
    # by identical file content so search can surface the canonical name. --
    by_hash: dict[str, list[str]] = {}
    for svg_file in ICONS_DIR.glob("*.svg"):
        digest = hashlib.sha256(svg_file.read_bytes()).hexdigest()
        by_hash.setdefault(digest, []).append(svg_file.stem)

    canonical: dict[str, str] = {}
    for names in by_hash.values():
        tagged = [n for n in names if n in tags]
        if tagged:
            for n in names:
                canonical[n] = tagged[0]

    index = {
        "lucide_version": LUCIDE_VERSION,
        "icons": {
            svg_file.stem: {
                "tags": tags.get(svg_file.stem, []),
                "canonical": canonical.get(svg_file.stem, svg_file.stem),
            }
            for svg_file in sorted(ICONS_DIR.glob("*.svg"))
        },
    }
    (PKG / "icon_index.json").write_text(json.dumps(index))

    alias_count = sum(
        1 for name, v in index["icons"].items() if v["canonical"] != name
    )
    print("Bundled {} icons (lucide-static v{}), {} are aliases".format(
        len(index["icons"]), LUCIDE_VERSION, alias_count))
    print("Wrote icon_mcp/icon_index.json, icon_mcp/LUCIDE_LICENSE")


if __name__ == "__main__":
    sys.exit(main())
