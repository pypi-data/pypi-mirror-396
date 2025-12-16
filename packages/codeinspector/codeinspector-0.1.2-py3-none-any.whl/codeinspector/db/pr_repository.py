"""Repository pattern for PR review database operations"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from .schema import CommitDatabase


class PRReviewRepository:
    """Repository for PR review database operations"""
    
    def __init__(self, db_path: str):
        self.db = CommitDatabase(db_path)
        self._init_pr_tables()
    
    def _init_pr_tables(self):
        """Initialize PR review tables"""
        cursor = self.db.conn.cursor()
        
        # Create pr_reviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pr_reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pr_number INTEGER NOT NULL,
                repository TEXT NOT NULL,
                status TEXT,
                issues_found INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                review_url TEXT
            )
        """)
        
        # Create pr_comments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pr_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pr_review_id INTEGER,
                file_path TEXT,
                line_number INTEGER,
                comment_text TEXT,
                issue_type TEXT,
                FOREIGN KEY (pr_review_id) REFERENCES pr_reviews(id)
            )
        """)
        
        self.db.conn.commit()
    
    def save_pr_review(self, review_data: Dict) -> int:
        """
        Save a PR review to database
        
        Args:
            review_data: Dict with keys: pr_number, repository, status,
                        issues_found, review_url, comments (list of dicts)
        
        Returns:
            review_id: ID of the inserted review
        """
        cursor = self.db.conn.cursor()
        
        # Insert PR review
        cursor.execute("""
            INSERT INTO pr_reviews
            (pr_number, repository, status, issues_found, review_url, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            review_data.get('pr_number'),
            review_data.get('repository'),
            review_data.get('status'),
            review_data.get('issues_found', 0),
            review_data.get('review_url'),
            datetime.now().isoformat()
        ))
        
        review_id = cursor.lastrowid
        
        # Insert comments
        for comment in review_data.get('comments', []):
            cursor.execute("""
                INSERT INTO pr_comments
                (pr_review_id, file_path, line_number, comment_text, issue_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                review_id,
                comment['file'],
                comment['line'],
                comment['message'],
                comment['code']
            ))
        
        self.db.conn.commit()
        return review_id
    
    def get_pr_review_history(self, limit: int = 50, repository: Optional[str] = None) -> List[Dict]:
        """Get PR review history, optionally filtered by repository"""
        cursor = self.db.conn.cursor()
        
        if repository:
            cursor.execute("""
                SELECT * FROM pr_reviews
                WHERE repository = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (repository, limit))
        else:
            cursor.execute("""
                SELECT * FROM pr_reviews
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
        
        reviews = []
        for row in cursor.fetchall():
            review = dict(row)
            review_id = review['id']
            
            # Get comments for this review
            cursor.execute("""
                SELECT file_path, line_number, comment_text, issue_type
                FROM pr_comments
                WHERE pr_review_id = ?
            """, (review_id,))
            review['comments'] = [dict(row) for row in cursor.fetchall()]
            
            reviews.append(review)
        
        return reviews
    
    def close(self):
        """Close database connection"""
        self.db.close()
