"""
Pydantic models for request/response validation
"""

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field


class JobBase(BaseModel):
    """Base job model with common fields"""
    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    location: Optional[str] = None
    job_url: Optional[str] = None
    salary_min: Optional[int] = Field(None, ge=0)
    salary_max: Optional[int] = Field(None, ge=0)
    status: str = Field(default="wishlist")
    notes: Optional[str] = None
    job_description: Optional[str] = None  # Added missing field


class JobCreate(JobBase):
    """Model for creating a new job"""
    pass


class JobUpdate(BaseModel):
    """Model for updating a job (all fields optional)"""
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    job_url: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    status: Optional[str] = None
    date_applied: Optional[date] = None
    notes: Optional[str] = None
    job_description: Optional[str] = None  # Added missing field


class Job(JobBase):
    """Complete job model with all fields"""
    id: int
    date_added: date
    date_applied: Optional[date] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    """Base contact model"""
    job_id: int
    name: str
    role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


class ContactCreate(ContactBase):
    """Model for creating a contact"""
    pass


class Contact(ContactBase):
    """Complete contact model"""
    id: int
    
    class Config:
        from_attributes = True


class InterviewBase(BaseModel):
    """Base interview model"""
    job_id: int
    interview_date: datetime
    interview_type: Optional[str] = None
    notes: Optional[str] = None


class InterviewCreate(InterviewBase):
    """Model for creating an interview"""
    pass


class Interview(InterviewBase):
    """Complete interview model"""
    id: int
    
    class Config:
        from_attributes = True


class ResumeBase(BaseModel):
    """Base resume model"""
    filename: str
    file_path: str
    content: Optional[str] = None
    file_type: Optional[str] = None
    notes: Optional[str] = None


class ResumeCreate(BaseModel):
    """Model for creating a resume (manual entry)"""
    filename: str
    file_path: str
    content: Optional[str] = None
    file_type: Optional[str] = None
    notes: Optional[str] = None


class ResumeUpdate(BaseModel):
    """Model for updating resume info"""
    ats_score: Optional[int] = Field(None, ge=0, le=100)
    ats_analysis: Optional[str] = None
    notes: Optional[str] = None


class Resume(ResumeBase):
    """Complete resume model"""
    id: int
    upload_date: datetime
    ats_score: Optional[int] = None
    ats_analysis: Optional[str] = None
    
    class Config:
        from_attributes = True


# ATS Analysis Models
class ATSAnalysisRequest(BaseModel):
    """Request for ATS analysis"""
    resume_text: str
    job_description: str
    resume_id: Optional[int] = None


class ATSAnalysisResponse(BaseModel):
    """Response from ATS analysis"""
    success: bool
    score: int
    missing_keywords: List[str]
    suggestions: List[str]
    summary: str


class CoverLetterRequest(BaseModel):
    """Request for cover letter generation"""
    resume_text: str
    job_description: str
    company_name: str
    tone: str = "professional"


class CoverLetterResponse(BaseModel):
    """Response with generated cover letter"""
    success: bool
    cover_letter: str


# ==================== JOB EXTRACTION MODELS ====================

class JobExtractRequest(BaseModel):
    """Request model for extracting job details from description"""
    job_description: str


class JobExtractFromURLRequest(BaseModel):
    """Request model for extracting job details from URL"""
    url: str


class JobExtractResponse(BaseModel):
    """Response model for extracted job details"""
    company: Optional[str] = None
    position: Optional[str] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    job_description: Optional[str] = None