# 🏗️ MNEMOS-OS Architecture

MNEMOS-OS is designed as a **Micro-Kernel Memory Layer**. Unlike standard vector databases or local loggers, it operates as a low-latency IPC bridge that synchronizes multiple AI agents into a single "Hive Mind."

---

## 👻 The Ghost Kernel (Ring -1)
The Ghost Kernel is a persistent background daemon that bypasses the high latency of Python startup and SQLite initialization. 

### IPC Communication
- **Windows:** Uses **Named Pipes** (`\\.\pipe\mnemos_ghost`).
- **Linux/macOS:** Uses **Unix Sockets** (`/tmp/mnemos_ghost.sock`).

### Performance Metrics
| Operation | Latency | Efficiency Gain |
| :--- | :--- | :--- |
| **Integrated Agent (Pure IPC)** | **~0.1ms** | **2,500x Faster** vs Spawn |
| **CLI Handover (Ghost Mode)** | **~50ms** | **5x Faster** vs Direct |
| **Standard Startup (Direct)** | ~250ms | Baseline |

### Stateless Design
v1.2.0 introduced a stateless architecture where the Ghost Kernel does not "hold" a global active branch. Instead, every IPC request includes the `branch` parameter. This allows a single Ghost instance to serve different branches to different AI agents (e.g., Cursor working in `main` while a CLI tool works in `experiment`) simultaneously without race conditions.

---

## 🏛️ MÍMIR-DB (Storage Engine)
The core storage is powered by **SQLite 3**, optimized for high-concurrency AI workloads.

- **WAL Mode:** Write-Ahead Logging allows multiple readers and one writer to coexist without blocking.
- **FTS5 Integration:** Full-Text Search enables sub-millisecond keyword lookups across all memory shorthands and raw content.
- **Active Salience Engine:**
  - **Age Decay:** Low-salience memories lose priority over time.
  - **Hydration Boost:** High-salience memories (ARCH/ANTI) are immune to decay and auto-expand in the context window.
  - **Usage Heat:** The more a memory is hydrated, the "hotter" it becomes in the ranking algorithm.

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
