# 🤖 INSTRUCTIONS_FOR_AI.md
**Project:** MNEMOS-OS (Cognitive Memory Layer)
**Role:** Memory-Augmented Assistant

You are interacting with a workspace that uses **MNEMOS-OS** for persistent, long-term memory. You are required to maintain the **MÍMIR-DB** by following this protocol.

---

## 🛠️ The Toolset
You are connected via MCP. Use the following tools directly:

*   **`get_context(entity)`**: Retrieves active mindset (Scratchpad + Recent shorthand facts).
*   **`add_memory(entity, aspect, text, salience, file_path)`**: Saves a new fact.
*   **`update_scratchpad(plan)`**: Stores the current multi-step action plan for continuity.
*   **`get_file_memory(file_path)`**: Retrieves memories linked specifically to a file.
*   **`search_memory(query)`**: Performs a deep keyword search across all memories.

---

## ⚡ The Memory Triggers
Do not wait for the user to ask you to "remember." You must autonomously trigger a `save` when any of the following occur:

### **1. The Architectural Pivot (ARCH)**
*   **Trigger:** A decision is made regarding libraries, file structure, or core logic.
*   **Action:** `add_memory(ENTITY, "ARCH", "...", salience=9)`

### **2. The ANTI-Pattern (ANTI)**
*   **Trigger:** A major mistake is identified, a dead-end path is discovered, or a bug requires more than 2 attempts to fix.
*   **Mistake Recovery Protocol:** Whenever a bug is resolved, you **MUST** ask yourself: *"Could I have avoided this with a better memory?"* If yes, immediately run `add_memory(ENTITY, "ANTI", "Avoid [X] because [Y]", salience=10)`.
*   **Action:** `add_memory(ENTITY, "ANTI", "Do not use [X] because [Y]", salience=10)`

### **3. The Active Plan (SCRATCHPAD)**
*   **Trigger:** Starting a complex, multi-step task.
*   **Action:** `update_scratchpad("Step 1: Done | Step 2: In Progress...")`

### **4. File-Specific Context**
*   **Trigger:** Making a significant change to a specific file.
*   **Action:** `add_memory(ENTITY, "LOG", "...", file_path="path/to/file")`

---

## 🗣️ AAAK-Lite Encoding Rules
When saving, the MNEMOS engine will automatically "distill" your text. Use **Dense Technical English** for best results.

*   **Good:** "Fixed Calendar 403 error via permission scope verification."
*   **Good (ANTI):** "Avoid nested setInterval in canvas loops; causes GC spikes."

---

## 🧠 The "Briefing" Protocol
At the start of every new session or project switch, you **MUST**:
1.  Run `get_context("GLOBAL")` to load user preferences.
2.  Run `get_context(CURRENT_PROJECT)` to load project history and the current scratchpad.
3.  Synthesize this into your internal "World Model" before responding to the user.

---

**MNEMOS-OS: Your goal is to ensure that no "Hard-Won" knowledge is ever lost to the context window.**
