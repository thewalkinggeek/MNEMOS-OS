# 📜 MNEMOS-OS Patch Notes

All notable changes to the MNEMOS-OS Kernel will be documented in this file.

---

## [v1.2.0] - The Velocity Update (2026-04-13)
*The focus of this update was radical performance gains and multi-agent stability.*

### 👻 Ghost Kernel (Ring -1)
- **Zero-Latency IPC:** Implemented a persistent background daemon using **Named Pipes (Windows)** and **Unix Sockets (Linux/macOS)**.
- **Pure IPC Performance:** Reduced memory access latency from ~250ms to **~0.1ms** for integrated agents.
- **Stateless Architecture:** Re-engineered the IPC bridge to be stateless, allowing multiple agents to serve different branches simultaneously without race conditions.

### 🌿 Cognitive Version Control
- **Branching System:** Introduced `branch`, `checkout`, and `delete-branch` to isolate experimental thoughts.
- **Knowledge Promotion:** Added `merge` functionality to promote successful experimental logic into the `main` memory bank.

### 📜 Retrieval Intelligence
- **Recursive Lore:** Enhanced `get_file_context` to traverse directory hierarchies. Files now automatically inherit architectural rules from parent folders.
- **Context Clarity:** Added explicit source tags (`[CORE]`, `[EXTERNAL: PROJECT]`) to prevent reasoning pollution in multi-project environments.

### 🛡️ Safety & Documentation
- **Observation vs. Action:** Hardened the AI mandate to distinguish between autonomous memory preservation (background) and manual code implementation (foreground).
- **Documentation Refactor:** Moved heavy technical specifications into `/docs` and refactored the README into a high-impact landing page.

---

## [v1.1.0] - The Cognition Update (2026-04-12)
*The focus of this update was deepening the AI's relational understanding and salience logic.*

### 🧠 Core Engine
- **Relational Memory:** Added `related_id` support to link facts into logic chains.
- **Active Salience:** Implemented a dual-priority engine using **Age Decay** for noise and **Permanent Hydration** for ARCH/ANTI patterns.
- **Usage Heat:** Introduced usage tracking to keep high-utility memories "hot" in the context window.

### 💧 Memory Hydration
- **Shorthand expansion:** Added the `details` tool, allowing agents to expand dense AAAK-Lite shorthand into full technical reasoning.

### 🏛️ Discovery Protocol
- **Cross-Project Intelligence:** Added the ability to query known entities and project lists from a single interface.

---

## [v1.0.0] - Initial Release (2026-04-11)
*The birth of the MÍMIR-DB and the AAAK-Lite specification.*

- 🏛️ **MÍMIR-DB:** Initial SQLite 3 implementation with FTS5.
- 💎 **AAAK-Lite:** Introduction of the technical shorthand dialect for context window efficiency.
- ⚡ **Interactive CLI:** Basic terminal with tab-completion and history.
- 🔌 **MCP Server:** Foundation for tool-based AI memory integration.
