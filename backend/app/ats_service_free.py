"""
Free ATS Analysis Service
Provides AI features without requiring paid APIs

Supports:
- Ollama (local LLM) - free, good quality
- Keyword matching - free, no setup required
"""

import json
import re
import urllib.request
import urllib.error
from collections import Counter
from typing import Tuple

from .config import AI_MODE, OLLAMA_MODEL, OLLAMA_URL


# ==================== OLLAMA FUNCTIONS ====================

def _call_ollama(prompt: str, max_tokens: int = 1024) -> Tuple[bool, str]:
    """
    Call Ollama API locally.
    Returns (success, response_text)
    """
    try:
        data = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens
            }
        }).encode('utf-8')
        
        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"}
        )
        
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode('utf-8'))
            return True, result.get("response", "")
            
    except urllib.error.URLError as e:
        return False, f"Ollama not running. Start it with: ollama serve"
    except Exception as e:
        return False, str(e)


def _is_ollama_available() -> bool:
    """Check if Ollama is running"""
    try:
        req = urllib.request.Request(f"{OLLAMA_URL}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status == 200
    except:
        return False


# ==================== KEYWORD MATCHING FUNCTIONS ====================

def _extract_keywords(text: str) -> set:
    """Extract meaningful keywords from text"""
    # Common words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'we', 'you', 'your', 'our', 'their', 'this', 'that', 'these', 'those',
        'it', 'its', 'they', 'them', 'he', 'she', 'his', 'her', 'who', 'what',
        'which', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
        'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only',
        'own', 'same', 'so', 'than', 'too', 'very', 'just', 'also', 'now',
        'about', 'after', 'before', 'between', 'into', 'through', 'during',
        'above', 'below', 'up', 'down', 'out', 'off', 'over', 'under', 'again',
        'further', 'then', 'once', 'here', 'there', 'any', 'etc', 'including',
        'work', 'working', 'job', 'position', 'role', 'team', 'company',
        'experience', 'ability', 'strong', 'excellent', 'good', 'great',
        'looking', 'seeking', 'required', 'requirements', 'qualifications',
        'responsibilities', 'duties', 'skills', 'years', 'year', 'plus'
    }
    
    # Extract words (3+ chars, alphanumeric)
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.-]{2,}\b', text.lower())
    
    # Filter stop words and return unique
    return {w for w in words if w not in stop_words}


def _keyword_match_analysis(resume_text: str, job_description: str) -> dict:
    """Analyze resume against job using keyword matching"""
    
    resume_keywords = _extract_keywords(resume_text)
    job_keywords = _extract_keywords(job_description)
    
    # Find matches and missing
    matched = resume_keywords & job_keywords
    missing = job_keywords - resume_keywords
    
    # Calculate score (percentage of job keywords found in resume)
    if len(job_keywords) == 0:
        score = 0
    else:
        score = int((len(matched) / len(job_keywords)) * 100)
    
    # Cap at 100
    score = min(score, 100)
    
    # Sort missing by likely importance (longer words often more specific)
    missing_sorted = sorted(missing, key=lambda x: (-len(x), x))[:15]
    
    # Generate basic suggestions
    suggestions = []
    if score < 50:
        suggestions.append("Your resume is missing many keywords from the job description. Consider tailoring it more specifically.")
    if score < 70:
        suggestions.append(f"Try to incorporate these terms naturally: {', '.join(missing_sorted[:5])}")
    if len(missing_sorted) > 5:
        suggestions.append("Focus on adding technical skills and tools mentioned in the job posting.")
    if score >= 70:
        suggestions.append("Good keyword match! Focus on quantifying your achievements.")
    
    # Summary
    summary = f"Your resume matches {score}% of keywords from the job description. "
    if score >= 80:
        summary += "Strong match - your background aligns well with this role."
    elif score >= 60:
        summary += "Decent match - some tailoring could improve your chances."
    else:
        summary += "Consider customizing your resume more for this specific position."
    
    return {
        "score": score,
        "missing_keywords": missing_sorted,
        "suggestions": suggestions,
        "summary": summary
    }


# ==================== MAIN SERVICE FUNCTIONS ====================

def analyze_resume_ats(resume_text: str, job_description: str) -> dict:
    """
    Analyze a resume against a job description.
    Uses Ollama if available, falls back to keyword matching.
    """
    
    # Try Ollama first if configured
    if AI_MODE == "ollama" and _is_ollama_available():
        prompt = f"""You are an expert ATS (Applicant Tracking System) analyzer.

Analyze this resume against the job description and provide:
1. An ATS compatibility score from 0-100
2. Keywords from the job description that are MISSING from the resume
3. Specific suggestions to improve the resume
4. A brief summary

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{job_description[:2000]}

Respond in this exact JSON format only (no other text):
{{"score": <number>, "missing_keywords": ["keyword1", "keyword2"], "suggestions": ["suggestion1", "suggestion2"], "summary": "Brief summary"}}
"""
        
        success, response = _call_ollama(prompt)
        if success:
            try:
                # Try to extract JSON from response
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    # Validate required fields
                    if all(k in result for k in ['score', 'missing_keywords', 'suggestions', 'summary']):
                        return result
            except json.JSONDecodeError:
                pass
    
    # Fall back to keyword matching
    return _keyword_match_analysis(resume_text, job_description)


def generate_cover_letter(
    resume_text: str, 
    job_description: str, 
    company_name: str,
    tone: str = "professional"
) -> str:
    """
    Generate a cover letter.
    Uses Ollama if available, otherwise returns a template.
    """
    
    # Try Ollama first
    if AI_MODE == "ollama" and _is_ollama_available():
        prompt = f"""Write a {tone} cover letter for someone applying to {company_name}.

THEIR RESUME:
{resume_text[:3000]}

JOB DESCRIPTION:
{job_description[:2000]}

Write a compelling 3-4 paragraph cover letter. Do NOT use placeholders like [Your Name].
Start directly with the letter content:"""

        success, response = _call_ollama(prompt, max_tokens=1500)
        if success and len(response) > 100:
            return response.strip()
    
    # Fallback: Return a template with instructions
    return f"""[COVER LETTER TEMPLATE - AI generation requires Ollama or Claude API]

Dear Hiring Manager at {company_name},

I am writing to express my strong interest in this position. Based on my background and experience, I believe I would be a valuable addition to your team.

[Paragraph 2: Highlight 2-3 specific experiences from your resume that match the job requirements]

[Paragraph 3: Explain why you're interested in this company specifically and what you can contribute]

[Paragraph 4: Thank them and express enthusiasm for the opportunity to discuss further]

Sincerely,
[Your Name]

---
💡 TIP: To generate personalized cover letters automatically:
   - Install Ollama (free): https://ollama.ai
   - Run: ollama pull llama3.2
   - Restart JobTrack
   
Or add your Anthropic API key for Claude-powered generation.
"""


def extract_job_details(job_description: str) -> dict:
    """
    Extract structured job details from a job description.
    Uses Ollama if available, otherwise uses regex patterns.
    """
    
    # Try Ollama first
    if AI_MODE == "ollama" and _is_ollama_available():
        prompt = f"""Extract job details from this posting.

JOB POSTING:
{job_description[:3000]}

Respond in this exact JSON format only:
{{"company": "name or null", "position": "title or null", "location": "location or null", "salary_min": null, "salary_max": null}}
"""
        
        success, response = _call_ollama(prompt, max_tokens=500)
        if success:
            try:
                json_match = re.search(r'\{[\s\S]*\}', response)
                if json_match:
                    result = json.loads(json_match.group())
                    # Clean up null strings
                    for key in result:
                        if result[key] in ["null", "None", ""]:
                            result[key] = None
                    return result
            except json.JSONDecodeError:
                pass
    
    # Fallback: Use regex patterns
    result = {
        "company": None,
        "position": None,
        "location": None,
        "salary_min": None,
        "salary_max": None
    }
    
    # Try to extract salary
    salary_pattern = r'\$\s*([\d,]+)\s*(?:k|K|,000)?(?:\s*[-–to]+\s*\$?\s*([\d,]+)\s*(?:k|K|,000)?)?'
    salary_match = re.search(salary_pattern, job_description)
    if salary_match:
        try:
            min_sal = salary_match.group(1).replace(',', '')
            result["salary_min"] = int(min_sal) * (1000 if len(min_sal) < 4 else 1)
            if salary_match.group(2):
                max_sal = salary_match.group(2).replace(',', '')
                result["salary_max"] = int(max_sal) * (1000 if len(max_sal) < 4 else 1)
            else:
                result["salary_max"] = result["salary_min"]
        except ValueError:
            pass
    
    # Try to extract location (look for common patterns)
    location_patterns = [
        r'(?:Location|Based in|Office)[:\s]+([^,\n]+(?:,\s*[A-Z]{2})?)',
        r'(Remote|Hybrid|On-?site)',
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?,\s*[A-Z]{2})\b'
    ]
    for pattern in location_patterns:
        match = re.search(pattern, job_description, re.IGNORECASE)
        if match:
            result["location"] = match.group(1).strip()
            break
    
    return result


def fetch_and_extract_from_url(url: str) -> dict:
    """
    Fetch a job posting from URL and extract details.
    """
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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        req = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        parser = TextExtractor()
        parser.feed(html)
        page_text = parser.get_text()
        
        if len(page_text) > 8000:
            page_text = page_text[:8000]
        
        # Try Ollama if available
        if AI_MODE == "ollama" and _is_ollama_available():
            prompt = f"""Extract job details from this page content.

PAGE CONTENT:
{page_text[:4000]}

Respond in this exact JSON format only:
{{"company": "name or null", "position": "title or null", "location": "location or null", "salary_min": null, "salary_max": null, "job_description": "main description under 1500 chars"}}
"""
            
            success, response = _call_ollama(prompt, max_tokens=2000)
            if success:
                try:
                    json_match = re.search(r'\{[\s\S]*\}', response)
                    if json_match:
                        result = json.loads(json_match.group())
                        for key in result:
                            if result[key] in ["null", "None", ""]:
                                result[key] = None
                        return result
                except json.JSONDecodeError:
                    pass
        
        # Fallback: Return raw text with basic extraction
        details = extract_job_details(page_text)
        details["job_description"] = page_text[:2000]
        return details
            
    except urllib.error.HTTPError as e:
        return {"error": f"Could not access URL (HTTP {e.code}). Some sites block automated access."}
    except urllib.error.URLError as e:
        return {"error": f"Could not connect to URL: {str(e)}"}
    except Exception as e:
        return {"error": f"Failed to fetch URL: {str(e)}"}