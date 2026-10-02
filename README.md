# icon-mcp

mcp-name: io.github.pratham-jain33/icon-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)
[![Version](https://img.shields.io/badge/version-v0.1.0-orange.svg)](https://github.com/pratham-jain33/icon-mcp/releases)
[![PyPI](https://img.shields.io/pypi/v/icon-mcp.svg)](https://pypi.org/project/icon-mcp/)

Give any AI assistant a custom icon button. No emojis, no designer needed.

> **Unofficial community project.** Not made by, endorsed by, or affiliated with Lucide. The Lucide icon set (ISC licensed) is bundled inside the package, so everything works offline.

## Why

AI assistants reach for emojis when a UI needs an icon, because drawing a good icon is actual design work. This server plugs into any MCP-compatible assistant (Claude Desktop, Claude Code, Cursor, and more) and lets it **search 2000+ Lucide icons by keyword, restyle them** (stroke width, color, size), and **generate a whole matching set in one call** so every icon on the page looks like it belongs together. The SVGs come back as markup the assistant saves straight into the project. No API key, no account, no network.

## Tools

| Tool | Description |
|------|-------------|
| `search_icons` | Finds icons by keyword across names and tags. Use when you don't know the exact icon name. |
| `generate_icons` | Renders one icon or a whole matching set as styled SVG markup. Takes names or plain-words queries plus shared `stroke_width`, `color`, `size`. |

## Quickstart

**Install**

No cloning needed:

```bash
uvx icon-mcp
```

or with pip:

```bash
pip install icon-mcp
```

From source instead:

```bash
git clone https://github.com/pratham-jain33/icon-mcp
cd icon-mcp
python -m venv .venv
.venv/bin/pip install -e .
```

**Connect your assistant**

Claude Desktop config file:

- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "icon-mcp": {
      "command": "uvx",
      "args": ["icon-mcp"]
    }
  }
}
```

No environment variables, no keys. From source, point at your checkout instead:

```json
{
  "mcpServers": {
    "icon-mcp": {
      "command": "/absolute/path/to/icon-mcp/.venv/bin/python",
      "args": ["-m", "icon_mcp.server"]
    }
  }
}
```

Restart Claude Desktop, then try: *"Find me a settings icon and a trash icon, both 1.5px stroke in #2f6bff at 32px, as SVGs."*

## Configuration

None. There is nothing to configure: no API keys, no accounts, no network access. The icon set ships inside the package.

## How it works

1. You ask the assistant for icons in plain words.
2. The assistant calls `search_icons` to find the right names, or passes keywords straight to `generate_icons`.
3. The server resolves each query to a bundled Lucide SVG and rewrites four attributes on it: `width`, `height`, `stroke-width`, `stroke`. Pure XML manipulation, no rendering, no native dependencies.
4. Every icon in one call gets the identical style, so the set is visually consistent by construction.
5. The server returns JSON with the SVG markup per icon; the assistant saves them as `.svg` files in your project.

## Example session

```
You:    I need icons for my landing page nav: home, features, pricing,
        contact. Make them all match: thin 1.5 stroke, blue #2f6bff.

Claude: [calls generate_icons with ["home", "features", "pricing",
        "contact"], stroke_width=1.5, color="#2f6bff"]
        Done. Four SVGs, all 1.5px stroke in #2f6bff, saved to icons/.
        "features" resolved to the "sparkles" icon, "contact" to "mail".
```

## Why icon-mcp instead of Unicon

[Unicon](https://github.com/webrenew/unicon) is the closest existing tool: an MCP server over a hosted icon API with 19,000+ icons across 9 libraries. icon-mcp takes the opposite trade:

- **Fully offline.** The whole set is bundled in the package. No hosted API, works on a plane.
- **No account, no tiers.** Free forever, nothing to sign up for.
- **Python-native.** Installs with `uvx`/`pip`; no Node or npx needed.
- **One-call consistent sets.** Pass a list of icons plus one style; every SVG comes back matching. The style params (stroke width, color, size) are first-class, not an afterthought.
- **Smaller, calmer surface.** Two tools, one library, zero config.

The trade: one library (Lucide) instead of nine, and keyword search instead of semantic search. For shipping a consistent icon set on a page, that's the whole job.

## Parameters

`generate_icons` accepts:

| Parameter | Default | Rules |
|-----------|---------|-------|
| `icons` | (required) | 1-50 names or keyword queries, e.g. `["home", "trash can"]` |
| `stroke_width` | `2.0` | 0.5 to 4 (2 is Lucide's default) |
| `color` | `"currentColor"` | `currentColor`, hex (`#2f6bff`), or CSS name (`red`) |
| `size` | `24` | 1 to 1024 pixels |

Queries that don't resolve are reported in the `unresolved` list instead of failing the whole call.

## Roadmap

- [x] v0.1 — bundled Lucide set (v1.50.0), keyword search, parametric SVG styling, batch sets in one call
- [ ] Website: paste a prompt, download a styled set
- [ ] More libraries (Tabler, Heroicons) as opt-in bundles

## Contributing

Issues and pull requests are welcome. If you add a tool, write its description the way you'd explain it to a smart friend who has never seen it — the assistant reads that text to decide when to use it. To refresh the icon bundle against a newer Lucide release, bump `LUCIDE_VERSION` in `scripts/fetch_lucide.py` and run it.

## License

MIT © Pratham Jain. See [LICENSE](LICENSE).

## Acknowledgments

Built on [Lucide](https://lucide.dev)'s icon set (ISC licensed, see `icon_mcp/LUCIDE_LICENSE`) and the [Model Context Protocol](https://modelcontextprotocol.io/).
