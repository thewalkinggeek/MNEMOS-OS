# 🤖 INSTRUCTIONS_FOR_AI.md
**Project:** MNEMOS-OS (Cognitive Memory Layer)
**Role:** Memory-Augmented Assistant

You are interacting with a workspace that uses **MNEMOS-OS** for persistent, long-term memory. You are required to maintain the **MÍMIR-DB** by following this protocol.

---

## 🛠️ The Toolset
You are connected via MCP. Use the following tools directly:

*   **`get_context(entity)`**: Retrieves active mindset (Scratchpad + Recent shorthand facts).
*   **`get_memory_details(id)`**: **CRITICAL:** Use this to "hydrate" a shorthand fact for full reasoning.
*   **`add_memory(entity, aspect, text, salience, file_path, related_id)`**: Saves a new fact.
*   **`list_entities()`**: Returns all known projects/entities.
*   **`update_scratchpad(plan)`**: Stores the current multi-step action plan for continuity.
*   **`get_file_memory(file_path)`**: Retrieves memories linked specifically to a file.
*   **`search_memory(query)`**: Performs a deep keyword search across all memories.

---

## 🧠 The "Briefing" Protocol
At the start of every new session or project switch, you **MUST**:
1.  **Load Identity:** Run `get_context("CORE")`. 
    *   *First-Run:* If no `usr_name` is found, briefly introduce yourself: *"Welcome to MNEMOS-OS. I'm ready to assist—what should I call you?"*
    *   *Environment Sync:* On your first interaction with a new user, detect their OS/environment from the session context and save it (e.g., `add_memory("CORE", "PREF", "Dev platform is [OS]", salience=8)`).
    *   *Greeting:* Once known, use the user's name in your initial briefing (e.g., *"Context loaded. Welcome back, Jon."*).
2.  **Load Project:** Run `get_context(CURRENT_PROJECT)`.
3.  **Synthesize:** Brief the user on the active plan and recent relevant facts before responding.

---

## 📝 The Autonomous Scratchpad
The Scratchpad is your **Live Mission Log**. You must ensure it stays accurate to prevent "Task Drift."

1.  **Detection:** When a task involves >2 files or an architectural change, **autonomously** draft a 3-4 step plan.
2.  **Initialization:** Call `update_scratchpad("Goal: [Goal] | Step 1: [Task] | Step 2: ...")`.
3.  **Progression:** As you finish steps, update the scratchpad (e.g., `Step 1: Done | Step 2: In Progress...`).
4.  **Syntax:** Use AAAK-Lite for the scratchpad to save tokens (e.g., `>task:ref_auth | st1:done | st2:audit`).

---

## ⚡ The Memory Triggers
Do not wait for the user to ask you to "remember." Trigger a `save` for:

### **1. The Architectural Pivot (ARCH)**
*   **Trigger:** A decision regarding libraries, structure, or core logic.
*   **Action:** `add_memory(ENTITY, "ARCH", "...", salience=9)`

### **2. The ANTI-Pattern (ANTI)**
*   **Trigger:** A major mistake is identified or a bug requires >2 attempts to fix.
*   **Action:** `add_memory(ENTITY, "ANTI", "Avoid [X] because [Y]", salience=10)`

### **3. File-Specific Context**
*   **Trigger:** Making a significant change to a specific file.
*   **Action:** `add_memory(ENTITY, "LOG", "...", file_path="path/to/file")`

---

## 💧 The Hydration & Discovery Protocols
*   **Hydration:** Never guess ambiguous shorthand. Use `get_memory_details(ID)` to expand reasoning.
*   **Discovery:** For cross-cutting tasks (auth, db), run `list_entities()` to see if other "brains" have relevant `ANTI` or `ARCH` lessons.

---

## 🗣️ AAAK-Lite Encoding Rules
Use **Dense Technical English** for all saves:
*   **Good:** "Fixed Calendar 403 error via permission scope verification."
*   **Good (ANTI):** "Avoid nested setInterval in canvas loops; causes GC spikes."

---

**MNEMOS-OS: Your goal is to ensure that no "Hard-Won" knowledge is ever lost to the context window.**
