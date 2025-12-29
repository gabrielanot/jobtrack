"""
ATS Analysis Service
Uses Claude API to analyze resumes against job descriptions
"""

import json

from dotenv import load_dotenv
from anthropic import Anthropic

# Load environment variables
load_dotenv()

# Initialize the client
client = Anthropic()


def analyze_resume_ats(resume_text: str, job_description: str) -> dict:
    """
    Analyze a resume against a job description for ATS compatibility.
    
    Returns:
        dict with score, missing_keywords, suggestions, and summary
    """
    
    prompt = f"""You are an expert ATS (Applicant Tracking System) analyzer and career coach.

Analyze this resume against the job description and provide:
1. An ATS compatibility score from 0-100
2. Keywords from the job description that are MISSING from the resume
3. Specific suggestions to improve the resume for this role
4. A brief summary of the analysis

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

Respond in this exact JSON format (no markdown, just pure JSON):
{{
    "score": <number 0-100>,
    "missing_keywords": ["keyword1", "keyword2", ...],
    "suggestions": ["suggestion1", "suggestion2", ...],
    "summary": "Brief 2-3 sentence summary of the analysis"
}}
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    try:
        result = json.loads(response_text)
    except json.JSONDecodeError:
        result = {
            "score": 0,
            "missing_keywords": [],
            "suggestions": ["Could not analyze - please try again"],
            "summary": response_text
        }
    
    return result


def generate_cover_letter(
    resume_text: str, 
    job_description: str, 
    company_name: str,
    tone: str = "professional"
) -> str:
    """
    Generate a personalized cover letter.
    """
    
    prompt = f"""You are an expert career coach and professional writer.

Write a compelling cover letter for this candidate applying to {company_name}.

RESUME:
{resume_text}

JOB DESCRIPTION:
{job_description}

INSTRUCTIONS:
- Tone: {tone}
- Length: 3-4 paragraphs
- Highlight relevant experience from the resume
- Show enthusiasm for the specific role and company
- Include a strong opening and call to action
- Do NOT use placeholder text like [Your Name] - write it as a complete letter

Write the cover letter now:"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return message.content[0].text


def extract_job_details(job_description: str) -> dict:
    """
    Extract structured job details from a job description using AI.
    
    Returns:
        dict with company, position, location, salary_min, salary_max
    """
    
    prompt = f"""Extract job details from this job posting. 

JOB POSTING:
{job_description}

Extract and respond in this exact JSON format (no markdown, just pure JSON):
{{
    "company": "Company name or null if not found",
    "position": "Job title or null if not found",
    "location": "Location (city, state, remote, etc.) or null if not found",
    "salary_min": <minimum salary as integer or null if not found>,
    "salary_max": <maximum salary as integer or null if not found>
}}

Notes:
- For salary, extract numbers only (e.g., "$150,000" becomes 150000)
- If salary is a single number, use it for both min and max
- If location says "Remote" or "Hybrid", include that
- Be precise with the job title - use exactly what's posted
"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=500,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    response_text = message.content[0].text
    
    try:
        result = json.loads(response_text)
        # Clean up null strings
        for key in result:
            if result[key] == "null" or result[key] == "None":
                result[key] = None
    except json.JSONDecodeError:
        result = {
            "company": None,
            "position": None,
            "location": None,
            "salary_min": None,
            "salary_max": None
        }
    
    return result


def fetch_and_extract_from_url(url: str) -> dict:
    """
    Fetch a job posting from URL and extract details.
    
    Note: This won't work for LinkedIn (they block scraping).
    Works best with: Greenhouse, Lever, company career pages, Indeed.
    
    Returns:
        dict with company, position, location, salary_min, salary_max, job_description
    """
    import urllib.request
    import urllib.error
    from html.parser import HTMLParser
    
    class TextExtractor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.text = []
            self.skip_tags = {'script', 'style', 'meta', 'link', 'noscript'}
            self.current_tag = None
            
        def handle_starttag(self, tag, attrs):
            self.current_tag = tag
            
        def handle_endtag(self, tag):
            self.current_tag = None
            
        def handle_data(self, data):
            if self.current_tag not in self.skip_tags:
                text = data.strip()
                if text:
                    self.text.append(text)
        
        def get_text(self):
            return ' '.join(self.text)
    
    try:
        # Add headers to look like a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        # Extract text from HTML
        parser = TextExtractor()
        parser.feed(html)
        page_text = parser.get_text()
        
        # Limit text length for API
        if len(page_text) > 8000:
            page_text = page_text[:8000]
        
        # Use AI to extract details
        prompt = f"""Extract job details from this job posting page content.

PAGE CONTENT:
{page_text}

Extract and respond in this exact JSON format (no markdown, just pure JSON):
{{
    "company": "Company name or null if not found",
    "position": "Job title or null if not found",
    "location": "Location or null if not found",
    "salary_min": <minimum salary as integer or null>,
    "salary_max": <maximum salary as integer or null>,
    "job_description": "The main job description text (requirements, responsibilities, etc.) - keep it under 2000 characters"
}}
"""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        try:
            result = json.loads(response_text)
            for key in result:
                if result[key] == "null" or result[key] == "None":
                    result[key] = None
            return result
        except json.JSONDecodeError:
            return {
                "company": None,
                "position": None,
                "location": None,
                "salary_min": None,
                "salary_max": None,
                "job_description": page_text[:2000],
                "error": "Could not parse job details"
            }
            
    except urllib.error.HTTPError as e:
        return {
            "error": f"Could not access URL (HTTP {e.code}). LinkedIn and some sites block automated access."
        }
    except urllib.error.URLError as e:
        return {
            "error": f"Could not connect to URL: {str(e)}"
        }
    except Exception as e:
        return {
            "error": f"Failed to fetch URL: {str(e)}"
        }