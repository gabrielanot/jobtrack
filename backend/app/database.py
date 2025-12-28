"""
Database initialization and connection management
"""

import sqlite3
from pathlib import Path
from typing import Optional


class Database:
    """Handle SQLite database operations"""
    
    def __init__(self, db_path: str = "jobtrack.db"):
        self.db_path = db_path
        self._schema_initialized = False
    
    def connect(self):
        """Establish database connection"""
        # check_same_thread=False allows connection to be used across threads
        # This is safe for our use case since we commit after each operation
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def close(self):
        """Close database connection (no-op now since we don't cache)"""
        pass
    
    def initialize_schema(self):
        """Create database tables if they don't exist"""
        # Avoid re-initializing if already done (except for memory DBs)
        if self._schema_initialized and self.db_path != ":memory:":
            return
            
        conn = self.connect()
        cursor = conn.cursor()
        
        # Jobs table (with job_description column)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                position TEXT NOT NULL,
                location TEXT,
                job_url TEXT,
                salary_min INTEGER,
                salary_max INTEGER,
                status TEXT DEFAULT 'wishlist',
                date_added DATE DEFAULT CURRENT_DATE,
                date_applied DATE,
                notes TEXT,
                job_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Contacts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                name TEXT,
                role TEXT,
                email TEXT,
                phone TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            )
        """)
        
        # Interviews table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                interview_date DATETIME,
                interview_type TEXT,
                notes TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
            )
        """)

        # Resumes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                file_path TEXT NOT NULL,
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ats_score INTEGER,
                ats_analysis TEXT,
                notes TEXT
            )
        """)
        
        conn.commit()
        conn.close()
        self._schema_initialized = True
        print("Database schema initialized")


# Global database instance
db = Database()


def get_db():
    """Dependency for FastAPI endpoints"""
    connection = db.connect()
    try:
        yield connection
    finally:
        connection.close()
        