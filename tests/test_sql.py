"""
SQL and Database Tests for JobTrack
"""

import pytest
import tempfile
import os
from backend.app.database import Database


def test_database_schema():
    """Test that database schema initializes correctly"""
    # Create a temporary file for the test database
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    try:
        db = Database(temp_db_path)
        db.initialize_schema()
        conn = db.connect()
        cursor = conn.cursor()

        # Verify jobs table exists
        cursor.execute("SELECT COUNT(*) FROM jobs")
        count = cursor.fetchone()[0]
        assert count == 0  # Table exists but is empty
        
        conn.close()
    finally:
        # Cleanup
        try:
            os.unlink(temp_db_path)
        except OSError:
            pass


def test_tables_exist():
    """Test that all required tables are created"""
    # Create a temporary file for the test database
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    
    try:
        db = Database(temp_db_path)
        db.initialize_schema()
        conn = db.connect()
        cursor = conn.cursor()

        # Check all tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]

        assert "jobs" in tables
        assert "contacts" in tables
        assert "interviews" in tables
        assert "resumes" in tables
        
        conn.close()
    finally:
        # Cleanup
        try:
            os.unlink(temp_db_path)
        except OSError:
            pass