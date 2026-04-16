-- MÍMIR-DB SCHEMA (MNEMOS-OS)
-- Optimized for SQLite 3 with FTS5 for high-speed, lightweight AI context.

-- 1. The Core Knowledge Table
-- This stores the "compressed" facts and their metadata.
CREATE TABLE IF NOT EXISTS knowledge (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity TEXT NOT NULL,
    aspect TEXT NOT NULL,
    shorthand TEXT NOT NULL,
    raw_content TEXT,
    salience INTEGER DEFAULT 5,
    usage_count INTEGER DEFAULT 0, -- Tracks how often this memory is hydrated
    related_id INTEGER REFERENCES knowledge(id) ON DELETE SET NULL, -- Relational link
    branch TEXT DEFAULT 'main', -- Cognitive isolation branch
    regex_pattern TEXT, -- For local non-AI matching
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- High-Speed Indexes for Performance scaling
CREATE INDEX IF NOT EXISTS idx_knowledge_entity ON knowledge(entity);
CREATE INDEX IF NOT EXISTS idx_knowledge_salience ON knowledge(salience);
CREATE INDEX IF NOT EXISTS idx_knowledge_usage ON knowledge(usage_count);
CREATE INDEX IF NOT EXISTS idx_knowledge_created ON knowledge(created_at);
-- Composite index for Phase 2 Branching
CREATE INDEX IF NOT EXISTS idx_knowledge_branch_entity ON knowledge(branch, entity);

-- 2. Full-Text Search Virtual Table (FTS5)
-- We use a standard FTS5 table for simplicity and reliability.
-- It stores its own copy of the searchable text for maximum performance.
CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_search USING fts5(
    entity,
    aspect,
    shorthand,
    raw_content,
    branch,
    regex_pattern,
    tokenize="unicode61" -- Supports better cross-language matching
);

-- 3. Triggers to keep the Search Index synchronized with the Core Table
-- Since we are now using an internal-content FTS table, we manually sync.
CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN
  INSERT INTO knowledge_search(rowid, entity, aspect, shorthand, raw_content, branch, regex_pattern) 
  VALUES (new.id, new.entity, new.aspect, new.shorthand, new.raw_content, new.branch, new.regex_pattern);
END;

CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN
  DELETE FROM knowledge_search WHERE rowid = old.id;
END;

CREATE TRIGGER IF NOT EXISTS knowledge_au AFTER UPDATE ON knowledge BEGIN
  DELETE FROM knowledge_search WHERE rowid = old.id;
  INSERT INTO knowledge_search(rowid, entity, aspect, shorthand, raw_content, branch, regex_pattern) 
  VALUES (new.id, new.entity, new.aspect, new.shorthand, new.raw_content, new.branch, new.regex_pattern);
END;

-- 4. The Active Scratchpad (Session Continuity)
-- Updated for Phase 2: Each branch has its own scratchpad.
CREATE TABLE IF NOT EXISTS scratchpad (
    branch TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 5. File-Linked Memory
CREATE TABLE IF NOT EXISTS file_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    knowledge_id INTEGER NOT NULL,
    file_path TEXT NOT NULL,
    FOREIGN KEY(knowledge_id) REFERENCES knowledge(id) ON DELETE CASCADE
);

-- 6. The "Lethe Protocol" View
CREATE VIEW IF NOT EXISTS lethe_candidates AS
SELECT id, shorthand, entity, aspect FROM knowledge 
WHERE salience < 3 
AND last_accessed < datetime('now', '-30 days');
