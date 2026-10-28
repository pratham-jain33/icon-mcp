# icon-mcp
Offline MCP server providing searchable, parametric Lucide icons for AI assistants

## Motivation
AI assistants often fall back to emojis because designers are needed for good icons. This server lets assistants search, style, and batch‑export Lucide icons completely offline, removing the need for external APIs or design work.

## Tech stack
- Python ≥3.10
- fastmcp (MCP framework)
- Lucide SVG icon set (bundled)

## Features
- Keyword search across 2000+ Lucide icons
- Parametric styling of SVGs (stroke width, color, size)
- Batch generation of consistent icon sets in a single call
- Fully offline operation – no API keys or network access required

## Installation
```bash
# Using uvx (no virtualenv needed)
uvx icon-mcp
```
Or with pip:
```bash
pip install icon-mcp
```
From source:
```bash
git clone https://github.com/pratham-jain33/icon-mcp
cd icon-mcp
python -m venv .venv
.venv/bin/pip install -e .
```

## Usage
Add the server to an MCP‑compatible assistant configuration (e.g., Claude Desktop):
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
If running from a source checkout, point to the installed module:
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
After restarting the assistant, you can ask for icons, e.g.,
> "Find me a settings icon and a trash icon, both 1.5px stroke in #2f6bff at 32px, as SVGs."
The assistant will call `search_icons` or `generate_icons` and receive styled SVG markup.

---

*Created with [repo-doctor](https://prathamjain.com/projects/repo-doctor)*
