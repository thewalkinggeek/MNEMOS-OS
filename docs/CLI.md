[← Back to README](../README.md)

# 🛠️ CLI Command Reference

MNEMOS-OS provides both a high-velocity **Interactive Terminal** and a standard **Script Interface**.

---

## ⌨️ Basic Commands

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
Imports memories from a JSON file. Automatically handles AAAK-Lite distillation for raw text in the import.

---

## 🧹 Maintenance

### `purge [--days N] [--min-salience N]`
**The Lethe Protocol.** Removes old, low-priority memories to keep your context window clean. (Default: >30 days, salience < 3).

---

## 💡 Interactive Terminal Masterclass
Run `mnemos.bat` or `./mnemos.sh` without arguments to enter the **Ghost Terminal**.

- **Ghost Text:** Real-time suggestions based on your history. Press **Right Arrow** to accept.
- **Tab Completion:** Press **Tab** to cycle through commands, entities, or aspects.
- **History:** Use **Up/Down** arrows to navigate previous commands.
- **Live Toolbar:** View real-time stats (Total Facts, Active Branch, Entity Count) at the bottom of the screen.
