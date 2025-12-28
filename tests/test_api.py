"""
API Tests for JobTrack
"""

import pytest
import tempfile
import os
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import db


@pytest.fixture
def client():
    """Create a test client with a temporary database"""
    # Create a temporary file for the test database
    fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)  # Close the file descriptor, we just need the path
    
    # Configure database to use temp file
    original_db_path = db.db_path
    db.db_path = temp_db_path
    db._schema_initialized = False  # Reset so schema gets created
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Cleanup: restore original path and remove temp file
    db.db_path = original_db_path
    db._schema_initialized = False
    try:
        os.unlink(temp_db_path)
    except OSError:
        pass


def test_root(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "JobTrack API" in response.json()["message"]


def test_create_job(client):
    """Test creating a job"""
    job_data = {
        "company": "Tech Corp",
        "position": "Product Manager",
        "location": "Remote",
        "status": "wishlist"
    }
    
    response = client.post("/api/jobs", json=job_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["company"] == "Tech Corp"
    assert data["position"] == "Product Manager"
    assert "id" in data


def test_get_jobs(client):
    """Test getting all jobs"""
    # Create a job first
    client.post("/api/jobs", json={
        "company": "Test Company",
        "position": "Developer"
    })
    
    response = client.get("/api/jobs")
    assert response.status_code == 200
    
    jobs = response.json()
    assert len(jobs) > 0


def test_get_job_by_id(client):
    """Test getting a specific job"""
    # Create a job
    create_response = client.post("/api/jobs", json={
        "company": "Example Corp",
        "position": "Engineer"
    })
    job_id = create_response.json()["id"]
    
    # Get the job
    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    assert response.json()["company"] == "Example Corp"


def test_update_job(client):
    """Test updating a job"""
    # Create a job
    create_response = client.post("/api/jobs", json={
        "company": "Old Company",
        "position": "Role"
    })
    job_id = create_response.json()["id"]
    
    # Update the job
    response = client.put(f"/api/jobs/{job_id}", json={
        "status": "applied"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "applied"


def test_delete_job(client):
    """Test deleting a job"""
    # Create a job
    create_response = client.post("/api/jobs", json={
        "company": "Delete Me",
        "position": "Test"
    })
    job_id = create_response.json()["id"]
    
    # Delete the job
    response = client.delete(f"/api/jobs/{job_id}")
    assert response.status_code == 204
    
    # Verify it's gone
    get_response = client.get(f"/api/jobs/{job_id}")
    assert get_response.status_code == 404


def test_get_stats(client):
    """Test analytics endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    
    data = response.json()
    assert "total_jobs" in data
    assert "by_status" in data
    