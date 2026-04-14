[← Back to README](../README.md)

# 🛠️ CLI Command Reference

MNEMOS-OS provides both a high-velocity **Interactive CLI** and a standard **Script Interface**.

---

## 👻 Zero-Latency IPC (Ghost Mode)

MNEMOS-OS uses a background daemon for Ring -1 performance.

### `ghost`
Launches the Ghost Kernel IPC listener. 
- **Latency:** ~0.1ms retrieval for integrated agents (MCP/IDE).
- **Protocol:** Windows Named Pipes or Unix Domain Sockets.
- **Backgrounding:** For best performance, keep this running in a separate CLI window.
- **Self-Healing:** If the Ghost Kernel is offline, the CLI will automatically attempt to spawn it in the background on your first command.

### `mcp`
Launches the Model Context Protocol (MCP) server directly.

---

## 🚀 The Launcher Menu
Run `mnemos` (or `mnemos.bat` / `./mnemos.sh`) without arguments to enter the integrated launcher:

1. **Interactive CLI:** The primary UI for humans.
2. **MCP Server:** The primary UI for AI agents (Cursor, Claude, etc.).
3. **Ghost Kernel:** The zero-latency daemon for Ring -1 performance.

---
...
## 💡 Interactive CLI Masterclass
Run `mnemos.bat` or `./mnemos.sh` without arguments to enter the **Ghost CLI**.

### `add <entity> <aspect> "<text>"`
Saves a memory to the MÍMIR-DB.
- **Entity:** Your project name (e.g., `Ocelli`) or `GLOBAL`.
- **Aspect:** `PREF`, `BUG`, `ARCH`, `DEP`, `LOG`, or `ANTI`.
- **Flags:**
  - `--salience 1-10`: Set the importance (9+ is permanent).
  - `--file <path>`: Link the memory to a specific file or directory.
  - `--related <id>`: Link to another memory ID.

### `context <entity>`
Retrieves the active mindset briefing for an AI agent. Blends local project facts with core system rules and cross-project "heat."

### `details <id>`
**Hydrates** a shorthand memory. Shows the full raw text, creation date, usage count, and relational links.

### `search "<query>"`
Keyword search across all memories and raw content (FTS5).

---

## 🌿 Cognitive Version Control (New in v1.2.0)

MNEMOS-OS allows you to treat your mindset like a Git repository.

### `branch [name]`
Lists all cognitive branches. If a name is provided, it prepares that branch for the next `add` command.

### `checkout <name>`
Switches the active cognitive branch. All subsequent `context` and `add` calls will respect this isolation.

### `merge <source>`
Promotes all memories from an experimental branch to the `main` bank.

### `delete-branch <name>`
Surgically removes an experimental branch and its associated memories.

---

## 📦 Portability (New in v1.2.1)

### `export <file>`
Exports memories to a JSON file.
- **Flags:**
  - `--entity <name>`: Optional: Only export memories for a specific project.

### `import <file>`
Imports memories from a JSON file. Automatically handles MÍMIR-Shorthand distillation for raw text in the import.

---

## 🧹 Maintenance

### `purge [--days N] [--min-salience N]`
**The Lethe Protocol.** Removes old, low-priority memories to keep your context window clean. (Default: >30 days, salience < 3).

---

## 💡 Interactive CLI Masterclass
Run `mnemos.bat` or `./mnemos.sh` without arguments to enter the **Ghost CLI**.

- **Ghost Text:** Real-time suggestions based on your history. Press **Right Arrow** to accept.
- **Tab Completion:** Press **Tab** to cycle through commands, entities, or aspects.
- **History:** Use **Up/Down** arrows to navigate previous commands.
- **Live Toolbar:** View real-time stats (Total Facts, Active Branch, Entity Count) at the bottom of the screen.
