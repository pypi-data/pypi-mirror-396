"""Repository pattern for database operations"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from .schema import CommitDatabase


class CommitRepository:
    """Repository for commit database operations"""
    
    def __init__(self, db_path: str):
        self.db = CommitDatabase(db_path)
    
    def save_commit(self, commit_data: Dict) -> int:
        """
        Save a commit to the database
        
        Args:
            commit_data: Dict with keys: commit_hash, message, repository, 
                        files_changed, lines_added, lines_removed, quality_passed,
                        files (list of dicts), quality_checks (list of dicts)
        
        Returns:
            commit_id: ID of the inserted commit
        """
        cursor = self.db.conn.cursor()
        
        # Insert commit
        cursor.execute("""
            INSERT INTO commits 
            (commit_hash, message, repository, files_changed, lines_added, 
             lines_removed, quality_passed, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            commit_data.get('commit_hash'),
            commit_data.get('message'),
            commit_data.get('repository'),
            commit_data.get('files_changed', 0),
            commit_data.get('lines_added', 0),
            commit_data.get('lines_removed', 0),
            commit_data.get('quality_passed', True),
            datetime.now().isoformat()
        ))
        
        commit_id = cursor.lastrowid
        
        # Insert files
        for file_info in commit_data.get('files', []):
            cursor.execute("""
                INSERT INTO commit_files (commit_id, file_path, change_type)
                VALUES (?, ?, ?)
            """, (commit_id, file_info['path'], file_info['type']))
        
        # Insert quality checks
        for check in commit_data.get('quality_checks', []):
            cursor.execute("""
                INSERT INTO quality_checks (commit_id, check_type, passed, details)
                VALUES (?, ?, ?, ?)
            """, (commit_id, check['type'], check['passed'], check.get('details', '')))
        
        self.db.conn.commit()
        return commit_id
    
    def get_commit_history(self, limit: int = 50, repository: Optional[str] = None) -> List[Dict]:
        """Get commit history, optionally filtered by repository"""
        cursor = self.db.conn.cursor()
        
        if repository:
            cursor.execute("""
                SELECT * FROM commits 
                WHERE repository = ?
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (repository, limit))
        else:
            cursor.execute("""
                SELECT * FROM commits 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
        
        commits = []
        for row in cursor.fetchall():
            commit = dict(row)
            commit_id = commit['id']
            
            # Get files for this commit
            cursor.execute("""
                SELECT file_path, change_type 
                FROM commit_files 
                WHERE commit_id = ?
            """, (commit_id,))
            commit['files'] = [dict(row) for row in cursor.fetchall()]
            
            commits.append(commit)
        
        return commits
    
    def get_commit_by_hash(self, commit_hash: str) -> Optional[Dict]:
        """Get a specific commit by its hash"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT * FROM commits WHERE commit_hash = ?
        """, (commit_hash,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        commit = dict(row)
        commit_id = commit['id']
        
        # Get files
        cursor.execute("""
            SELECT file_path, change_type FROM commit_files WHERE commit_id = ?
        """, (commit_id,))
        commit['files'] = [dict(row) for row in cursor.fetchall()]
        
        # Get quality checks
        cursor.execute("""
            SELECT check_type, passed, details FROM quality_checks WHERE commit_id = ?
        """, (commit_id,))
        commit['quality_checks'] = [dict(row) for row in cursor.fetchall()]
        
        return commit
    
    def search_commits(self, query: str) -> List[Dict]:
        """Search commits by message content"""
        cursor = self.db.conn.cursor()
        cursor.execute("""
            SELECT * FROM commits 
            WHERE message LIKE ?
            ORDER BY timestamp DESC 
            LIMIT 50
        """, (f'%{query}%',))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection"""
        self.db.close()
