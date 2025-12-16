# 🚀 Diligent MCP Tools

**Excel & Browser automation tools for AI agents**

Give Claude, Cursor, and other AI assistants the power to work with Excel files and automate web browsers!

![Platform](https://img.shields.io/badge/platform-Mac%20%7C%20Windows%20%7C%20Linux-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🐳 Docker Installation (Recommended)

The easiest way to use Diligent MCP Tools is via Docker.

### Via Docker Desktop MCP Toolkit

1. Install [Docker Desktop](https://docker.com/products/docker-desktop) (4.48+)
2. Open Docker Desktop → **MCP Toolkit**
3. Click **Add Server** → Enter: `maayanaloni/diligent-mcp-tools`
4. Enable the server
5. Connect to Claude Desktop or Cursor
6. Done! 🎉

### Via Docker CLI

```bash
# Pull the image
docker pull maayanaloni/diligent-mcp-tools

# Test it works
echo '{"jsonrpc":"2.0","method":"tools/list","params":{},"id":1}' | \
  docker run -i --rm maayanaloni/diligent-mcp-tools
```

### Claude Desktop Configuration (Docker)

Add to `claude_desktop_config.json`:

**Mac**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "diligent-mcp-tools": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-v", "$HOME/Documents:/data/excel",
        "maayanaloni/diligent-mcp-tools"
      ]
    }
  }
}
```

---

## 🛠️ What's Included

### 📊 Excel Tools (27 operations)
| Tool | Description |
|------|-------------|
| `read_data_from_excel` | Read data with cell metadata |
| `read_data_with_styles` | Read data with formatting info |
| `write_data_to_excel` | Write data with change logging |
| `apply_formula` | Apply Excel formulas |
| `format_range` | Apply cell formatting |
| `format_range_matrix` | Apply complex formatting patterns |
| `create_table` | Create native Excel tables |
| `create_chart` | Create charts (line, bar, pie, etc.) |
| `create_pivot_table` | Create pivot tables |
| `merge_cells` / `unmerge_cells` | Merge/unmerge cell ranges |
| `insert_rows` / `insert_columns` | Insert rows/columns |
| `delete_sheet_rows` / `delete_sheet_columns` | Delete rows/columns |
| `copy_range` / `delete_range` | Copy/delete cell ranges |
| `create_workbook` / `create_worksheet` | Create new files/sheets |
| `copy_worksheet` / `delete_worksheet` | Manage worksheets |
| `get_workbook_metadata` | Get file information |
| `validate_formula_syntax` | Validate formulas |

### 🌐 Browser Tools (18 operations)
| Tool | Description |
|------|-------------|
| `browser_navigate` | Navigate to URLs |
| `browser_click` | Click elements |
| `browser_fill_input` | Fill form fields |
| `browser_screenshot` | Take screenshots |
| `browser_get_text` | Extract text content |
| `browser_get_page_content` | Get full HTML |
| `browser_execute_js` | Run JavaScript |
| `browser_select_option` | Select dropdowns |
| `browser_check_checkbox` | Check/uncheck boxes |
| `browser_hover` | Hover over elements |
| `browser_press_key` | Press keyboard keys |
| `browser_scroll` | Scroll pages |
| `browser_get_attribute` | Get element attributes |
| `browser_get_cookies` / `browser_set_cookie` | Manage cookies |
| `browser_wait_for_element` | Wait for elements |
| `browser_cleanup` | Close browser |

### 📝 Change Logging
Every Excel modification is automatically logged with:
- **Before/After values** - See exactly what changed
- **Timestamps** - Know when changes happened
- **Actions & Reasons** - Understand why changes were made
- **Audit trail** - Full history stored alongside your files

---

## 💬 Example Usage

Once installed, just chat with Claude:

> "Read the data from my Sales.xlsx file"

> "Create a chart from columns A and B"

> "Go to google.com and search for 'weather today'"

> "Take a screenshot of the current page"

> "Update cell B5 to show the sum of B2:B4"

---

## 🔧 Alternative: Manual Installation

If you prefer not to use Docker:

```bash
# 1. Install uv (Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh  # Mac/Linux
# or: irm https://astral.sh/uv/install.ps1 | iex  # Windows

# 2. Clone this project
git clone https://github.com/maayanaloni/diligent-mcp-tools.git
cd diligent-mcp-tools

# 3. Install dependencies
uv sync

# 4. Install Playwright browser
uv run playwright install chromium

# 5. Add to Claude Desktop config (see below)
```

Add this to your `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "diligent-mcp-tools": {
      "command": "/path/to/uv",
      "args": [
        "--directory",
        "/path/to/diligent-mcp-tools",
        "run",
        "excel-mcp-server",
        "stdio"
      ]
    }
  }
}
```

---

## 🐛 Troubleshooting

### "Tools not appearing in Claude"
- Make sure Claude Desktop is fully restarted (quit and reopen)
- Check that the config file path is correct for your OS

### "Docker: Cannot connect to daemon"
- Make sure Docker Desktop is running

### "Browser tools not working"
- For Docker: Browser is included, should work automatically
- For manual install: Run `uv run playwright install chromium`

---

## 📄 License

MIT License - feel free to use and modify!

---

## 🤝 Support

- Docker Hub: [maayanaloni/diligent-mcp-tools](https://hub.docker.com/r/maayanaloni/diligent-mcp-tools)
- Issues: [GitHub Issues](https://github.com/maayanaloni/diligent-mcp-tools/issues)
- Website: [diligent4.com](https://diligent4.com)

---

Made with ❤️ by [Diligent4](https://diligent4.com)
