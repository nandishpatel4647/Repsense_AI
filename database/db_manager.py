"""
RepSense AI - Database Manager
SQLite-based persistence for workout session history.
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Optional
from dataclasses import dataclass

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "repsense.db")


@dataclass
class SessionRecord:
    id: Optional[int]
    date: str
    duration_seconds: float
    total_reps: int
    avg_rep_speed: float
    form_score: float
    calories_burned: float
    grade: str


class DatabaseManager:
    """
    Handles all SQLite operations for workout history.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = os.path.abspath(db_path)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workout_sessions (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    date            TEXT NOT NULL,
                    duration_secs   REAL NOT NULL,
                    total_reps      INTEGER NOT NULL,
                    avg_rep_speed   REAL,
                    form_score      REAL,
                    calories        REAL,
                    grade           TEXT,
                    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def save_session(
        self,
        duration_secs: float,
        total_reps: int,
        avg_rep_speed: float,
        form_score: float,
        calories: float,
        grade: str,
    ) -> int:
        """Save a completed workout session. Returns new session ID."""
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO workout_sessions
                    (date, duration_secs, total_reps, avg_rep_speed, form_score, calories, grade)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (date_str, duration_secs, total_reps, avg_rep_speed, form_score, calories, grade))
            conn.commit()
            return cursor.lastrowid

    def get_all_sessions(self) -> List[SessionRecord]:
        """Fetch all workout sessions, newest first."""
        with self._get_connection() as conn:
            rows = conn.execute("""
                SELECT id, date, duration_secs, total_reps, avg_rep_speed,
                       form_score, calories, grade
                FROM workout_sessions
                ORDER BY created_at DESC
            """).fetchall()
        return [
            SessionRecord(
                id=row["id"],
                date=row["date"],
                duration_seconds=row["duration_secs"],
                total_reps=row["total_reps"],
                avg_rep_speed=row["avg_rep_speed"] or 0.0,
                form_score=row["form_score"] or 0.0,
                calories_burned=row["calories"] or 0.0,
                grade=row["grade"] or "—",
            )
            for row in rows
        ]

    def get_total_stats(self) -> dict:
        """Aggregate stats across all sessions."""
        with self._get_connection() as conn:
            row = conn.execute("""
                SELECT
                    COUNT(*) as sessions,
                    COALESCE(SUM(total_reps), 0) as total_reps,
                    COALESCE(SUM(calories), 0) as total_calories,
                    COALESCE(AVG(form_score), 0) as avg_form,
                    COALESCE(SUM(duration_secs), 0) as total_duration
                FROM workout_sessions
            """).fetchone()
        return dict(row)

    def delete_session(self, session_id: int):
        with self._get_connection() as conn:
            conn.execute("DELETE FROM workout_sessions WHERE id = ?", (session_id,))
            conn.commit()
