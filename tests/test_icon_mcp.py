"""Tests for icon-mcp. Everything is offline; no network, no keys."""

import asyncio
import json
import os
import sys
from xml.etree import ElementTree as ET

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from icon_mcp import icons as lib  # noqa: E402
from icon_mcp import server  # noqa: E402


# ---------------------------------------------------------------------------
# Tool registration
# ---------------------------------------------------------------------------

def test_tools_registered():
    tools = {t.name: t for t in asyncio.run(server.mcp.list_tools())}
    assert set(tools) == {"search_icons", "generate_icons"}
    for name, tool in tools.items():
        assert tool.description and len(tool.description) > 50, name
    gen_params = tools["generate_icons"].parameters["properties"]
    assert set(gen_params) == {"icons", "stroke_width", "color", "size"}
    assert set(
        tools["search_icons"].parameters["properties"]) == {"query", "limit"}


# ---------------------------------------------------------------------------
# Bundle sanity
# ---------------------------------------------------------------------------

def test_bundle_has_icons():
    assert lib.icon_count() > 1500
    assert lib.lucide_version() == "1.50.0"
    names = lib.icon_names()
    for expected in ("settings", "home", "search", "trash-2", "arrow-right"):
        assert expected in names, expected


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("query,expected_top", [
    ("settings", "settings"),
    ("trash", "trash"),
    ("trash can", "trash-2"),
    ("paper plane", "send"),
    ("cog", "cog"),
])
def test_search_finds_known_icons(query, expected_top):
    hits = lib.search(query, limit=5)
    assert hits, query
    assert hits[0]["name"] == expected_top, [h["name"] for h in hits]


def test_search_empty_query():
    assert lib.search("   ") == []


def test_search_no_match():
    assert lib.search("zzzqqqnotanicon") == []


def test_search_limit_clamped():
    assert len(lib.search("arrow", limit=500)) <= lib.MAX_SEARCH_LIMIT
    assert len(lib.search("arrow", limit=1)) == 1


def test_tool_search_icons_text():
    # Call through the underlying function regardless of wrapper shape.
    fn = getattr(server.search_icons, "fn", server.search_icons)
    out = fn("settings", 3)
    assert "settings" in out
    assert "No icons matched" not in out


def test_tool_search_icons_no_match():
    fn = getattr(server.search_icons, "fn", server.search_icons)
    assert "No icons matched" in fn("zzzqqqnotanicon", 5)


# ---------------------------------------------------------------------------
# Style validation
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("sw,color,size", [
    (2, "currentColor", 24),
    (0.5, "#2f6bff", 1),
    (4, "#FFF", 1024),
    (1.5, "red", 48),
    (2, "#2f6bff80", 24),  # 8-digit hex with alpha
    (2, "CURRENTCOLOR", 24),
])
def test_validate_style_accepts(sw, color, size):
    assert lib.validate_style(sw, color, size) is None


@pytest.mark.parametrize("sw,color,size", [
    (0, "currentColor", 24),          # stroke too thin
    (4.5, "currentColor", 24),        # stroke too thick
    ("thick", "currentColor", 24),    # stroke not a number
    (True, "currentColor", 24),       # bool is not a number here
    (2, "not a color!!", 24),        # invalid color
    (2, "#12", 24),                  # bad hex
    (2, "", 24),                     # empty color
    (2, "currentColor", 0),          # size too small
    (2, "currentColor", 2048),       # size too big
    (2, "currentColor", 24.5),       # size not an int
])
def test_validate_style_rejects(sw, color, size):
    assert lib.validate_style(sw, color, size) is not None


# ---------------------------------------------------------------------------
# SVG transform
# ---------------------------------------------------------------------------

def _parse(svg: str) -> ET.Element:
    return ET.fromstring(svg)


def test_style_svg_applies_params():
    svg = lib.style_svg("settings", stroke_width=1.5, color="#2f6bff",
                        size=48)
    root = _parse(svg)
    assert root.get("width") == "48"
    assert root.get("height") == "48"
    assert root.get("stroke-width") == "1.5"
    assert root.get("stroke") == "#2f6bff"
    assert root.get("viewBox") == "0 0 24 24"
    # The drawing itself is untouched.
    assert len(list(root)) > 0


def test_style_svg_defaults_match_lucide():
    svg = lib.style_svg("settings")
    root = _parse(svg)
    assert root.get("stroke-width") == "2"
    assert root.get("stroke") == "currentColor"
    assert root.get("width") == "24"


def test_style_svg_drops_class_attr():
    root = _parse(lib.style_svg("settings"))
    assert "class" not in root.attrib


def test_style_svg_clean_namespace():
    svg = lib.style_svg("settings")
    assert svg.startswith('<svg xmlns="http://www.w3.org/2000/svg"')
    assert "ns0" not in svg


def test_style_svg_unknown_icon():
    with pytest.raises((KeyError, ValueError)):
        lib.style_svg("this-icon-does-not-exist")


def test_style_svg_bad_style_raises():
    with pytest.raises(ValueError):
        lib.style_svg("settings", stroke_width=99)


def test_resolve_exact_and_fuzzy():
    assert lib.resolve("settings") == "settings"
    assert lib.resolve("Settings") == "settings"
    assert lib.resolve("trash can") == "trash-2"
    assert lib.resolve("zzzqqqnotanicon") is None


# ---------------------------------------------------------------------------
# generate_icons tool
# ---------------------------------------------------------------------------

def _gen(**kwargs):
    fn = getattr(server.generate_icons, "fn", server.generate_icons)
    return fn(**kwargs)


def test_generate_single_icon():
    payload = json.loads(_gen(icons=["settings"]))
    assert payload["style"]["stroke_width"] == 2.0
    assert payload["style"]["color"] == "currentColor"
    assert payload["style"]["size"] == 24
    assert len(payload["icons"]) == 1
    assert payload["icons"][0]["name"] == "settings"
    root = _parse(payload["icons"][0]["svg"])
    assert root.tag.endswith("svg")
    assert payload["unresolved"] == []


def test_generate_matching_set_same_style():
    payload = json.loads(_gen(
        icons=["home", "settings", "user", "search"],
        stroke_width=1.5, color="#7c5cff", size=32))
    assert len(payload["icons"]) == 4
    for item in payload["icons"]:
        root = _parse(item["svg"])
        assert root.get("stroke-width") == "1.5"
        assert root.get("stroke") == "#7c5cff"
        assert root.get("width") == "32"


def test_generate_fuzzy_queries_resolved():
    payload = json.loads(_gen(icons=["trash can", "paper plane"]))
    names = [i["name"] for i in payload["icons"]]
    assert "trash-2" in names
    assert "send" in names
    assert payload["icons"][0]["query"] == "trash can"


def test_generate_reports_unresolved():
    out = _gen(icons=["zzzqqqnotanicon"])
    assert "search_icons" in out  # helpful pointer, not JSON


def test_generate_mixed_resolved_and_unresolved():
    payload = json.loads(_gen(icons=["settings", "zzzqqqnotanicon"]))
    assert len(payload["icons"]) == 1
    assert payload["unresolved"] == ["zzzqqqnotanicon"]


def test_generate_rejects_bad_inputs():
    assert "stroke_width" in _gen(icons=["settings"], stroke_width=0)
    assert "color" in _gen(icons=["settings"], color="blurple!!")
    assert "at least one" in _gen(icons=[])
    many = ["settings"] * (lib.MAX_ICONS_PER_CALL + 1)
    assert "Too many" in _gen(icons=many)
