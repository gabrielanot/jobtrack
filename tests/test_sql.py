import pytest
from backend.app.database import Database


def test_database_schema():
    """Test that database schema initializes correctly"""
    db = Database(":memory:")
    db.initialize_schema()
    conn = db.connect()
    cursor = conn.cursor()
    
    # Verify jobs table exists
    cursor.execute("SELECT COUNT(*) FROM jobs")
    total = cursor.fetchone()[0]
    assert total == 0  # Empty table after init
    
    db.close()


def test_tables_exist():
    """Test that all required tables are created"""
    db = Database(":memory:")
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
    
    db.close()