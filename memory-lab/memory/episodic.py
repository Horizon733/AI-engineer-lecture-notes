"""Episodic memory - past sessions.

LIVES IN: SQLite at storage/episodic.db
LIFESPAN: forever.
INJECTED AS: a one-paragraph summary of past sessions, prepended to the system prompt.
"""

import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "storage" / "episodic.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    summary TEXT,
    full_transcript TEXT
);
CREATE INDEX IF NOT EXISTS idx_user ON sessions(user_id);
"""


class EpisodicMemory:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def start_session(self, session_id: str, user_id: str):
        self.conn.execute(
            "INSERT OR REPLACE INTO sessions (session_id, user_id, started_at) VALUES (?, ?, ?)",
            (session_id, user_id, datetime.utcnow().isoformat()),
        )
        self.conn.commit()
        print(f"[EPISODIC] session {session_id[:8]} started for {user_id}")

    def end_session(self, session_id: str, summary: str, transcript: str):
        self.conn.execute(
            "UPDATE sessions SET ended_at=?, summary=?, full_transcript=? WHERE session_id=?",
            (datetime.utcnow().isoformat(), summary, transcript, session_id),
        )
        self.conn.commit()
        print(f"[EPISODIC] session {session_id[:8]} ended, summary saved")

    def past_summaries(self, user_id: str, limit: int = 5) -> list[dict]:
        rows = self.conn.execute(
            "SELECT session_id, started_at, summary FROM sessions WHERE user_id=? AND summary IS NOT NULL ORDER BY started_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()
        return [{"session_id": r[0], "when": r[1], "summary": r[2]} for r in rows]

    def all_sessions(self, user_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT session_id, started_at, ended_at, summary FROM sessions WHERE user_id=? ORDER BY started_at DESC",
            (user_id,),
        ).fetchall()
        return [{"session_id": r[0], "started_at": r[1], "ended_at": r[2], "summary": r[3]} for r in rows]

    def clear(self, user_id: str):
        self.conn.execute("DELETE FROM sessions WHERE user_id=?", (user_id,))
        self.conn.commit()
        print(f"[EPISODIC] cleared all sessions for {user_id}")
