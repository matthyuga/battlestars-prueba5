-- Battlestars Saga Characters DB Schema (v1)

CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    franchise TEXT NOT NULL,
    tier TEXT NOT NULL CHECK (tier IN ('C','B','A','S','SS','SSS','IV')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(name, franchise)
);

CREATE INDEX IF NOT EXISTS idx_characters_tier ON characters(tier);
CREATE INDEX IF NOT EXISTS idx_characters_franchise ON characters(franchise);
