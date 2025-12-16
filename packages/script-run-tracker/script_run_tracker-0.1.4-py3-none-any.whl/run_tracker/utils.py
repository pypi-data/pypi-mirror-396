# File: run_tracker/utils.py

import sqlite3
from datetime import datetime


def init_database(db_path: str):
    """
    Initialize the database with required tables

    Args:
        db_path: Path to the SQLite database file
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create flows table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flows (
            flow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flow_name TEXT NOT NULL UNIQUE,
            flow_path TEXT NOT NULL,
            description TEXT,
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create runs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            run_id INTEGER PRIMARY KEY AUTOINCREMENT,
            flow_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('running', 'success', 'fail')),
            trigger_type TEXT CHECK(trigger_type IN ('scheduler', 'manual')),
            start_time TEXT DEFAULT CURRENT_TIMESTAMP,
            finish_time TEXT,
            error_message TEXT,
            log_file_path TEXT,
            FOREIGN KEY (flow_id) REFERENCES flows (flow_id)
        )
    """)

    conn.commit()
    conn.close()
    print(f"[INFO] Database initialized at: {db_path}")


def register_flow(db_path: str, flow_name: str, flow_path: str, description: str = None):
    """
    Register a new flow in the database

    Args:
        db_path: Path to the SQLite database file
        flow_name: Name of the flow
        flow_path: Full path to the script file
        description: Optional description of the flow
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute(
            """INSERT INTO flows (flow_name, flow_path, description) 
               VALUES (?, ?, ?)""",
            (flow_name, flow_path, description)
        )
        conn.commit()
        flow_id = cursor.lastrowid
        print(f"[INFO] Flow registered: {flow_name} (ID: {flow_id})")
    except sqlite3.IntegrityError:
        print(f"[WARNING] Flow '{flow_name}' already exists")
    finally:
        conn.close()


def deactivate_flow(db_path: str, flow_name: str):
    """
    Deactivate a flow

    Args:
        db_path: Path to the SQLite database file
        flow_name: Name of the flow to deactivate
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE flows SET is_active = 0 WHERE flow_name = ?",
        (flow_name,)
    )
    conn.commit()

    if cursor.rowcount > 0:
        print(f"[INFO] Flow '{flow_name}' deactivated")
    else:
        print(f"[WARNING] Flow '{flow_name}' not found")

    conn.close()