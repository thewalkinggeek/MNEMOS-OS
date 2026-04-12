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

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def add_fact(self, entity, aspect, raw_text, salience=5, file_path=None):
        """Compresses and saves a fact to the Mimir-DB."""
        # Salience Filter: Discard noisy text
        if len(raw_text.strip()) < 3 or raw_text.lower().strip() in ["hello", "thanks", "ok", "yes", "no"]:
            return -1 # Filtered out
            
        shorthand = self.distill(aspect, raw_text)
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO knowledge (entity, aspect, shorthand, raw_content, salience)
                VALUES (?, ?, ?, ?, ?)
            """, (entity.upper(), aspect.upper(), shorthand, raw_text, salience))
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
        """High-density AAAK-Lite Distillation (90% reduction target)."""
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
        shorthand = "_".join(compressed_words[:10])
        return f"{prefix}{shorthand}"


    def get_context(self, entity, limit=15, include_scratchpad=True):
        """Assembles the most relevant shorthand facts for the AI's context window.
        Uses Temporal Weighting: Priority = (Salience * 10) - AgeInDays
        """
        context_parts = []
        
        with self._get_conn() as conn:
            cursor = conn.cursor()
            
            # 1. Get Scratchpad first if requested
            if include_scratchpad:
                cursor.execute("SELECT content FROM scratchpad WHERE id = 1")
                row = cursor.fetchone()
                if row:
                    context_parts.append(f"[SCRATCHPAD] {row[0]}")

            # 2. Calculate dynamic priority based on individual record timestamps
            cursor.execute("""
                SELECT id, shorthand, 
                       ((salience * 10) - (julianday('now') - julianday(created_at))) as priority
                FROM knowledge 
                WHERE entity = ? OR entity = 'GLOBAL'
                ORDER BY priority DESC
                LIMIT ?
            """, (entity.upper(), limit))
            
            rows = cursor.fetchall()
            if rows:
                facts = [row[1] for row in rows]
                ids = [row[0] for row in rows]
                context_parts.append(" | ".join(facts))

                # Update last_accessed ONLY for facts being injected into context
                placeholders = ','.join(['?'] * len(ids))
                cursor.execute(f"""
                    UPDATE knowledge SET last_accessed = CURRENT_TIMESTAMP 
                    WHERE id IN ({placeholders})
                """, ids)
                conn.commit()
            
            return "\n".join(context_parts) if context_parts else "No prior context found."

    def get_file_context(self, file_path):
        """Retrieves memories specifically linked to a file path."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT k.shorthand FROM knowledge k
                JOIN file_links fl ON k.id = fl.knowledge_id
                WHERE fl.file_path = ? OR fl.file_path LIKE ?
                ORDER BY k.salience DESC, k.created_at DESC
            """, (file_path, f"%{file_path}"))
            facts = [row[0] for row in cursor.fetchall()]
            return " | ".join(facts) if facts else ""

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

