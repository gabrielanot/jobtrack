import pytest
from backend.app.database import Database


@pytest.fixture
def test_db():
    """Create an in-memory test database"""
    db = Database(":memory:")
    db.initialize_schema()
    conn = db.connect()
    yield conn
    db.close()


# Note: CI installs the package (pip install -e .), so no sys.path hacks are required.
