"""Database schema for storing commit history"""

import sqlite3
from pathlib import Path
from datetime import datetime


class CommitDatabase:
    """SQLite database for storing codeinspector commit history"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database and create tables if they don't exist"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        
        # Create commits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commit_hash TEXT NOT NULL,
                message TEXT NOT NULL,
                repository TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                files_changed INTEGER,
                lines_added INTEGER,
                lines_removed INTEGER,
                quality_passed BOOLEAN
            )
        """)
        
        # Create commit_files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS commit_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commit_id INTEGER,
                file_path TEXT NOT NULL,
                change_type TEXT,
                FOREIGN KEY (commit_id) REFERENCES commits(id)
            )
        """)
        
        # Create quality_checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quality_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                commit_id INTEGER,
                check_type TEXT,
                passed BOOLEAN,
                details TEXT,
                FOREIGN KEY (commit_id) REFERENCES commits(id)
            )
        """)
        
        self.conn.commit()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
