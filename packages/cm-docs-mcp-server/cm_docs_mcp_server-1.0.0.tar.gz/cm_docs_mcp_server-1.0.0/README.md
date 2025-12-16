# CM.com Documentation MCP

An MCP server that provides access to CM.com's documentation.
It dynamically fetches documentation from the [CM.com Developer Portal](https://developers.cm.com),
so documentation updates are automatically available without code changes.

## Tools

| Tool | Description |
|------|-------------|
| `list_products()` | Discover all available CM.com products/services with documentation |
| `list_pages(product)` | List all documentation pages for a specific product/service |
| `fetch_page(path)` | Fetch and read a specific documentation page |

## Installation

### Option 1: Using uvx (Recommended)

The easiest way to use this MCP server is with `uvx`. Add the MCP server to your `.mcp.json`:

From Git repository:
```json
{
  "mcpServers": {
    "cm-docs": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/cmcom-shared/cm-docs-mcp-server", "cm_docs_mcp_server"]
    }
  }
}
```

### Option 2: Manual Setup

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   .venv/Scripts/pip install -r requirements.txt  # Windows
   # or
   .venv/bin/pip install -r requirements.txt      # Linux/Mac
   ```

2. Add to your `.mcp.json`:
   ```json
   {
     "mcpServers": {
       "cm-docs": {
         "command": "/path/to/.venv/Scripts/python.exe",
         "args": ["/path/to/main.py"]
       }
     }
   }
   ```

3. Restart Claude Code and verify with `/mcp`

## Usage Example

**User:** "How do I send an RCS message with buttons?"

**Agent workflow:**
1. `list_products()` → sees "Messaging" available
2. `list_pages("messaging")` → finds RCS-related pages
3. `fetch_page("/messaging/docs/rcs-suggested-replies-messages")` → gets documentation
4. Answers with accurate, up-to-date information

## How It Works

- **Dynamic discovery**: Products are fetched from the portal's metadata
- **Page discovery**: Documentation pages are parsed from each product's navigation
- **Content extraction**: Pages are fetched and cleaned of navigation/chrome elements
- **Zero maintenance**: When the CM.com developer documentation is updated, this MCP automatically serves the new content
