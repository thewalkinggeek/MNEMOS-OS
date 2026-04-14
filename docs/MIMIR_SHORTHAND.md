[← Back to README](../README.md)

# 💎 MÍMIR-Shorthand Specification

**MÍMIR-Shorthand** is a compressed technical dialect designed for high-density AI memory within the MNEMOS-OS ecosystem. It prioritizes semantic "shorthand" over conversational prose, saving up to 90% on context window tokens.

---

## 🗣️ The Syntax Table

| Prefix | Aspect | Description | Example |
| :--- | :--- | :--- | :--- |
| `*` | **PREF** | User or coding preferences | `*pref_modular_css` |
| `!` | **BUG** | Known issues or edge cases | `!res_403_err_gcal` |
| `?` | **ARCH** | Structural/Architectural decisions | `?use_wal_mode_sqlite` |
| `@` | **DEP** | Library or external dependencies | `@dep_pydantic_v2` |
| `~` | **ANTI** | Guardrails (What NOT to do) | `~avoid_setInterval` |
| `>` | **LOG** | Significant task milestones | `>auth_refactor_done` |

---

## 🧠 The Distillation Engine
MNEMOS-OS does not store raw prose in the context window. When a fact is saved, it is passed through the distillation logic:

1. **Stop-word Removal:** Removes noise like "the", "is", "a", "because".
2. **Dense Mapping:** Replaces common technical words with 3-4 letter codes (e.g., `architecture` -> `arch`, `database` -> `db`, `performance` -> `perf`).
3. **The 15-Word Rule:** To preserve nuance while remaining dense, distillation is limited to the first 15 meaningful words.
4. **Relational Hydration:** While the *context window* only sees the shorthand, agents can use the `details` tool to "hydrate" the memory back into its original raw reasoning.

### Example Transformation
- **Input:** "We decided to use SQLite WAL mode because standard rollback journaling was causing database is locked errors during multi-agent ingest."
- **Output:** `?use_sqlite_wal_mode_std_rollback_journaling_err_db_locked_multi_agent_ingest`
