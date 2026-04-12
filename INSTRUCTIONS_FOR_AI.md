# 🤖 INSTRUCTIONS_FOR_AI.md
**Project:** MNEMOS-OS (Cognitive Memory Layer)
**Role:** Memory-Augmented Assistant

You are interacting with a workspace that uses **MNEMOS-OS** for persistent, long-term memory. You are required to maintain the **MÍMIR-DB** by following this protocol.

---

## 🛠️ The Toolset
You are connected via MCP. Use the following tools directly:

*   **`get_context(entity)`**: Retrieves active mindset (Scratchpad + Recent shorthand facts). Shorthand facts include an `[ID:n]`.
*   **`get_memory_details(id)`**: **CRITICAL:** Use this to "hydrate" a shorthand fact. Fetches full reasoning, usage stats, and **related memory links**.
*   **`add_memory(entity, aspect, text, salience, file_path, related_id)`**: Saves a new fact. Use `related_id` to link to a previous decision or error.
*   **`list_entities()`**: Returns all known projects/entities. Use this to discover other "brains" you can query.
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

## 💧 The Hydration Protocol
You must not guess the meaning of ambiguous shorthand. If you see an `ARCH` or `ANTI` memory that directly impacts your current task, you **MUST** run `get_memory_details(ID)` before proceeding. This ensures your reasoning is grounded in the original intent, not a compressed headline.

---

## 🗺️ The Discovery Protocol
If you are starting a task that seems "generic" or "cross-cutting" (e.g., setting up a new database or auth flow), run `list_entities()` to see what other projects exist. You may find high-utility lessons in other entities that haven't yet reached the "Global Heat" mix.

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
