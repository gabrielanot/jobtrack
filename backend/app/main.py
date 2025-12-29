"""
JobTrack FastAPI Application
Main entry point for the API
"""

from contextlib import contextmanager, asynccontextmanager
import json
import os
import uuid
from typing import List

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from .database import db
from .models import (
    Job, JobCreate, JobUpdate,
    Resume, ResumeCreate, ResumeUpdate,
    ATSAnalysisRequest, ATSAnalysisResponse,
    CoverLetterRequest, CoverLetterResponse,
    JobExtractRequest, JobExtractFromURLRequest, JobExtractResponse
)
from .ats_service import (
    analyze_resume_ats,
    generate_cover_letter,
    extract_job_details,
    fetch_and_extract_from_url
)
from .file_service import parse_resume_file

# Directory to store uploaded resumes
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads", "resumes")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code here
    db.initialize_schema()
    yield
    # Shutdown code here

# Initialize FastAPI app
app = FastAPI(
    title="JobTrack API",
    description="API for tracking job applications with AI-powered features",
    version="1.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = db.connect()
    try:
        yield conn
    finally:
        conn.close()

@app.get("/api")
def root():
    """Health check endpoint"""
    return {
        "message": "JobTrack API is running",
        "version": "1.1.0",
        "docs": "/docs"
    }


# ==================== JOB ENDPOINTS ====================

@app.get("/api/jobs", response_model=List[Job])
def get_jobs(status: str = None):
    """Get all jobs, optionally filtered by status"""
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


@app.get("/api/jobs/with-descriptions")
def get_jobs_with_descriptions():
    """Get all jobs that have job descriptions saved"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, company, position, job_description 
            FROM jobs 
            WHERE job_description IS NOT NULL AND job_description != ''
            ORDER BY date_added DESC
        """)
        jobs = cursor.fetchall()
        return [dict(job) for job in jobs]


@app.post("/api/jobs", response_model=Job, status_code=201)
def create_job(job: JobCreate):
    """Create a new job application"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO jobs (company, position, location, job_url, salary_min, 
                             salary_max, status, notes, job_description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            job.company, job.position, job.location, job.job_url,
            job.salary_min, job.salary_max, job.status, job.notes, job.job_description
        ))
        
        conn.commit()
        job_id = cursor.lastrowid
        
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
        
        cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Job not found")
        
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
        
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM jobs
            GROUP BY status
        """)
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) as total FROM jobs")
        total = cursor.fetchone()['total']
        
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
        
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Resume not found")
        
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
        
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        updated_resume = cursor.fetchone()
        
        return dict(updated_resume)


@app.post("/api/resumes/upload", status_code=201)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a resume file (PDF, DOCX, or TXT).
    
    Extracts text content and stores both the file and extracted text.
    """
    # Validate file size (max 10MB)
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
    
    # Validate and parse file
    try:
        extracted_text, file_type = parse_resume_file(file.filename, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    if not extracted_text.strip():
        raise HTTPException(
            status_code=400, 
            detail="Could not extract text from file. The file may be empty or image-based."
        )
    
    # Generate unique filename
    file_ext = file.filename.rsplit('.', 1)[-1] if '.' in file.filename else file_type
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file to disk
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store in database
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO resumes (filename, file_path, content, file_type)
            VALUES (?, ?, ?, ?)
        """, (file.filename, file_path, extracted_text, file_type))
        
        conn.commit()
        resume_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM resumes WHERE id = ?", (resume_id,))
        created_resume = cursor.fetchone()
        
        return {
            "id": created_resume["id"],
            "filename": created_resume["filename"],
            "file_type": file_type,
            "content_preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text,
            "content_length": len(extracted_text),
            "upload_date": created_resume["upload_date"],
            "message": "Resume uploaded and parsed successfully"
        }


@app.get("/api/resumes/{resume_id}/content")
def get_resume_content(resume_id: int):
    """Get the extracted text content of a resume"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, filename, content FROM resumes WHERE id = ?", (resume_id,))
        resume = cursor.fetchone()
        
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")
        
        return {
            "id": resume["id"],
            "filename": resume["filename"],
            "content": resume["content"]
        }


# ==================== ATS ANALYSIS ENDPOINTS ====================

@app.post("/api/analyze-ats", response_model=ATSAnalysisResponse)
def analyze_ats(request: ATSAnalysisRequest):
    """Analyze resume against job description for ATS compatibility"""
    try:
        result = analyze_resume_ats(
            resume_text=request.resume_text,
            job_description=request.job_description
        )
        
        # Optionally update resume record if resume_id provided
        if request.resume_id:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                analysis_json = json.dumps(result)
                cursor.execute("""
                    UPDATE resumes 
                    SET ats_score = ?, ats_analysis = ?
                    WHERE id = ?
                """, (result['score'], analysis_json, request.resume_id))
                conn.commit()
        
        return {"success": True, **result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ATS analysis failed: {str(e)}")


@app.post("/api/generate-cover-letter", response_model=CoverLetterResponse)
def create_cover_letter(request: CoverLetterRequest):
    """Generate a personalized cover letter using AI"""
    try:
        cover_letter = generate_cover_letter(
            resume_text=request.resume_text,
            job_description=request.job_description,
            company_name=request.company_name,
            tone=request.tone
        )
        
        return {"success": True, "cover_letter": cover_letter}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cover letter generation failed: {str(e)}")


# ==================== JOB EXTRACTION ENDPOINTS ====================

@app.post("/api/ats/extract-job", response_model=JobExtractResponse)
def extract_job(request: JobExtractRequest):
    """Extract job details from a job description using AI"""
    result = extract_job_details(request.job_description)
    return result


@app.post("/api/ats/extract-from-url")
def extract_from_url(request: JobExtractFromURLRequest):
    """Fetch a job posting from URL and extract details"""
    result = fetch_and_extract_from_url(request.url)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return result


# ==================== FRONTEND SERVING ====================

from fastapi.responses import FileResponse

# Serve frontend at root
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")

@app.get("/", response_class=FileResponse)
def serve_frontend():
    """Serve the frontend application"""
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
