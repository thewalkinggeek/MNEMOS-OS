[← Back to README](../README.md)

# 🏗️ MNEMOS-OS Architecture

MNEMOS-OS is designed as a **Micro-Kernel Memory Layer**. Unlike standard vector databases or local loggers, it operates as a low-latency IPC bridge that synchronizes multiple AI agents into a single "Hive Mind."

---

## 👻 The Ghost Kernel (Ring -1)
The Ghost Kernel is a persistent background daemon that bypasses the high latency of Python startup and SQLite initialization. 

### IPC Communication (Multi-Instance Isolation)
v1.2.3 introduces **Path-Unique IPC**. The system automatically generates a unique identifier based on a hash of the project's absolute root directory. This allows multiple MNEMOS-OS projects to coexist on the same machine without IPC collisions.

- **Windows:** Uses **Named Pipes** (`\\.\pipe\mnemos_ghost_[HASH]`). 
- **Linux/macOS:** Uses **Unix Sockets** (`/tmp/mnemos_ghost_[HASH].sock`).
- **Isolation:** Each project directory has its own dedicated "Ghost" daemon. Commands like `stop` or `ping` are context-aware and only target the daemon for the current workspace.

### Performance Metrics
| Operation | Latency | Efficiency Gain |
| :--- | :--- | :--- |
| **Pure IPC** | **~0.1ms** | **2,500x Faster** vs Spawn |
| **Concurrency** | **Zero-Wait** | Multi-agent safe |
| **Context Shield (Debounced)** | **~3.7ms** | **100% Token Savings** |
| **Boundary Check** | **<1ms** | Workspace security |
| **Guardrail Scan + Filter** | **~6.3ms** | Zero-token local defense |
| **Standard Setup (Direct)** | ~30.0ms | Cold start baseline |

### Stateless Design
v1.2.0 introduced a stateless architecture where the Ghost Kernel does not "hold" a global active branch. Instead, every IPC request includes the `branch` parameter. In v1.2.3, the `GhostBridge` is also stateless, ensuring that every request establishes a fresh, isolated connection to the kernel.

---

## 🛡️ Security Boundaries (Ring 0 Defense)
v1.2.3 introduces the **Workspace Boundary Enforcement** layer within the core engine.

- **Path Sanitization:** Every file path passed to the kernel is normalized and validated against the Current Working Directory (CWD).
- **Sub-Directory Inclusion:** The kernel uses `os.path.commonpath` to ensure all children and sub-directories are accessible while blocking any attempt to escape to parent or sibling directories.
- **Data Leak Prevention:** Prevents AI agents from accidentally reading sensitive files (e.g., `.git`, `.env`, `~/.ssh`) that are not explicitly part of the project's active workspace.

---

## 🏛️ MÍMIR-DB (Storage Engine)
The core storage is powered by **SQLite 3**, optimized for high-concurrency AI workloads.

- **WAL Mode:** Write-Ahead Logging allows multiple readers and one writer to coexist without blocking.
- **FTS5 Integration:** Full-Text Search enables sub-millisecond keyword lookups across all memory shorthands and raw content.
- **Active Salience Engine:**
  - **Age Decay:** Low-salience memories lose priority over time.
  - **Hydration Boost:** High-salience memories (ARCH/ANTI) are immune to decay and auto-expand in the context window.
  - **Usage Heat:** The more a memory is hydrated, the "hotter" it becomes in the ranking algorithm.
  - **Adaptive Hydration (v1.2.2):** Introduced "Low-Power" mode. The kernel serves only shorthands by default, reducing token pressure. Full hydration is only triggered on-demand via the `details` tool.
  - **Surgical Pre-Filtering (v1.2.2):** The kernel uses the `relevant_to` parameter to perform local FTS5 keyword matching against the MÍMIR-DB, boosting the priority of relevant memories before the AI briefing is generated.

---

## 🤖 Offline Distillation (The Housekeeper)
v1.2.2 introduces **Local AI Distillation** to eliminate "Main" AI costs for memory summarization.

### Ollama Integration
When the `MNEMOS_LOCAL_DISTILL` environment variable is set to a model name (e.g., `phi3`), the kernel's `distill()` method routes all raw notes to a local Ollama instance (`localhost:11434`). 
- **Latency:** ~500ms (Internal to the user's machine).
- **Cost:** **$0.00** (Zero API tokens used for distillation).
- **Fallback:** If Ollama is offline, the kernel gracefully falls back to Regex-based pseudo-distillation.

---

## 🛡️ Executable Guardrails
Beyond passive memory, MNEMOS-OS supports **Active Local Defense**.
- **Regex Matching:** Memories can store a `regex_pattern`.
- **Ghost Interception:** The Ghost Kernel can perform high-speed, non-AI scans of the workspace to detect these patterns, providing instant warnings for known `BUG` or `ANTI` patterns without needing an LLM to "reason" about the code.

---

## 📜 Recursive Lore Inheritance
MNEMOS-OS understands project structure. When a file context is requested, the kernel traverses the directory hierarchy:
1. Exact file match.
2. Immediate parent directory.
3. Module root.
4. Project root.

This ensures that a file at `src/auth/login.py` automatically "inherits" architectural rules linked to the `src/auth/` directory.

---

## 🛡️ The Observation vs. Action Boundary
To prevent "Autonomy Overrun," the kernel enforces a strict mandate:
- **Autonomous Observations:** Saving memories and updating the scratchpad is background behavior.
- **Manual Implementation:** Modifying the workspace or executing code requires explicit user confirmation.
