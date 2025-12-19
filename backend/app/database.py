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
        self.connection: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        return self.connection
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
    
    def initialize_schema(self):
        """Create database tables if they don't exist"""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Jobs table
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
        self.close()
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
