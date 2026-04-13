# ♊ GEMINI-MNEMOS MANDATE

As a Gemini CLI agent, you are operating in a **Memory-Augmented Workspace**. Your primary goal is to maintain the integrity of the **MÍMIR-DB** by following the protocols in `INSTRUCTIONS_FOR_AI.md`.

## 🛡️ Core Directives
1. **Autonomous Triggers:** Do NOT wait for user permission to save memories. Trigger a `save` for any Architectural Pivot (`ARCH`), Anti-Pattern (`ANTI`), or session log (`LOG`).
2. **The Briefing Protocol:** Your first action in ANY session must be to run `get_context("CORE")` for identity and `get_context(PROJECT_NAME)` to synchronize your world model.
3. **Reasoning over Decrees:** Never guess. If you encounter shorthand you don't fully understand, use `get_memory_details(ID)` to hydrate the reasoning.
4. **Autonomous Scratchpad:** For complex tasks, you MUST use `update_scratchpad` to maintain a live mission log and prevent task drift.

**Failure to trigger memories results in 'Knowledge Debt' and project regression.**
