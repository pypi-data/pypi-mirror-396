# Engram

**The permanent and semantic memory layer for AI agents.**

<div align="center">
  <p><em>A better-notion-mcp bridge for effortless usage of Notion as a knowledge base.</em></p>
</div>

## Introduction

**Engram** transforms your Notion workspace into a living, cognitive substrate for your AI agents.

### Why Engram?
According to neuropsychology, an **engram** is a unit of cognitive information imprinted in a physical substance, theorized to be the means by which memories are stored. This MCP server acts as that physical bridge, allowing your AI to:
- **Encode Information**: Instantly store facts in a local vector-like "synaptic" database.
- **Stimulate Recall**: Semantically search your entire knowledge base to retrieve context.
- **Imprint Knowledge**: Create and edit rich Notion pages (markdown, tables, mermaid) as permanent memory traces.

## Features

| Feature Category | Tool Name | Description | Arguments |
| :--- | :--- | :--- | :--- |
| **Memory** | `remember_fact` | Store a text snippet (memory trace) in the local synaptic database. | `fact` (str) |
| | `search_memory` | Semantically retrieve facts ("Stimulate Recall"). | `query` (str) |
| | `get_recent_memories` | Retrieve the most recent memory traces. | `limit` (int) |
| **Page Management** | `create_page` | Create a new sub-page under your root page. | `title` (str), `content` (str) |
| | `list_sub_pages` | List all child pages of a specific page. | `parent_id` (str, optional) |
| | `read_page_content` | Read and parse the content of a page as Markdown. | `page_id` (str) |
| **Content Editing** | `update_page` | Append rich content (paragraphs, code, tables) to a page. | `page_id` (str), `title` (str), `content` (str), `type` (str), `language` (str) |
| | `log_to_notion` | Fast way to append a daily log/note to the root page. | `title` (str), `content` (str) |
| **Utilities** | `send_alert` | Send a push notification via Telegram. | `message` (str) |

## Prerequisites

Before using this tool, ensure you have **Python 3.10 or higher** installed.

<details>
<summary><strong>Installing uv (Recommended)</strong></summary>

We recommend using **uv** for the best experience.
[Download uv here](https://docs.astral.sh/uv/)

</details>

<details>
<summary><strong>Installing pipx (Alternative)</strong></summary>

If you prefer `pipx`, install it using these universal commands (works on Windows, Mac, and Linux):

```bash
# 1. Install pipx (user scope)
python3 -m pip install --user pipx

# 2. Add to PATH
python3 -m pipx ensurepath

# 3. Verify
pipx --version
```
</details>

## Configuration

### 1. Notion Setup
*   **Integration Token**: Go to [Notion My Integrations](https://www.notion.so/my-integrations) -> New Integration -> Copy the "Internal Integration Secret".
*   **Page ID**: Open the Notion page you want to use as the root. Copy the alphanumeric ID from the URL. **Don't forget to connect this page to your specific integration**.

### 2. Environment Variables

| Variable | Description | Default / Note | Required |
| :--- | :--- | :--- | :---: |
| `NOTION_API_KEY` | Your Notion Integration Secret. | - | ✅ |
| `NOTION_PAGE_ID` | The ID of the root page for creating/listing content. | - | ✅ |
| `TELEGRAM_BOT_TOKEN` | Token from @BotFather for alerts. | Optional | ❌ |
| `TELEGRAM_CHAT_ID` | Your Chat ID for receiving alerts. | Optional | ❌ |
| `AGENT_MEMORY_PATH` | Path to the local SQLite DB. | **Win**: `C:\Users\<User>\.engram\data\`<br>**Mac**: `~/Library/.engram/data/` | ❌ |

## Client Setup

Add the following to your MCP client configuration (e.g., `claude_desktop_config.json` for Claude Desktop).

### Recommended: `uv`

```json
{
  "mcpServers": {
    "engram": {
      "command": "uvx",
      "args": ["engram-mcp"],
      "env": {
        "NOTION_API_KEY": "secret_...",
        "NOTION_PAGE_ID": "page_id_...",
        "TELEGRAM_BOT_TOKEN": "bot_token_...",
        "TELEGRAM_CHAT_ID": "chat_id_...",
        "AGENT_MEMORY_PATH": "/path/to/db"
      }
    }
  }
}
```

<details>
<summary><strong>Alternative: <code>pipx</code></strong></summary>

```json
{
  "mcpServers": {
    "engram": {
      "command": "pipx",
      "args": ["run", "engram-mcp"],
      "env": {
        "NOTION_API_KEY": "secret_...",
        "NOTION_PAGE_ID": "page_id_...",
        "TELEGRAM_BOT_TOKEN": "bot_token_...",
        "...": "..."
      }
    }
  }
}
```
</details>

## License

This project is licensed under the MIT License.
