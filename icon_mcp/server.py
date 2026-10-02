"""icon-mcp: parametric Lucide icon sets for AI assistants.

No API keys, no network, no accounts. The whole Lucide set is bundled in
the package, so every call works offline. The assistant asks for icons by
name or keyword plus a style; the server hands back styled SVG markup the
assistant can save straight into a project.
"""

import json

from fastmcp import FastMCP

from icon_mcp import LUCIDE_VERSION, __version__
from icon_mcp import icons as lib

mcp = FastMCP("icon-mcp")


@mcp.tool()
def search_icons(query: str, limit: int = 10) -> str:
    """Finds Lucide icons by keyword, searching icon names and tags. Use this when you need an icon but don't know its exact name, or when the user describes an icon in plain words ("trash can", "cog", "paper plane"). Returns the best matching icon names with their tags; pass one of those names to generate_icons. Fully offline, no API key."""
    query = (query or "").strip()
    if not query:
        return "Give me a keyword to search for, e.g. 'settings' or 'arrow'."
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = 10
    hits = lib.search(query, limit)
    if not hits:
        return ("No icons matched '{}'. Try a simpler keyword like "
                "'home', 'user', or 'mail'.".format(query))
    lines = ["Icons matching '{}' ({} of {} bundled):".format(
        query, len(hits), lib.icon_count())]
    for h in hits:
        tags = ", ".join(h["tags"][:6])
        suffix = "  [tags: {}]".format(tags) if tags else ""
        lines.append("- {}{}".format(h["name"], suffix))
    return "\n".join(lines)


@mcp.tool()
def generate_icons(icons: list[str], stroke_width: float = 2.0,
                   color: str = "currentColor", size: int = 24) -> str:
    """Generates one icon or a whole matching set of Lucide icons as styled SVG markup. Each entry in `icons` can be an exact icon name ("settings") or a plain-words query ("trash can") which is resolved to the best match. Every icon is rendered with the SAME stroke_width, color, and size, so a list of many gives you a visually consistent set for a page or app. stroke_width is 0.5-4 (2 is Lucide's default); color is 'currentColor', a hex like '#2f6bff', or a CSS name like 'red'; size is pixels 1-1024. Returns JSON with the styled SVG for each icon, which you can save as .svg files. Fully offline, no API key."""
    if not icons:
        return "Give me at least one icon name or keyword, e.g. ['settings']."
    if len(icons) > lib.MAX_ICONS_PER_CALL:
        return ("Too many icons at once: {} requested, max {} per call. "
                "Split the list across calls.".format(
                    len(icons), lib.MAX_ICONS_PER_CALL))

    error = lib.validate_style(stroke_width, color, size)
    if error:
        return error

    style = {
        "stroke_width": stroke_width,
        "color": color.strip(),
        "size": size,
        "library": "lucide",
        "lucide_version": lib.lucide_version(),
    }
    results = []
    unresolved = []
    for query in icons:
        name = lib.resolve(str(query))
        if name is None:
            unresolved.append(query)
            continue
        try:
            svg = lib.style_svg(name, stroke_width, color, size)
        except (KeyError, ValueError) as e:
            unresolved.append(query)
            continue
        results.append({"query": query, "name": name, "svg": svg})

    payload = {"style": style, "icons": results, "unresolved": unresolved}
    if unresolved and not results:
        return ("None of those resolved to an icon: {}. Call search_icons "
                "with a keyword to find valid names.".format(
                    ", ".join(repr(u) for u in unresolved)))
    return json.dumps(payload, indent=2)


def main() -> None:
    """Entry point for the `icon-mcp` console script (pip/uvx installs)."""
    mcp.run()


if __name__ == "__main__":
    main()
