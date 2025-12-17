# gate/ext/db.py

import sqlite3
import json
from typing import List, Optional
from models import TrackEvent, AgentRegistration

# Create persistent in-memory DB connection
conn = sqlite3.connect(":memory:", check_same_thread=False)
cursor = conn.cursor()

# Initialize DB schema
def init_db():
    # Events table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event TEXT,
        agent TEXT,
        action TEXT,
        timestamp REAL,
        success INTEGER,
        created_at TEXT,
        affected_apps TEXT
    );
    """)
    
    # Agents table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        name TEXT PRIMARY KEY,
        registered_at TEXT
    );
    """)
    conn.commit()


init_db()


# Insert event
def insert_event(e: TrackEvent):
    affected_apps_json = json.dumps(e.get("affected_apps", []))
    cursor.execute("""
        INSERT INTO events (event, agent, action, timestamp, success, created_at, affected_apps)
        VALUES (?, ?, ?, ?, ?, datetime('now'), ?)
    """, (
        e["event"],
        e["agent"],
        e["action"],
        e["timestamp"],
        1 if e.get("success") else 0 if e.get("success") is not None else None,
        affected_apps_json
    ))
    conn.commit()


# Fetch events
def list_events(limit: int = 200):
    cursor.execute("""
        SELECT id, event, agent, action, timestamp, success, created_at, affected_apps
        FROM events
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    return cursor.fetchall()

# Register agent
def register_agent(agent: AgentRegistration):
    cursor.execute("""
        INSERT OR IGNORE INTO agents (name, registered_at)
        VALUES (?, datetime('now'))
    """, (agent.name,))
    conn.commit()

# List agents
def list_agents():
    cursor.execute("SELECT name FROM agents ORDER BY name")
    return [row[0] for row in cursor.fetchall()]
