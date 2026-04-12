# MNEMOS-OS Core Engine
# Copyright (c) 2026 Jonathan Schoenberger
# Licensed under the MIT License

import sqlite3
import os
from datetime import datetime

class MnemosCore:
    def __init__(self, db_path=None):
        if db_path is None:
            # Default to data folder relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "mnemos.db")
        self.db_path = db_path
        self._ensure_initialized()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_initialized(self):
        """Checks if the database is initialized and runs schema if not."""
        # Check if knowledge table exists
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
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
            # Fallback if run from a different context
            schema_path = os.path.join("data", "schema.sql")
            
        if os.path.exists(schema_path):
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_script = f.read()
            with self._get_conn() as conn:
                conn.executescript(schema_script)
                conn.commit()


    def add_fact(self, entity, aspect, raw_text, salience=5, file_path=None, related_id=None):
        """Compresses and saves a fact to the Mimir-DB."""
        # Salience Filter: Discard noisy text
        if len(raw_text.strip()) < 3 or raw_text.lower().strip() in ["hello", "thanks", "ok", "yes", "no"]:
            return -1 # Filtered out
            
        shorthand = self.distill(aspect, raw_text)
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (entity, aspect, shorthand, raw_content, salience, related_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (entity.upper(), aspect.upper(), shorthand, raw_text, salience, related_id))
            row_id = cursor.lastrowid
            
            # Link to file if provided
            if file_path:
                cursor.execute("""
                    INSERT INTO file_links (knowledge_id, file_path)
                    VALUES (?, ?)
                """, (row_id, file_path))
                
            conn.commit()
            return row_id

    def distill(self, aspect, text):
        """AAAK-Lite Distillation (15-word limit for better nuance preservation)."""
        prefixes = {"PREF": "*", "BUG": "!", "ARCH": "?", "DEP": "@", "LOG": ">", "ANTI": "~"}
        prefix = prefixes.get(aspect.upper(), "~")
        
        # Mapping for ultra-dense shorthand
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
            # Use map if exists, otherwise keep word
            compressed_words.append(mapping.get(w, w))
            
        # Join with minimal separators and limit length
        shorthand = "_".join(compressed_words[:15])
        return f"{prefix}{shorthand}"


    def get_memory_details(self, memory_id):
        """Retrieves full content and increments usage_count (Active Salience)."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Increment usage_count first
            cursor.execute("UPDATE knowledge SET usage_count = usage_count + 1 WHERE id = ?", (memory_id,))
            
            # Sub-query to get related memory shorthand if it exists
            cursor.execute("""
                SELECT k.entity, k.aspect, k.shorthand, k.raw_content, k.salience, k.usage_count, 
                       k.created_at, k.last_accessed, k.related_id, r.shorthand as related_shorthand
                FROM knowledge k
                LEFT JOIN knowledge r ON k.related_id = r.id
                WHERE k.id = ?
            """, (memory_id,))
            row = cursor.fetchone()
            if row:
                conn.commit()
                return {
                    "entity": row[0], "aspect": row[1], "shorthand": row[2], 
                    "raw": row[3], "salience": row[4], "usage": row[5], 
                    "created": row[6], "last_accessed": row[7],
                    "related_id": row[8], "related_shorthand": row[9]
                }
            return None

    def get_context(self, entity, limit=15, include_scratchpad=True):
        """Assembles context with Active Salience and Cross-Project Intelligence.
        Safety Guarantee: Salience 9+ (ARCH/ANTI) does not decay with age.
        """
        context_parts = []
        entity = entity.upper()
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Get Scratchpad
            if include_scratchpad:
                cursor.execute("SELECT content FROM scratchpad WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    context_parts.append(f"[SCRATCHPAD] {row[0]}")

            # 2. Local & Global Context Mix
            # Priority Logic: 
            # - If Salience >= 9: (Salience * 10) + (Usage * 2)  [NO AGE DECAY]
            # - If Salience < 9:  (Salience * 10) + (Usage * 2) - AgeInDays
            cursor.execute("""
                SELECT id, entity, shorthand, raw_content, salience, priority FROM (
                    WITH ranked_knowledge AS (
                        SELECT id, entity, shorthand, raw_content, salience, usage_count,
                            CASE 
                                    WHEN salience >= 9 THEN (salience * 10) + (usage_count * 2)
                                    ELSE (salience * 10) + (usage_count * 2) - (julianday('now') - julianday(created_at))
                            END as priority
                        FROM knowledge
                    )
                    SELECT id, entity, shorthand, raw_content, salience, priority, 1 as is_local FROM ranked_knowledge 
                    WHERE entity = ? OR entity = 'GLOBAL'
                    
                    UNION ALL
                    
                    -- High-Utility Cross-Entity 'Heat'
                    SELECT id, entity, shorthand, raw_content, salience, priority, 0 as is_local FROM (
                        SELECT * FROM ranked_knowledge 
                        WHERE entity != ? AND entity != 'GLOBAL' AND usage_count > 0
                        ORDER BY usage_count DESC LIMIT 3
                    )
                )
                ORDER BY is_local DESC, priority DESC
                LIMIT ?
            """, (entity, entity, limit))
            
            rows = cursor.fetchall()
            if rows:
                facts = []
                for row in rows:
                    mem_id, ent, shorthand, raw, salience = row[0], row[1], row[2], row[3], row[4]
                    prefix = f"[{ent}] " if ent != entity else ""
                    if salience >= 9:
                        facts.append(f"{prefix}{shorthand} [ID:{mem_id}] (FULL: {raw})")
                    else:
                        facts.append(f"{prefix}{shorthand} [ID:{mem_id}]")
                
                context_parts.append(" | ".join(facts))
                
                ids = [row[0] for row in rows]
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f"UPDATE knowledge SET last_accessed = CURRENT_TIMESTAMP WHERE id IN ({placeholders})", ids)
                conn.commit()
            
            return "\n".join(context_parts) if context_parts else "No prior context found."

    def get_file_context(self, file_path):
        """Retrieves memories linked to this file or any of its parent directories."""
        # Normalize path
        target_path = file_path.replace("\\", "/").lower()
        parts = target_path.split("/")
        
        # Build list of potential parent paths: ["src/auth/login.py", "src/auth", "src", ""]
        prefixes = [target_path]
        for i in range(1, len(parts)):
            prefixes.append("/".join(parts[:-i]))
            
        with self._get_conn() as conn:
            cursor = conn.cursor()
            placeholders = ",".join(["?"] * len(prefixes))
            # Match exact prefixes OR patterns like "%login.py"
            cursor.execute(f"""
                SELECT k.shorthand FROM knowledge k
                JOIN file_links fl ON k.id = fl.knowledge_id
                WHERE LOWER(fl.file_path) IN ({placeholders})
                OR ? LIKE '%' || LOWER(fl.file_path)
                ORDER BY k.salience DESC, k.created_at DESC
            """, (*prefixes, target_path))
            facts = [row[0] for row in cursor.fetchall()]
            # Use a set to remove duplicates if multiple patterns match
            return " | ".join(list(dict.fromkeys(facts))) if facts else ""

    def list_entities(self):
        """Returns a list of all unique entities (projects) in the database."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT entity FROM knowledge ORDER BY entity ASC")
            return [row[0] for row in cursor.fetchall()]


    def update_scratchpad(self, content):
        """Updates the persistent session scratchpad."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO scratchpad (id, content, updated_at)
                VALUES (1, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(id) DO UPDATE SET 
                    content = excluded.content,
                    updated_at = CURRENT_TIMESTAMP
            """, (content,))
            conn.commit()
            return True


    def search(self, query):
        """Uses FTS5 to find specific memories across all entities."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            # Wrap query in double quotes to handle hyphens and special chars in FTS5
            safe_query = f'"{query}"'
            cursor.execute("""
                SELECT entity, aspect, shorthand FROM knowledge_search 
                WHERE knowledge_search MATCH ?
            """, (safe_query,))
            return cursor.fetchall()

    def list_memories(self, entity=None, limit=100):
        """Returns a list of all memories, optionally filtered by entity."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            if entity:
                cursor.execute("""
                    SELECT entity, aspect, shorthand, salience, created_at 
                    FROM knowledge WHERE entity = ? 
                    ORDER BY created_at DESC LIMIT ?
                """, (entity.upper(), limit))
            else:
                cursor.execute("""
                    SELECT entity, aspect, shorthand, salience, created_at 
                    FROM knowledge ORDER BY created_at DESC LIMIT ?
                """, (limit,))
            return cursor.fetchall()

    def purge_lethe(self, days=30, min_salience=3):
        """The Lethe Protocol: Removes memories based on custom age and salience thresholds."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM knowledge 
                WHERE salience < ? 
                AND last_accessed < datetime('now', '-' || ? || ' days')
            """, (min_salience, days))
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def get_stats(self):
        """Retrieves metrics for the system toolbar."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT (SELECT COUNT(*) FROM knowledge), (SELECT COUNT(DISTINCT entity) FROM knowledge)")
            res = cursor.fetchone()
            return {"facts": res[0], "entities": res[1]}

