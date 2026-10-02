"""Icon library: load the bundled Lucide set, search it, restyle it.

The transform is pure attribute manipulation on the SVG root element:
width/height, stroke-width, stroke. No rasterization, no native
dependencies, nothing but the standard library.
"""

import json
import math
import re
from pathlib import Path
from xml.etree import ElementTree as ET

_PKG_DIR = Path(__file__).resolve().parent
_INDEX_PATH = _PKG_DIR / "icon_index.json"
_ICONS_DIR = _PKG_DIR / "icons"

# Sensible bounds. Lucide draws on a 24px grid; stroke widths outside
# 0.5-4 either vanish or swallow the shapes.
MIN_STROKE_WIDTH = 0.5
MAX_STROKE_WIDTH = 4.0
MIN_SIZE = 1
MAX_SIZE = 1024
MAX_ICONS_PER_CALL = 50
MAX_SEARCH_LIMIT = 30

_HEX_COLOR = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_NAMED_COLOR = re.compile(r"^[a-zA-Z]+$")

# Serialize <svg> with a clean default xmlns instead of ns0: prefixes.
ET.register_namespace("", "http://www.w3.org/2000/svg")

_index: dict | None = None
_svg_cache: dict[str, str] = {}


def _load_index() -> dict:
    """Read icon_index.json once; maps name -> {tags, canonical}."""
    global _index
    if _index is None:
        _index = json.loads(_INDEX_PATH.read_text())
    return _index


def icon_count() -> int:
    """How many icons are bundled."""
    return len(_load_index()["icons"])


def lucide_version() -> str:
    """The pinned Lucide release bundled in the package."""
    return _load_index()["lucide_version"]


def icon_names() -> list[str]:
    """Every bundled icon name, sorted."""
    return sorted(_load_index()["icons"])


def icon_tags(name: str) -> list[str]:
    """Lucide's keyword tags for an icon, empty list if unknown."""
    entry = _load_index()["icons"].get(name)
    return list(entry["tags"]) if entry else []


def _normalize_query(query: str) -> str:
    return query.strip().lower().replace("_", "-").replace(" ", "-")


def _tokens(query: str) -> list[str]:
    return [t for t in re.split(r"[\s\-_]+", query.strip().lower()) if t]


def search(query: str, limit: int = 10) -> list[dict]:
    """Keyword search over icon names and Lucide tags.

    Returns up to `limit` dicts: {name, tags, canonical}, best first.
    Exact name matches outrank prefix matches, which outrank tag hits.
    """
    limit = max(1, min(MAX_SEARCH_LIMIT, limit))
    tokens = _tokens(query)
    if not tokens:
        return []

    index = _load_index()["icons"]
    normalized_whole = _normalize_query(query)
    names = list(index)
    total_icons = len(names)

    # Rarity weight per token: a token few icons contain (e.g. "trash")
    # says more than one found everywhere (e.g. "can").
    idf: dict[str, float] = {}
    for tok in tokens:
        df = sum(1 for n in names if tok in n.lower())
        idf[tok] = math.log(total_icons / max(df, 1))

    # Rank key per icon: (whole-query exact, tokens covered,
    # rarity of covered tokens, match quality). Tuple-sorted descending
    # except the name, which breaks ties alphabetically.
    scored: list[tuple[tuple[float, int, float, float], str]] = []
    for name, entry in index.items():
        lname = name.lower()
        if normalized_whole == lname:
            scored.append(((1.0, 0, 0.0, 0.0), name))
            continue
        tags = entry["tags"]
        joined_tags = " ".join(tags).lower()
        matched = 0
        rarity = 0.0
        quality = 0.0
        for tok in tokens:
            if tok == lname:
                q = 25.0
            elif lname.startswith(tok):
                q = 40.0
            elif tok in lname:
                q = 20.0
            elif any(tok == tag.lower() for tag in tags):
                q = 15.0
            elif tok in joined_tags:
                q = 8.0
            else:
                q = 0.0
            if q:
                matched += 1
                rarity += idf[tok]
                quality += q
        if matched:
            scored.append(((0.0, matched, rarity, quality), name))

    scored.sort(key=lambda s: (-s[0][0], -s[0][1], -s[0][2], -s[0][3],
                               s[1]))
    return [
        {"name": name, "tags": index[name]["tags"],
         "canonical": index[name]["canonical"]}
        for _, name in scored[:limit]
    ]


def resolve(query: str) -> str | None:
    """Turn a name or keyword query into an exact icon name.

    Exact names win; otherwise the best search hit. None if nothing fits.
    """
    normalized = _normalize_query(query)
    index = _load_index()["icons"]
    if normalized in index:
        return normalized
    hits = search(query, limit=1)
    return hits[0]["canonical"] if hits else None


def validate_style(stroke_width: float, color: str,
                   size: int) -> str | None:
    """Check the style params. Returns a plain-words error, or None if OK."""
    if isinstance(stroke_width, bool) or not isinstance(
            stroke_width, (int, float)):
        return ("stroke_width must be a number between {} and {}.".format(
            MIN_STROKE_WIDTH, MAX_STROKE_WIDTH))
    if not (MIN_STROKE_WIDTH <= stroke_width <= MAX_STROKE_WIDTH):
        return ("stroke_width {} is out of range: use {} to {}.".format(
            stroke_width, MIN_STROKE_WIDTH, MAX_STROKE_WIDTH))
    if not isinstance(color, str):
        return "color must be a string."
    c = color.strip()
    if not (c.lower() == "currentcolor"
            or _HEX_COLOR.match(c)
            or _NAMED_COLOR.match(c)):
        return ("color '{}' is not valid: use 'currentColor', a hex color "
                "like #2f6bff, or a CSS color name like 'red'.".format(color))
    if isinstance(size, bool) or not isinstance(size, int):
        return "size must be a whole number of pixels."
    if not (MIN_SIZE <= size <= MAX_SIZE):
        return "size {} is out of range: use {} to {} pixels.".format(
            size, MIN_SIZE, MAX_SIZE)
    return None


def _normalize_color(color: str) -> str:
    c = color.strip()
    return "currentColor" if c.lower() == "currentcolor" else c


def _read_svg(name: str) -> str:
    """Raw bundled SVG for an icon name. Raises KeyError if unknown."""
    if name not in _svg_cache:
        path = _ICONS_DIR / (name + ".svg")
        if not path.is_file():
            raise KeyError(name)
        _svg_cache[name] = path.read_text()
    return _svg_cache[name]


def style_svg(name: str, stroke_width: float = 2.0,
              color: str = "currentColor", size: int = 24) -> str:
    """Render one icon's SVG with the given style applied.

    Raises KeyError for an unknown icon name, ValueError for bad style.
    """
    error = validate_style(stroke_width, color, size)
    if error:
        raise ValueError(error)

    root = ET.fromstring(_read_svg(name))
    root.set("width", str(size))
    root.set("height", str(size))
    root.set("stroke-width", "%g" % stroke_width)
    root.set("stroke", _normalize_color(color))
    # Drop the framework-y class attribute; keep the drawing attributes.
    if "class" in root.attrib:
        del root.attrib["class"]
    return ET.tostring(root, encoding="unicode")
