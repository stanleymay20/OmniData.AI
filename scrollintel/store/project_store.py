"""
ScrollIntel v2: The Flame Interpreter
Project store for session management and history
"""

from typing import Dict, Any, List, Optional
import sqlite3
import json
from datetime import datetime
import pytz
import os
from pathlib import Path

class ProjectStore:
    """Project store for managing interpretation sessions and history."""
    
    def __init__(self, db_path: str = "scrollintel.db"):
        """Initialize the project store with SQLite database."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize the database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    input_data TEXT NOT NULL,
                    interpretation TEXT NOT NULL,
                    chart_path TEXT,
                    sacred_timing TEXT NOT NULL,
                    metadata TEXT
                )
            """)
    
    def store_session(
        self,
        domain: str,
        input_data: Dict[str, Any],
        interpretation: Dict[str, Any],
        chart_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """Store a new interpretation session."""
        try:
            timestamp = datetime.now(pytz.UTC).isoformat()
            sacred_timing = interpretation.get("sacred_timing", {})
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO sessions (
                        timestamp, domain, input_data, interpretation,
                        chart_path, sacred_timing, metadata
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        timestamp,
                        domain,
                        json.dumps(input_data),
                        json.dumps(interpretation),
                        chart_path,
                        json.dumps(sacred_timing),
                        json.dumps(metadata or {})
                    )
                )
                return cursor.lastrowid
        except Exception as e:
            raise ValueError(f"Failed to store session: {str(e)}")
    
    def get_session(self, session_id: int) -> Dict[str, Any]:
        """Retrieve a specific interpretation session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    "SELECT * FROM sessions WHERE id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    raise ValueError(f"Session {session_id} not found")
                
                return {
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "domain": row["domain"],
                    "input_data": json.loads(row["input_data"]),
                    "interpretation": json.loads(row["interpretation"]),
                    "chart_path": row["chart_path"],
                    "sacred_timing": json.loads(row["sacred_timing"]),
                    "metadata": json.loads(row["metadata"])
                }
        except Exception as e:
            raise ValueError(f"Failed to retrieve session: {str(e)}")
    
    def list_sessions(
        self,
        domain: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List interpretation sessions with optional filters."""
        try:
            query = "SELECT * FROM sessions WHERE 1=1"
            params = []
            
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            
            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                return [{
                    "id": row["id"],
                    "timestamp": row["timestamp"],
                    "domain": row["domain"],
                    "input_data": json.loads(row["input_data"]),
                    "interpretation": json.loads(row["interpretation"]),
                    "chart_path": row["chart_path"],
                    "sacred_timing": json.loads(row["sacred_timing"]),
                    "metadata": json.loads(row["metadata"])
                } for row in rows]
        except Exception as e:
            raise ValueError(f"Failed to list sessions: {str(e)}")
    
    def delete_session(self, session_id: int) -> bool:
        """Delete a specific interpretation session."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM sessions WHERE id = ?",
                    (session_id,)
                )
                return cursor.rowcount > 0
        except Exception as e:
            raise ValueError(f"Failed to delete session: {str(e)}")
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about stored sessions."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT
                        COUNT(*) as total_sessions,
                        COUNT(DISTINCT domain) as unique_domains,
                        MIN(timestamp) as first_session,
                        MAX(timestamp) as last_session
                    FROM sessions
                """)
                row = cursor.fetchone()
                
                return {
                    "total_sessions": row[0],
                    "unique_domains": row[1],
                    "first_session": row[2],
                    "last_session": row[3]
                }
        except Exception as e:
            raise ValueError(f"Failed to get session stats: {str(e)}") 