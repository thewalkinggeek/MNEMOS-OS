# 📜 MNEMOS-OS Patch Notes

All notable changes to the MNEMOS-OS Kernel will be documented in this file.

## [v1.2.2] - The Token Economy & Stability Update (2026-04-16)
*Slashing AI costs and hardening IPC performance for high-concurrency environments.*

### 🚀 Zero-Friction UX
- **Transparent Launcher:** Removed the startup mode selection menu. Running `mnemos` now routes directly to the Interactive Terminal by default.
- **Unified Subcommands:** Added support for `mnemos ghost` and `mnemos mcp` directly from the primary entry point, aligning with industry-standard CLI patterns.

### 📉 Token Economy
- **Adaptive Hydration (Low-Power Mode):** Introduced the `auto_hydrate` parameter to the `get_context` core and MCP tool. When disabled, the kernel serves only 15-word shorthands, reducing per-prompt token overhead by **~80%**.
- **Surgical Pre-Filtering:** The `get_context` tool now accepts a `relevant_to` parameter (e.g., a filename or keyword). The Ghost Kernel uses FTS5 locally to prioritize relevant memories, ensuring the AI receives a precise briefing instead of a general project dump.
- **Local AI Distillation:** Memory summarization can now be offloaded to a local **Ollama** instance (e.g., Phi-3) via the `MNEMOS_LOCAL_DISTILL` environment variable, eliminating the "Main" AI token cost for housekeeping.
- **Context Throttling:** Initial implementation of token-aware context management to prevent prompt bloat.

### 🛡️ Active Guardrails (Phase 2)
- **Zero-Token Local Defense:** Implemented a high-speed local scanner in the Ghost Kernel. By attaching a `regex_pattern` to an `ANTI` or `BUG` memory, the kernel will automatically scan the active file and inject a **Hard Warning** into the context if a violation is detected. This prevents known mistakes before the AI even finishes generating code.
- **Extended Schema:** Added the `regex_pattern` column to the core MÍMIR-DB and FTS5 search index.

### 🧠 Core Reflexes (The "Final Trinity")
- **Atomic Task State:** Upgraded the `scratchpad` to a structured JSON state machine. Added the `update_task` tool, allowing AI agents to track mission progress programmatically with a "Checklist Reflex."
- **Implicit Dependency Mapping:** The kernel now automatically scans active files for `import` statements and injects relevant `DEP` (Dependency) memories into the context without being asked.
- **Context Debouncing (The Token Shield):** Implemented high-speed context hashing. If a request is identical to the previous one, the Ghost Kernel returns `[CONTEXT_UNCHANGED]`, saving **100% of tokens** for that turn.

### 🐛 Bug Fixes
- **Windows "Phantom Window" Suppression:** Resolved a bug where the Ghost Kernel auto-launch would trigger visible console windows. The daemon now runs in a fully detached, windowless state.
- **Protocol Protection:** Implemented `stdout` redirection during MCP server initialization. Stray debug prints from sub-modules now route to `stderr`, preventing JSON-RPC corruption and eliminating long "Thinking" hangs in IDEs.
- **Self-Healing IPC:** Refined the GhostBridge connection handshake to ensure the daemon is ready before serving the first request.

---

## [v1.2.1] - The Stability & Integration Update (2026-04-13)
*Refining the zero-latency experience with unified integration and hardened core stability.*

### 👻 Unified Ghost Integration
- **Direct Launch:** Added the `ghost` command to the CLI for starting the daemon (`mnemos ghost`).
- **Launcher Integration:** Added the Ghost Kernel as a selectable option [3] in the interactive menu.
- **Startup Sync:** Updated `mnemos.bat` and `mnemos.sh` to support direct Ghost routing.
- **Micro-Latency Logging:** Added real-time IPC request logging with micro-second precision (e.g., `[CONTEXT] 0.15ms`).

### 📦 Portability (JSON Serialization)
- **JSON Export:** Added `mnemos export <file>` to dump project brains into a structured, diff-friendly JSON format. 
- **JSON Import:** Added `mnemos import <file>` to populate the MÍMIR-DB from a lore package. Automatically handles MÍMIR-Shorthand distillation for raw text.
- **Git Synchronization:** Lore can now be committed to version control and shared across teams.

### 🛠️ Core Hardening
- **Persistent Connection Pooling:** Implemented long-lived SQLite connections in the core engine. Reduced latency for all memory operations and eliminated multi-agent file-locking issues.
- **MCP Protocol Hardening:** Implemented `silent` mode in `GhostBridge` to suppress console output during background daemon auto-launch. This prevents "Protocol Pollution" (stdout noise) from crashing IDE connections (Cursor/Windsurf).
- **Launcher UX:** Updated the interactive menu to clarify that MCP mode `[2]` is for manual debugging/logging only, as human-readable menus break JSON-RPC communication.
- **Context Loop Protection:** Added duplicate memory detection to `add_fact`. redundant failure reports are silently discarded within a 1-hour window to prevent context window bloat and AI crashing.
- **FTS5 Optimization:** Hardened keyword search logic for high-frequency concurrent tool calls.

### 🧹 Maintenance & Cleanup
- **Git Hygiene:** Performed a complete history scrub to remove binary database files (`mnemos.db`) from the repository history.
- **Hardened Gitignore:** Updated rules to protect all user-specific state, including local DBs, environment secrets, and IDE caches.

---

## [v1.2.0] - The Velocity Update (2026-04-13)
*This massive update focuses on radical performance gains, multi-agent stability, and knowledge portability.*

### 👻 Ghost Kernel (Ring -1)
- **Zero-Latency IPC:** Implemented a persistent background daemon using **Named Pipes (Windows)** and **Unix Sockets (Linux/macOS)**.
- **Pure IPC Performance:** Reduced memory access latency to **~0.1ms** for integrated agents.
- **Stateless Architecture:** Re-engineered the IPC bridge to be stateless, allowing multiple agents to serve different branches simultaneously without race conditions.
- **MCP Bridge:** Fully integrated the MCP Server with the Ghost Kernel, bringing zero-latency speed to IDEs like Cursor and Windsurf.

### 📦 Portability (JSON Serialization)
- **JSON Export:** Added `mnemos export <file>` to dump project brains into a structured, diff-friendly JSON format. 
- **JSON Import:** Added `mnemos import <file>` to populate the MÍMIR-DB from a lore package. Automatically handles MÍMIR-Shorthand distillation for raw text.
- **Git Synchronization:** Lore can now be committed to version control and shared across teams.

### 🌿 Cognitive Version Control
- **Branching System:** Introduced `branch`, `checkout`, and `delete-branch` to isolate experimental thoughts.
- **Knowledge Promotion:** Added `merge` functionality to promote successful experimental logic into the `main` memory bank.

### 📜 Retrieval Intelligence
- **Recursive Lore:** Enhanced `get_file_context` to traverse directory hierarchies. Files now automatically inherit architectural rules from parent folders.
- **Context Clarity:** Added explicit source tags (`[CORE]`, `[EXTERNAL: PROJECT]`) to prevent reasoning pollution.

### 🐛 Bug Fixes
- **CLI UI Logic:** Fixed a critical gap where `branch`, `merge`, and `import/export` logic were missing from the interactive terminal (`terminal.py`).
- **Tab-Completion Metadata:** Resolved a bug where command descriptions were not appearing in the Ghost Suggestions menu.
- **Windows Unicode Stability:** Fixed `UnicodeEncodeError` on Windows terminals by replacing emojis with robust ASCII markers in the Ghost Kernel.
- **Multi-Instance Concurrency:** Increased Windows Named Pipe max instances to 10, enabling simultaneous connections for multiple AI agents.
- **IPC Routing:** Fixed incorrect Ghost routing for `list` and `context` commands in the CLI bridge.

---

## [v1.1.0] - The Cognition Update (2026-04-12)
*The focus of this update was deepening the AI's relational understanding and salience logic.*

### 🧠 Core Engine
- **Relational Memory:** Added `related_id` support to link facts into logic chains.
- **Active Salience:** Implemented a dual-priority engine using **Age Decay** for noise and **Permanent Hydration** for ARCH/ANTI patterns.
- **Usage Heat:** Introduced usage tracking to keep high-utility memories "hot" in the context window.

### 💧 Memory Hydration
- **Shorthand expansion:** Added the `details` tool, allowing agents to expand dense MÍMIR-Shorthand into full technical reasoning.

### 🏛️ Discovery Protocol
- **Cross-Project Intelligence:** Added the ability to query known entities and project lists from a single interface.

---

## [v1.0.0] - Initial Release (2026-04-11)
*The birth of the MÍMIR-DB and the MÍMIR-Shorthand specification.*

- 🏛️ **MÍMIR-DB:** Initial SQLite 3 implementation with FTS5.
- 💎 **MÍMIR-Shorthand:** Introduction of the technical shorthand dialect for context window efficiency.
- ⚡ **Interactive CLI:** Basic terminal with tab-completion and history.
- 🔌 **MCP Server:** Foundation for tool-based AI memory integration.
