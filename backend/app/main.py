"""
JobTrack FastAPI Application
Main entry point for the API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import sqlite3
from contextlib import contextmanager

from .database import db
from .models import Job, JobCreate, JobUpdate, Resume, ResumeCreate, ResumeUpdate


# Initialize FastAPI app
app = FastAPI(
    title="JobTrack API",
    description="API for tracking job applications",
    version="1.0.0"
)

# Configure CORS (allows frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(db.db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


@app.on_event("startup")
def startup():
    """Initialize database on app startup"""
    db.initialize_schema()


@app.get("/")
def root():
    """Health check endpoint"""
    return {
        "message": "JobTrack API is running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/jobs", response_model=List[Job])
def get_jobs(status: str = None):
    """
    Get all jobs, optionally filtered by status
    
    - **status**: Filter by job status (wishlist, applied, interviewing, offer, rejected)
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM jobs WHERE status = ? ORDER BY date_added DESC",
                (status,)
            )
        else:
            cursor.execute("SELECT * FROM jobs ORDER BY date_added DESC")
        
        jobs = cursor.fetchall()
        return [dict(job) for job in jobs]


@app.post("/api/jobs", response_model=Job, status_code=201)
def create_job(job: JobCreate):
    """
    Create a new job application
    
    - **company**: Company name (required)
    - **position**: Job position (required)
    - **location**: Job location
    - **job_url**: Link to job posting
    - **salary_min**: Minimum salary
    - **salary_max**: Maximum salary
    - **status**: Current status (default: wishlist)
    - **notes**: Additional notes
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (company, position, location, job_url, salary_min, 
                             salary_max, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.company, job.position, job.location, job.job_url,
            job.salary_min, job.salary_max, job.status, job.notes
        ))
        
        conn.commit()
        job_id = cursor.lastrowid
        
        # Fetch the created job
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        created_job = cursor.fetchone()
        
        return dict(created_job)


@app.get("/api/jobs/{job_id}", response_model=Job)
def get_job(job_id: int):
    """Get a specific job by ID"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return dict(job)


@app.put("/api/jobs/{job_id}", response_model=Job)
def update_job(job_id: int, job_update: JobUpdate):
    """Update a job application"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if job exists
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job not found")
        
        # Build UPDATE query dynamically for provided fields
        update_fields = []
        values = []
        
        for field, value in job_update.model_dump(exclude_unset=True).items():
            update_fields.append(f"{field} = ?")
            values.append(value)
        
        if update_fields:
            values.append(job_id)
            query = f"UPDATE jobs SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        # Return updated job
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        updated_job = cursor.fetchone()
        
        return dict(updated_job)


@app.delete("/api/jobs/{job_id}", status_code=204)
def delete_job(job_id: int):
    """Delete a job application"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Job not found")
        
        conn.commit()
        return None


@app.get("/api/stats")
def get_stats():
    """Get analytics and statistics"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total jobs by status
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM jobs
            GROUP BY status
        """)
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        # Total jobs
        cursor.execute("SELECT COUNT(*) as total FROM jobs")
        total = cursor.fetchone()['total']
        
        # Recent activity
        cursor.execute("""
            SELECT DATE(date_added) as date, COUNT(*) as count
            FROM jobs
            WHERE date_added >= date('now', '-30 days')
            GROUP BY DATE(date_added)
            ORDER BY date
        """)
        recent_activity = [dict(row) for row in cursor.fetchall()]
        
        return {
            "total_jobs": total,
            "by_status": status_counts,
            "recent_activity": recent_activity
        }
    
# ==================== RESUME ENDPOINTS ====================

@app.get("/api/resumes", response_model=List[Resume])
def get_resumes():
    """Get all uploaded resumes"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resumes ORDER BY upload_date DESC")
        resumes = cursor.fetchall()
        return [dict(resume) for resume in resumes]


@app.post("/api/resumes", response_model=Resume, status_code=201)
def create_resume(resume: ResumeCreate):
    """Register a new resume in the system"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resumes (filename, file_path, notes)
            VALUES (?, ?, ?)
        """, (resume.filename, resume.file_path, resume.notes))
        
        conn.commit()
        resume_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        created_resume = cursor.fetchone()
        
        return dict(created_resume)


@app.get("/api/resumes/{resume_id}", response_model=Resume)
def get_resume(resume_id: int):
    """Get a specific resume"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        resume = cursor.fetchone()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return dict(resume)


@app.put("/api/resumes/{resume_id}", response_model=Resume)
def update_resume(resume_id: int, resume_update: ResumeUpdate):
    """Update resume ATS analysis"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Check if resume exists
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Resume not found")
        
        # Build UPDATE query
        update_fields = []
        values = []
        
        for field, value in resume_update.model_dump(exclude_unset=True).items():
            update_fields.append(f"{field} = ?")
            values.append(value)
        
        if update_fields:
            values.append(resume_id)
            query = f"UPDATE resumes SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        # Return updated resume
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        updated_resume = cursor.fetchone()
        
        return dict(updated_resume)    