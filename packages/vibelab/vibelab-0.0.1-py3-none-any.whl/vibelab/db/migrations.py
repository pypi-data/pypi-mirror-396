"""Database migrations."""

import sqlite3
from typing import Any


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""
    try:
        cursor = conn.execute("SELECT MAX(version) FROM schema_version")
        row = cursor.fetchone()
        return row[0] if row and row[0] is not None else 0
    except sqlite3.OperationalError:
        return 0


MIGRATIONS: list[str] = [
    # Version 1: Initial schema
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS scenarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code_type TEXT NOT NULL CHECK (code_type IN ('github', 'local', 'empty')),
        code_ref TEXT,
        prompt TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
        harness TEXT NOT NULL,
        provider TEXT NOT NULL,
        model TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued'
            CHECK (status IN ('queued', 'running', 'completed', 'failed', 'timeout')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        started_at TEXT,
        finished_at TEXT,
        duration_ms INTEGER,
        lines_added INTEGER,
        lines_removed INTEGER,
        files_changed INTEGER,
        tokens_used INTEGER,
        cost_usd REAL,
        harness_metrics TEXT,
        annotations TEXT,
        timeout_seconds INTEGER
    );
    
    CREATE INDEX IF NOT EXISTS idx_results_scenario ON results(scenario_id);
    CREATE INDEX IF NOT EXISTS idx_results_status ON results(status);
    """,
    # Version 2: Add timeout_seconds column (if it doesn't exist)
    """
    -- SQLite doesn't support IF NOT EXISTS for ALTER TABLE ADD COLUMN
    -- So we'll check if the column exists first
    -- This will fail silently if column already exists, which is fine
    -- We'll catch the error and continue
    """,
    # Version 3: Add driver column
    """
    -- Add driver column to results table
    """,
    # Version 4: Add updated_at column
    """
    -- Add updated_at column to results table
    """,
    # Version 5: Add datasets table and dataset_scenarios join table
    """
    CREATE TABLE IF NOT EXISTS datasets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE TABLE IF NOT EXISTS dataset_scenarios (
        dataset_id INTEGER NOT NULL REFERENCES datasets(id) ON DELETE CASCADE,
        scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
        PRIMARY KEY (dataset_id, scenario_id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_dataset_scenarios_dataset ON dataset_scenarios(dataset_id);
    CREATE INDEX IF NOT EXISTS idx_dataset_scenarios_scenario ON dataset_scenarios(scenario_id);
    """,
    # Version 6: Add error_message column and update status constraint
    """
    -- Add error_message column and update status constraint
    """,
    # Version 7: Add notes and quality columns
    """
    -- Add notes and quality columns to results table
    """,
    # Version 8: Add LLM judges and judgements tables
    """
    -- Add LLM scenario judges and judgements tables
    """,
]


def migrate(conn: sqlite3.Connection) -> None:
    """Apply pending migrations."""
    current = get_schema_version(conn)
    for version, sql in enumerate(MIGRATIONS, start=1):
        if version > current:
            if version == 2:
                # Version 2: Add timeout_seconds column if it doesn't exist
                try:
                    # Check if column exists
                    cursor = conn.execute("PRAGMA table_info(results)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if "timeout_seconds" not in columns:
                        conn.execute("ALTER TABLE results ADD COLUMN timeout_seconds INTEGER")
                        conn.commit()
                except Exception:
                    # Column might already exist, ignore
                    pass
            elif version == 3:
                # Version 3: Add driver column if it doesn't exist
                try:
                    cursor = conn.execute("PRAGMA table_info(results)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if "driver" not in columns:
                        conn.execute("ALTER TABLE results ADD COLUMN driver TEXT DEFAULT 'local'")
                        conn.commit()
                except Exception:
                    # Column might already exist, ignore
                    pass
            elif version == 4:
                # Version 4: Add updated_at column if it doesn't exist
                try:
                    cursor = conn.execute("PRAGMA table_info(results)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if "updated_at" not in columns:
                        conn.execute("ALTER TABLE results ADD COLUMN updated_at TEXT")
                        conn.commit()
                except Exception:
                    # Column might already exist, ignore
                    pass
            elif version == 5:
                # Version 5: Add datasets tables
                conn.executescript(sql)
            elif version == 6:
                # Version 6: Add error_message column and update status constraint
                try:
                    cursor = conn.execute("PRAGMA table_info(results)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if "error_message" not in columns:
                        conn.execute("ALTER TABLE results ADD COLUMN error_message TEXT")
                        conn.commit()
                    
                    # Update status constraint to include infra_failure
                    # SQLite doesn't support ALTER TABLE to modify CHECK constraints,
                    # so we need to recreate the table
                    # First, create a new table with the updated constraint
                    conn.execute("""
                        CREATE TABLE results_new (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            scenario_id INTEGER NOT NULL REFERENCES scenarios(id),
                            harness TEXT NOT NULL,
                            provider TEXT NOT NULL,
                            model TEXT NOT NULL,
                            status TEXT NOT NULL DEFAULT 'queued'
                                CHECK (status IN ('queued', 'running', 'completed', 'failed', 'timeout', 'infra_failure')),
                            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            started_at TEXT,
                            finished_at TEXT,
                            duration_ms INTEGER,
                            lines_added INTEGER,
                            lines_removed INTEGER,
                            files_changed INTEGER,
                            tokens_used INTEGER,
                            cost_usd REAL,
                            harness_metrics TEXT,
                            annotations TEXT,
                            timeout_seconds INTEGER,
                            driver TEXT DEFAULT 'local',
                            updated_at TEXT,
                            error_message TEXT
                        )
                    """)
                    
                    # Copy data from old table to new table
                    conn.execute("""
                        INSERT INTO results_new 
                        SELECT * FROM results
                    """)
                    
                    # Drop old table and rename new table
                    conn.execute("DROP TABLE results")
                    conn.execute("ALTER TABLE results_new RENAME TO results")
                    
                    # Recreate indexes
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_results_scenario ON results(scenario_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_results_status ON results(status)")
                    conn.commit()
                except Exception as e:
                    # If migration fails, log and continue
                    import logging
                    logging.getLogger(__name__).warning(f"Migration 6 failed: {e}")
                    pass
            elif version == 7:
                # Version 7: Add notes and quality columns if they don't exist
                try:
                    cursor = conn.execute("PRAGMA table_info(results)")
                    columns = [row[1] for row in cursor.fetchall()]
                    if "notes" not in columns:
                        conn.execute("ALTER TABLE results ADD COLUMN notes TEXT")
                    if "quality" not in columns:
                        conn.execute("ALTER TABLE results ADD COLUMN quality INTEGER CHECK (quality IS NULL OR (quality >= 1 AND quality <= 4))")
                    conn.commit()
                except Exception as e:
                    # If migration fails, log and continue
                    import logging
                    logging.getLogger(__name__).warning(f"Migration 7 failed: {e}")
                    pass
            elif version == 8:
                # Version 8: Add LLM judges and judgements tables
                try:
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS llm_scenario_judges (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            scenario_id INTEGER NOT NULL REFERENCES scenarios(id) ON DELETE CASCADE,
                            guidance TEXT NOT NULL,
                            training_sample_ids TEXT NOT NULL,  -- JSON array of result IDs
                            test_sample_ids TEXT NOT NULL,  -- JSON array of result IDs
                            alignment_score REAL,  -- NULL until trained
                            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                    conn.execute("""
                        CREATE TABLE IF NOT EXISTS judgements (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            result_id INTEGER NOT NULL REFERENCES results(id) ON DELETE CASCADE,
                            judge_id INTEGER NOT NULL REFERENCES llm_scenario_judges(id) ON DELETE CASCADE,
                            notes TEXT,
                            quality INTEGER CHECK (quality IS NULL OR (quality >= 1 AND quality <= 4)),
                            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(result_id, judge_id)
                        )
                    """)
                    
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_judges_scenario ON llm_scenario_judges(scenario_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_judgements_result ON judgements(result_id)")
                    conn.execute("CREATE INDEX IF NOT EXISTS idx_judgements_judge ON judgements(judge_id)")
                    conn.commit()
                except Exception as e:
                    # If migration fails, log and continue
                    import logging
                    logging.getLogger(__name__).warning(f"Migration 8 failed: {e}")
                    pass
            else:
                conn.executescript(sql)
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (version,))
            conn.commit()
