# 🔌 Integration Guide (MCP)

MNEMOS-OS uses the **Model Context Protocol (MCP)** to provide memory to any AI agent.

---

## ♊ Gemini CLI
Run this command to register globally:
```bash
gemini mcp add mnemos-os python "[PATH_TO_MNEMOS-OS]/cli/mcp_server.py" --scope user --trust
```

---

## 🤖 Claude Desktop
Add the following to your `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "mnemos-os": {
      "command": "python",
      "args": ["[PATH_TO_MNEMOS-OS]/cli/mcp_server.py"],
      "env": { "PYTHONPATH": "[PATH_TO_MNEMOS-OS]" }
    }
  }
}
```

---

## 🖱️ Cursor IDE
1. Open **Cursor Settings** (`Ctrl + Shift + J`).
2. Go to **Features** > **MCP**.
3. **Add new MCP server**:
   - **Name:** `MNEMOS-OS`
   - **Type:** `command`
   - **Command:** `[PATH_TO_MNEMOS-OS]/mnemos.bat mcp`

---

## 🏄 Windsurf IDE
1. Open **Settings** > **Advanced** > **Cascade** > **MCP Servers**.
2. **Add custom server +** and paste:

```json
{
  "mcpServers": {
    "mnemos-os": {
      "command": "[PATH_TO_MNEMOS-OS]/mnemos.bat",
      "args": ["mcp"]
    }
  }
}
```

---

## 🐚 Claude Code (CLI)
```bash
claude mcp add mnemos-os "[PATH_TO_MNEMOS-OS]/mnemos.bat" mcp --scope user
```

---

## 🤖 AI Briefing
After integrating, simply tell your AI agent:
> *"Read `MNEMOS-OS/INSTRUCTIONS_FOR_AI.md` and brief yourself on the memory protocols for this workspace."*
