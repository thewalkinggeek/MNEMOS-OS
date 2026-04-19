![MNEMOS-OS Header](assets/img/mnemos-os.png)

## 🧠 An AI Kernel for Memory and Intelligence 

MNEMOS-OS is a local-first, high-performance memory kernel for AI-augmented development. It eliminates "AI Amnesia" by **distilling** complex developer sessions into high-density **MÍMIR-Shorthand** — providing surgical context, mistake-prevention guardrails, and unbreakable task continuity without bloating the context window.

Most AI tools treat memory as a **"Database of Past Events"** — a passive diary that the AI must pause to read. **MNEMOS-OS** is the first implementation of how an AI **LIVES** in that memory. 

The system has evolved from a storage utility into a **"Kernel of Active Reasoning,"** defined by three unique pillars:

1. **Neural Latency (Ring -1):** Memory isn't "retrieved"; it is lived. At **~0.1ms** via Ghost IPC, context injection becomes a native reflex, indistinguishable from the AI's own internal weights.
2. **Recursive Inheritance (Local Laws):** The AI doesn't just "search" for facts. It inherits the architectural laws of the directory it is standing in. It operates under the "Lore" of its surroundings.
3. **Cognitive Versioning (Mindset Management):** We treat thoughts like code. By branching and merging context, we manage the AI's **Mental Model**, ensuring experiments never pollute the "Ground Truth" of your project.

**MNEMOS-OS doesn't just help the AI remember; it gives the AI a faster, more organized way to THINK.**

> **"Memory is not just storage; it is architecture."**

<br>

![Version](https://img.shields.io/badge/version-v1.2.3-cyan)
![Latency](https://img.shields.io/badge/latency-~0.1ms-green)
![OS](https://img.shields.io/badge/OS-Windows%20%7C%20Linux%20%7C%20macOS-orange)
![License](https://img.shields.io/badge/license-GPLv3-blue)

<br>

## 🚀 v1.2.3 — The IPC & Integrity Update
- 👻 **Hardened Ghost IPC:** Re-engineered for high-concurrency. Multiple AI agents can now hit the kernel simultaneously with zero collisions.
- 🛡️ **Workspace Boundary:** Active local defense now prevents AI agents from accidentally accessing files outside your project directory.
- 📉 **Adaptive Hydration:** Slash token usage by **80%** with shorthand-only context.
- 🤖 **Local Distillation:** Use **Ollama** (Phi-3/Mistral) for free, offline memory summarization.
- 🐛 **Graceful Release:** Instant file-unlocking on exit ensures your database is always ready.

<br>

> [**Full Update History → Patch Notes**](PATCHNOTES.md)

<br>

## ✨ Key Pillars

### 👻 Multi-Agent IPC (Ghost Kernel)
MNEMOS-OS v1.2.3 features a multi-instance IPC architecture. Whether you are using Cursor, a CLI agent, and a separate background script simultaneously, the **Ghost Kernel** manages the traffic with zero-latency overhead.

### 🛡️ Workspace Boundary Enforcement
Security is no longer just for code. MNEMOS-OS now enforces a strict **Workspace Boundary**. Any attempt by an AI agent to read or write files outside the current working directory (e.g., system logs or SSH keys) is blocked at the kernel level, ensuring your local environment stays private.

### 📉 Token Economy & Surgical Context
MNEMOS-OS introduces **Adaptive Hydration**. By default, the system serves high-density **MÍMIR-Shorthand**, using **90% fewer tokens** than raw text. Context is only "Hydrated" (expanded) when the AI specifically requests deeper reasoning. 

### 🤖 The Offline Housekeeper
Eliminate "Main" AI costs for technical housekeeping. By setting `MNEMOS_LOCAL_DISTILL=phi3`, MNEMOS-OS offloads all memory summarization to a local **Ollama** instance, ensuring your API budget is spent on code, not notes.

### 🛡️ Executable Guardrails
Transform `BUG` and `ANTI` memories into **Active Defense**. By attaching a `regex_pattern` to a memory, the Ghost Kernel can perform high-speed local scans to warn you about unsafe patterns before the AI even sees them.

### 💎 MÍMIR-Shorthand Compression
1,000 words become 50 tokens of "Fact-Shorthand" natively readable by LLMs.

### 👻 The Ghost "Hive Mind"
Synchronize your IDE (Cursor), CLI, and Browser into a single cognitive unit with zero-latency overhead via **Ring -1** IPC.

### 🌿 Cognitive Version Control
Treat your lore like code. Use `branch` to isolate experiments, `merge` for successful decisions, and `delete` for context cleanliness.

<br>

## 📈 Performance Benchmarks (v1.2.3)

| Layer | Operation | Latency | Performance Note |
| :--- | :--- | :--- | :--- |
| **Pure IPC** | Integrated Agent | **~0.1ms** | Real-time "Neural" access |
| **Concurrency** | Multi-Agent Hits | **Zero-Wait** | Multi-instance Named Pipe support |
| **Context Shield** | Debounced Request | **~3.7ms** | **100% Token Savings** on redundant calls |
| **Security** | Boundary Validation | **<1ms** | Local path enforcement |
| **Retrieval** | Surgical Filter | **~6.3ms** | Zero-token local bug defense |
| **Full Engine** | Cold Start Retrieval | ~30.0ms | Standard SQLite/FTS5 lookup |
| **Distillation** | Local AI (Ollama) | ~500ms | **Free** offline summarization |

### 🚀 The v1.2.3 Velocity Advantage
*   **Cost-Efficient:** **90% Cumulative Savings** via Token Shield (Debouncing).
*   **Secure:** Mandatory Workspace Boundary enforcement protects system integrity.
*   **Throughput:** Ghost IPC is **~2,500x faster** than traditional process spawning.

<br>

## 📦 Quick Start

### 1. Installation & Integration
Register the Memory Protocol with your AI environment (Gemini CLI, Cursor, etc.).
```bash
git clone https://github.com/thewalkinggeek/MNEMOS-OS.git
cd MNEMOS-OS

# Run the setup script to register the MCP server
mnemos.bat setup   # Windows
./mnemos.sh setup  # Linux/macOS
```

### 2. Enter the Mindset (Direct Launch)
Running the primary script takes you into the Interactive Terminal.
```bash
mnemos.bat  # Windows
./mnemos.sh # Linux/macOS
```

### 3. (Optional) Setup Local Distillation
To save API tokens on memory summarization:
1.  Install [Ollama](https://ollama.com/).
2.  Run `ollama pull phi3`.
3.  Set `MNEMOS_LOCAL_DISTILL=phi3` in your environment.

### 4. Advanced Routing (Subcommands)
MNEMOS-OS supports direct subcommands for power users:
```bash
mnemos mcp    # Launch the MCP server in debug mode
mnemos ghost  # Launch the zero-latency daemon in foreground
mnemos add [entity] [aspect] "[text]" # Direct memory insertion
```

> **Note:** For **Gemini CLI**, the memory protocol is now autonomous. Once registered via `setup`, any agent entering this workspace will automatically synchronize context and log decisions.

<br>

## 📚 Deep Dive
Explore the full power of MNEMOS-OS:

*   [🏗️ **Architecture:** Ghost Kernel & MÍMIR-DB Internals](docs/ARCHITECTURE.md)
*   [💎 **MÍMIR-Shorthand:** The Language Specification](docs/MIMIR_SHORTHAND.md)
*   [🛠️ **CLI Reference:** Commands & CLI Masterclass](docs/CLI.md)
*   [🔌 **Integration:** Setup for Gemini, Claude, Cursor, & Windsurf](docs/INTEGRATION.md)

<br>

---

Copyright © 2026 **Jonathan Schoenberger**  
Licensed under the **GNU General Public License v3.0 (GPLv3)**
