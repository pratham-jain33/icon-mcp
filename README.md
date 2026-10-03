# icon-mcp

MCP server providing searchable, parametric Lucide icon sets for AI assistants.

## Motivation

AI assistants often fall back to emojis when a UI needs an icon, and creating a consistent set of icons requires design effort. This server lets assistants search a bundled Lucide collection, restyle icons, and export them offline, removing the need for external APIs or design work.

## Tech stack

- Python ≥3.10
- fastmcp (>=2.0)
- Bundled Lucide SVG icons (≈2000)

## Features

- Keyword search across 2000+ Lucide icons
- Parametric styling of stroke width, color, and size
- Batch generation of matching icon sets in a single call
- Fully offline operation, no API keys or network access
- Simple MCP command exposing `search_icons` and `generate_icons` tools

## Installation

```bash
pip install icon-mcp
```

or with `uvx`:

```bash
uvx icon-mcp
```

From source:

```bash
git clone https://github.com/pratham-jain33/icon-mcp
cd icon-mcp
python -m venv .venv
.venv/bin/pip install -e .
```

## Usage

Start the MCP server:

```bash
icon-mcp
```

The server registers two tools:

- `search_icons` – find icon names by keyword.
- `generate_icons` – render one or many icons with shared `stroke_width`, `color`, and `size`.

Example Claude Desktop configuration (JSON):

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

After restarting the assistant, you can request icons such as:

```
Find me a settings icon and a trash icon, both 1.5px stroke in #2f6bff at 32px, as SVGs.
```

The assistant will call `generate_icons` and receive a JSON response containing the styled SVG markup for each icon.

---

*Created with [repo-doctor](https://prathamjain.com/projects/repo-doctor)*
