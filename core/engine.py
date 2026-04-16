# MNEMOS-OS Core Engine
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the GNU General Public License v3.0 (GPLv3)
# See LICENSE file for full license text.

import sqlite3
import os
import json
from datetime import datetime

class MnemosCore:
    def __init__(self, db_path=None, branch='main'):
        if db_path is None:
            # Check for environment override
            db_path = os.environ.get("MNEMOS_DB_PATH")
            
        if db_path is None:
            # Default to data folder relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "mnemos.db")
        self.db_path = db_path
        self.branch = branch
        self.conn = None
        self._init_conn()
        self._ensure_initialized()
        self._migrate_branching()

    def _init_conn(self):
        """Initializes a persistent SQLite connection with WAL mode."""
        if self.conn:
            try:
                self.conn.close()
            except:
                pass
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL;")
        self.conn.execute("PRAGMA synchronous=NORMAL;")
        self.conn.commit()

    def _get_conn(self):
        """Legacy helper for backward compatibility; returns the persistent connection."""
        return self.conn

    def _is_duplicate(self, entity, aspect, raw_text, branch_name):
        """Loop Protection: Checks if an identical memory was saved in the last hour."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id FROM knowledge 
            WHERE entity = ? AND aspect = ? AND raw_content = ? AND branch = ?
            AND created_at > datetime('now', '-1 hour')
            LIMIT 1
        """, (entity.upper(), aspect.upper(), raw_text, branch_name))
        return cursor.fetchone() is not None

    def _migrate_branching(self):
        """Phase 2 Migration: Ensures branch columns and indexes exist for existing DBs."""
        cursor = self.conn.cursor()
        
        # 1. Migrate knowledge table
        cursor.execute("PRAGMA table_info(knowledge)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'branch' not in columns:
            cursor.execute("ALTER TABLE knowledge ADD COLUMN branch TEXT DEFAULT 'main'")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_branch_entity ON knowledge(branch, entity)")
        
        if 'regex_pattern' not in columns:
            cursor.execute("ALTER TABLE knowledge ADD COLUMN regex_pattern TEXT")
        
        # 2. Migrate scratchpad table (Drop/Recreate for new PK structure)
        cursor.execute("PRAGMA table_info(scratchpad)")
        sp_columns = [col[1] for col in cursor.fetchall()]
        if 'branch' not in sp_columns:
            # Backup existing content if any
            cursor.execute("SELECT content FROM scratchpad WHERE id = 1")
            row = cursor.fetchone()
            existing_content = row[0] if row else "Welcome to MNEMOS-OS. Memory active."
            
            cursor.execute("DROP TABLE IF EXISTS scratchpad")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scratchpad (
                    branch TEXT PRIMARY KEY,
                    content TEXT NOT NULL,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cursor.execute("INSERT INTO scratchpad (branch, content) VALUES ('main', ?)", (existing_content,))
        
        # 3. Migrate FTS5 (Drop/Recreate to include branch)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_search'")
        if cursor.fetchone():
            # Check if branch is in FTS table
            cursor.execute("PRAGMA table_info(knowledge_search)")
            fts_columns = [col[1] for col in cursor.fetchall()]
            if 'branch' not in fts_columns:
                cursor.execute("DROP TABLE IF EXISTS knowledge_search")
                cursor.execute("DROP TRIGGER IF EXISTS knowledge_ai")
                cursor.execute("DROP TRIGGER IF EXISTS knowledge_ad")
                cursor.execute("DROP TRIGGER IF EXISTS knowledge_au")
                self._run_schema() 
        
        self.conn.commit()

    def set_branch(self, branch_name):
        """Switches the active cognitive branch."""
        self.branch = branch_name

    def merge_branch(self, source_branch, target_branch='main'):
        """Promotes all memories from the source branch to the target branch."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE knowledge SET branch = ? WHERE branch = ?
        """, (target_branch, source_branch))
        count = cursor.rowcount
        
        # Also merge scratchpad content if target is empty
        cursor.execute("SELECT content FROM scratchpad WHERE branch = ?", (target_branch,))
        if not cursor.fetchone():
            cursor.execute("SELECT content FROM scratchpad WHERE branch = ?", (source_branch,))
            row = cursor.fetchone()
            if row:
                cursor.execute("INSERT INTO scratchpad (branch, content) VALUES (?, ?)", (target_branch, row[0]))
        
        self.conn.commit()
        return count

    def delete_branch(self, branch_name):
        """Deletes all memories and scratchpad for a specific branch."""
        if branch_name == 'main': return 0 
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM knowledge WHERE branch = ?", (branch_name,))
        count = cursor.rowcount
        cursor.execute("DELETE FROM scratchpad WHERE branch = ?", (branch_name,))
        self.conn.commit()
        return count

    def export_json(self, file_path, entity=None, branch_name=None):
        """Exports memories to a JSON file for portability."""
        active_branch = branch_name or self.branch
        cursor = self.conn.cursor()
        query = "SELECT entity, aspect, shorthand, raw_content, salience, branch FROM knowledge WHERE (branch = ? OR branch = 'main')"
        params = [active_branch]
        if entity:
            query += " AND entity = ?"
            params.append(entity.upper())
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        data = []
        for r in rows:
            data.append({
                "entity": r[0],
                "aspect": r[1],
                "shorthand": r[2],
                "raw": r[3],
                "salience": r[4],
                "branch": r[5]
            })
            
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        return len(data)

    def import_json(self, file_path):
        """Imports memories from a JSON file."""
        if not os.path.exists(file_path):
            return -1
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        count = 0
        for item in data:
            res = self.add_fact(
                entity=item['entity'],
                aspect=item['aspect'],
                raw_text=item['raw'],
                salience=item.get('salience', 5),
                branch_name=item.get('branch', 'main')
            )
            if res != -1:
                count += 1
        return count

    def _ensure_initialized(self):
        """Checks if the database is initialized and runs schema if not."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge'")
            if not cursor.fetchone():
                self._run_schema()
        except sqlite3.Error:
            self._run_schema()

    def _run_schema(self):
        """Executes the schema.sql file to initialize the database."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        schema_path = os.path.join(base_dir, "data", "schema.sql")
        
        if not os.path.exists(schema_path):
            schema_path = os.path.join("data", "schema.sql")
            
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()
            self.conn.executescript(schema_script)
            self.conn.commit()


    def add_fact(self, entity, aspect, raw_text, salience=5, file_path=None, related_id=None, branch_name=None, regex_pattern=None):
        """Compresses and saves a fact to the Mimir-DB."""
        active_branch = branch_name or self.branch
        
        # Duplicate Protection & Salience Filter
        if len(raw_text.strip()) < 3 or raw_text.lower().strip() in ["hello", "thanks", "ok", "yes", "no"]:
            return -1 
            
        if self._is_duplicate(entity, aspect, raw_text, active_branch):
            return -1 # Silent discard of redundant memory

        shorthand = self.distill(aspect, raw_text)
        
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO knowledge (entity, aspect, shorthand, raw_content, salience, related_id, branch, regex_pattern)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (entity.upper(), aspect.upper(), shorthand, raw_text, salience, related_id, active_branch, regex_pattern))
        row_id = cursor.lastrowid
        
        if file_path:
            cursor.execute("""
                INSERT INTO file_links (knowledge_id, file_path)
                VALUES (?, ?)
            """, (row_id, file_path))
            
        self.conn.commit()
        return row_id

    def distill(self, aspect, text):
        """MÍMIR-Shorthand Distillation. Supports local AI via Ollama if MNEMOS_LOCAL_DISTILL is set."""
        local_model = os.environ.get("MNEMOS_LOCAL_DISTILL")
        prefixes = {"PREF": "*", "BUG": "!", "ARCH": "?", "DEP": "@", "LOG": ">", "ANTI": "~"}
        prefix = prefixes.get(aspect.upper(), "~")
        
        if local_model:
            # Attempt Local AI Distillation (Ollama)
            try:
                import urllib.request
                import json
                
                prompt = f"Distill this technical {aspect} note into a dense 5-8 word shorthand (e.g., use_sqlite_storage). Use underscores instead of spaces. NO PREAMBLE. Text: {text}"
                data = json.dumps({
                    "model": local_model,
                    "prompt": prompt,
                    "stream": False
                }).encode("utf-8")
                
                req = urllib.request.Request("http://localhost:11434/api/generate", data=data, method="POST")
                req.add_header("Content-Type", "application/json")
                
                with urllib.request.urlopen(req, timeout=5) as f:
                    resp = json.loads(f.read().decode("utf-8"))
                    ai_shorthand = resp.get("response", "").strip().lower().replace(" ", "_")
                    if ai_shorthand and len(ai_shorthand) > 2:
                        # Clean AI output (remove prefix if AI added one)
                        if ai_shorthand[0] in prefixes.values(): ai_shorthand = ai_shorthand[1:]
                        return f"{prefix}{ai_shorthand}"
            except Exception as e:
                # Fallback to Regex if Ollama fails or isn't running
                pass

        # Regex-based Distillation (Fast Fallback)
        mapping = {
            "user": "usr", "prefers": "pref", "prefer": "pref", "architecture": "arch", 
            "database": "db", "resolved": "res", "error": "err", "function": "fn", 
            "missing": "miss", "api": "api", "calendar": "cal", "permission": "perm", 
            "using": "use", "modular": "mod", "performance": "perf", "loading": "load", 
            "memory": "mem", "authentication": "auth", "security": "sec", "initial": "init"
        }
        
        stop_words = {"the", "a", "is", "are", "to", "and", "in", "that", "of", "it", "with", "for", "on", "from", "because", "has", "was"}
        
        words = text.lower().replace("_", " ").replace("-", " ").split()
        compressed_words = []
        
        for w in words:
            if w in stop_words: continue
            compressed_words.append(mapping.get(w, w))
            
        shorthand = "_".join(compressed_words[:15])
        return f"{prefix}{shorthand}"


    def get_memory_details(self, memory_id):
        """Retrieves full content and increments usage_count (Active Salience)."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE knowledge SET usage_count = usage_count + 1 WHERE id = ?", (memory_id,))
        
        cursor.execute("""
            SELECT k.entity, k.aspect, k.shorthand, k.raw_content, k.salience, k.usage_count, 
                    k.created_at, k.last_accessed, k.related_id, r.shorthand as related_shorthand
            FROM knowledge k
            LEFT JOIN knowledge r ON k.related_id = r.id
            WHERE k.id = ?
        """, (memory_id,))
        row = cursor.fetchone()
        if row:
            self.conn.commit()
            return {
                "entity": row['entity'], "aspect": row['aspect'], "shorthand": row['shorthand'], 
                "raw": row['raw_content'], "salience": row['salience'], "usage": row['usage_count'], 
                "created": row['created_at'], "last_accessed": row['last_accessed'],
                "related_id": row['related_id'], "related_shorthand": row['related_shorthand']
            }
        return None

    def _run_guardrails(self, file_path, entity, branch_name):
        """Scans a file for regex patterns defined in ANTI/BUG memories. Zero-token defense."""
        if not file_path or not os.path.exists(file_path):
            return []
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, shorthand, regex_pattern FROM knowledge 
            WHERE (entity = ? OR entity = 'CORE') 
            AND (branch = ? OR branch = 'main')
            AND regex_pattern IS NOT NULL
        """, (entity.upper(), branch_name))
        
        rules = cursor.fetchall()
        if not rules:
            return []
            
        try:
            # High-speed local read
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except:
            return []
            
        import re
        triggered = []
        for r_id, shorthand, pattern in rules:
            try:
                # Compiled regex check
                if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
                    triggered.append(f"🛑 GUARDRAIL: {shorthand} [ID:{r_id}] detected in {os.path.basename(file_path)}")
            except:
                continue 
        return triggered

    def get_context(self, entity, limit=15, include_scratchpad=True, branch_name=None, auto_hydrate=True, relevant_to=None, file_path=None, last_hash=None):
        """Assembles context with Active Salience, Pre-Filtering, Guardrails, and Dependencies.
           `last_hash` enables Context Debouncing (Token Savings).
        """
        import hashlib
        active_branch = branch_name or self.branch
        entity = entity.upper()
        
        # 1. Dependency Mapping (Implicit Look-Around)
        extra_filters = []
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    # Scan first 30 lines for imports
                    head = [f.readline() for _ in range(30)]
                    import_text = "".join(head).lower()
                    
                    # Pull DEP memories for any mentioned libraries
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT DISTINCT entity FROM knowledge WHERE aspect = 'DEP'")
                    known_deps = [r[0] for r in cursor.fetchall()]
                    for dep in known_deps:
                        if dep.lower() in import_text:
                            extra_filters.append(dep)
            except: pass

        # 2. Assemble Content (Parts)
        context_parts = []
        
        # 2a. Guardrails
        if file_path:
            warnings = self._run_guardrails(file_path, entity, active_branch)
            if warnings:
                context_parts.append("[ACTIVE GUARDRAILS TRIGGERED]\n" + "\n".join(warnings))

        # 2b. Scratchpad
        if include_scratchpad:
            cursor = self.conn.cursor()
            cursor.execute("SELECT content FROM scratchpad WHERE branch = ?", (active_branch,))
            row = cursor.fetchone()
            if not row and active_branch != 'main':
                cursor.execute("SELECT content FROM scratchpad WHERE branch = 'main'")
                row = cursor.fetchone()
            if row:
                context_parts.append(f"[SCRATCHPAD] {row[0]}")

        # 3. Retrieval with Dependency Injection
        boosted_ids = []
        if relevant_to:
            safe_q = f'"{relevant_to}"'
            try:
                cursor.execute("""
                    SELECT rowid FROM knowledge_search 
                    WHERE knowledge_search MATCH ? AND (branch = ? OR branch = 'main')
                    LIMIT 5
                """, (safe_q, active_branch))
                boosted_ids = [r[0] for r in cursor.fetchall()]
            except: pass

        # Build combined entity filter
        entities = [entity, 'CORE'] + extra_filters
        ent_placeholders = ",".join(["?"] * len(entities))

        query = f"""
            SELECT id, entity, shorthand, raw_content, salience, priority FROM (
                WITH ranked_knowledge AS (
                    SELECT id, entity, shorthand, raw_content, salience, usage_count, branch,
                        CASE 
                                WHEN id IN ({','.join(['?']*len(boosted_ids)) if boosted_ids else '-1'}) THEN (salience * 100)
                                WHEN salience >= 9 THEN (salience * 10) + (usage_count * 2)
                                ELSE (salience * 10) + (usage_count * 2) - (julianday('now') - julianday(created_at))
                        END as priority
                    FROM knowledge
                    WHERE (branch = ? OR branch = 'main')
                )
                SELECT id, entity, shorthand, raw_content, salience, priority, 1 as is_local FROM ranked_knowledge 
                WHERE entity IN ({ent_placeholders})
                
                UNION ALL
                
                SELECT id, entity, shorthand, raw_content, salience, priority, 0 as is_local FROM (
                    SELECT * FROM ranked_knowledge 
                    WHERE entity NOT IN ({ent_placeholders}) AND usage_count > 0
                    ORDER BY usage_count DESC LIMIT 3
                )
            )
            ORDER BY is_local DESC, priority DESC
            LIMIT ?
        """
        
        cursor.execute(query, (*boosted_ids, active_branch, *entities, *entities, limit))
        rows = cursor.fetchall()
        
        if rows:
            facts = []
            for row in rows:
                mem_id, ent, shorthand, raw, salience = row['id'], row['entity'], row['shorthand'], row['raw_content'], row['salience']
                prefix = "" if ent == entity else (f"[{ent}] " if ent == 'CORE' else f"[{ent}] ")
                if salience >= 9 and auto_hydrate:
                    facts.append(f"{prefix}{shorthand} [ID:{mem_id}] (FULL: {raw})")
                else:
                    facts.append(f"{prefix}{shorthand} [ID:{mem_id}]")
            
            context_parts.append(" | ".join(facts))
            
            # Update last_accessed
            ids = [row['id'] for row in rows]
            cursor.execute(f"UPDATE knowledge SET last_accessed = CURRENT_TIMESTAMP WHERE id IN ({','.join(['?']*len(ids))})", ids)
            self.conn.commit()

        full_text = "\n".join(context_parts) if context_parts else "No prior context found."
        
        # 4. Context Debouncing (Hashing)
        new_hash = hashlib.md5(full_text.encode('utf-8')).hexdigest()
        if last_hash and last_hash == new_hash:
            return "[CONTEXT_UNCHANGED]"
            
        return f"[HASH:{new_hash}]\n{full_text}"

    def get_file_context(self, file_path):
        """Retrieves memories linked to this file or any of its parent directories."""
        target_path = file_path.replace("\\\\", "/").lower()
        parts = target_path.split("/")
        prefixes = [target_path]
        for i in range(1, len(parts)):
            parent = "/".join(parts[:-i])
            if parent: prefixes.append(parent)
            
        cursor = self.conn.cursor()
        placeholders = ",".join(["?"] * len(prefixes))
        
        cursor.execute(f"""
            SELECT k.shorthand FROM knowledge k
            JOIN file_links fl ON k.id = fl.knowledge_id
            WHERE (branch = ? OR branch = 'main')
            AND (LOWER(fl.file_path) IN ({placeholders})
            OR ? LIKE '%' || LOWER(fl.file_path))
            ORDER BY k.salience DESC, k.created_at DESC
        """, (self.branch, *prefixes, target_path))
        
        facts = [row['shorthand'] for row in cursor.fetchall()]
        return " | ".join(list(dict.fromkeys(facts))) if facts else ""

    def list_entities(self):
        """Returns a list of all unique entities in the database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT entity FROM knowledge ORDER BY entity ASC")
        return [row[0] for row in cursor.fetchall()]


    def update_scratchpad(self, content, branch_name=None):
        """Updates the persistent session scratchpad. Supports structured JSON task lists."""
        active_branch = branch_name or self.branch
        cursor = self.conn.cursor()
        
        # If content is a list/dict, serialize to JSON
        if isinstance(content, (list, dict)):
            content = json.dumps(content)
            
        cursor.execute("""
            INSERT INTO scratchpad (branch, content, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(branch) DO UPDATE SET 
                content = excluded.content,
                updated_at = CURRENT_TIMESTAMP
        """, (active_branch, content))
        self.conn.commit()
        return True

    def update_task(self, task_id, status, branch_name=None):
        """Granularly updates a specific task within the structured scratchpad JSON."""
        active_branch = branch_name or self.branch
        cursor = self.conn.cursor()
        cursor.execute("SELECT content FROM scratchpad WHERE branch = ?", (active_branch,))
        row = cursor.fetchone()
        
        if not row:
            return False
            
        try:
            tasks = json.loads(row[0])
            if not isinstance(tasks, list):
                return False
                
            updated = False
            for task in tasks:
                if str(task.get("id")) == str(task_id):
                    task["status"] = status
                    task["updated_at"] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated:
                self.update_scratchpad(tasks, branch_name=active_branch)
                return True
        except:
            return False
        return False


    def search(self, query, branch_name=None):
        """Uses FTS5 to find specific memories."""
        active_branch = branch_name or self.branch
        cursor = self.conn.cursor()
        safe_query = f'"{query}"'
        cursor.execute("""
            SELECT entity, aspect, shorthand FROM knowledge_search 
            WHERE knowledge_search MATCH ? AND (branch = ? OR branch = 'main')
        """, (safe_query, active_branch))
        return cursor.fetchall()

    def list_memories(self, entity=None, limit=100, branch_name=None):
        """Returns a list of all memories for the current branch."""
        active_branch = branch_name or self.branch
        cursor = self.conn.cursor()
        query = "SELECT entity, aspect, shorthand, salience, created_at FROM knowledge WHERE (branch = ? OR branch = 'main')"
        params = [active_branch]
        
        if entity:
            query += " AND entity = ?"
            params.append(entity.upper())
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        return cursor.fetchall()

    def purge_lethe(self, days=30, min_salience=3):
        """The Lethe Protocol: Removes stale memories."""
        cursor = self.conn.cursor()
        cursor.execute("""
            DELETE FROM knowledge 
            WHERE salience < ? 
            AND last_accessed < datetime('now', '-' || ? || ' days')
        """, (min_salience, days))
        deleted = cursor.rowcount
        self.conn.commit()
        return deleted

    def get_stats(self):
        """Retrieves metrics for the system toolbar."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT (SELECT COUNT(*) FROM knowledge), (SELECT COUNT(DISTINCT entity) FROM knowledge)")
        res = cursor.fetchone()
        return {"facts": res[0], "entities": res[1]}


