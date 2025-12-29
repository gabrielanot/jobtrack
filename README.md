# 🎯 JobTrack

**Your AI-powered job application tracker**

Track job applications, analyze your resume against job descriptions, and generate tailored cover letters - all in one place.

![JobTrack Dashboard](docs/screenshot-dashboard.png)

---

## ✨ Features

- **📋 Job Tracking** - Keep all your applications organized in one place
- **📄 Resume Upload** - Upload PDF or Word documents, we extract the text automatically
- **🔍 ATS Analysis** - See how well your resume matches a job description (0-100 score)
- **✉️ Cover Letter Generator** - Create personalized cover letters with AI
- **🌙 Beautiful Dark Theme** - Easy on the eyes during those late-night job searches

---

## 🚀 Quick Start

### Option 1: Use the Hosted Version (Easiest)

> Coming soon! We're setting up a hosted version so you can use JobTrack without installing anything.

### Option 2: Run on Your Computer

#### What You'll Need

1. **Python** (version 3.9 or newer)
   - Download from: https://www.python.org/downloads/
   - ⚠️ During installation, check ✅ **"Add Python to PATH"**

2. **Anthropic API Key** (for AI features)
   - Sign up at: https://console.anthropic.com/
   - Create an API key (they offer free credits to start)

#### Step-by-Step Setup

**Windows:**
1. Download this project (green "Code" button → "Download ZIP")
2. Extract the ZIP file to a folder
3. Double-click `start.bat`
4. Enter your API key when asked (first time only)
5. Open http://localhost:8000 in your browser

**Mac/Linux:**
1. Download this project
2. Open Terminal in the project folder
3. Run: `chmod +x start.sh && ./start.sh`
4. Enter your API key when asked (first time only)
5. Open http://localhost:8000 in your browser

---

## 📖 How to Use

### Adding Jobs

1. Click **"Jobs"** in the sidebar
2. Click **"Add Job"** button
3. Fill in the company, position, and other details
4. Click **"Save"**

### Uploading Your Resume

1. Click **"Resumes"** in the sidebar
2. Drag and drop your resume file (PDF, DOCX, or TXT)
3. Wait for it to upload and extract the text
4. Your resume is now saved and ready to use!

### Analyzing Your Resume (ATS Score)

1. Click **"ATS Analyzer"** in the sidebar
2. Paste your resume text (or click "Use for ATS" on a saved resume)
3. Paste the job description
4. Click **"Analyze Match"**
5. See your score, missing keywords, and suggestions!

### Generating a Cover Letter

1. Click **"Cover Letter"** in the sidebar
2. Enter the company name
3. Paste your resume and the job description
4. Choose a tone (Professional, Enthusiastic, or Conversational)
5. Click **"Generate Cover Letter"**
6. Copy and customize as needed!

---

## ❓ FAQ

### Is my data private?
Yes! Everything runs on your computer. Your resumes and job data are stored locally and never sent anywhere except to the AI for analysis (when you click analyze/generate).

### Do I need to pay for the AI?
Anthropic offers free credits when you sign up. For typical job searching, this should last a while. After that, it's pay-as-you-go (usually a few cents per analysis).

### The ATS score seems low - is that bad?
Not necessarily! The score shows keyword match percentage. Even 60-70% can be good. Focus on the "missing keywords" and suggestions to improve.

### Can I use this offline?
Job tracking and resume storage work offline. AI features (ATS analysis, cover letter generation) require internet.

### Something's not working!
1. Make sure Python is installed: Open terminal/command prompt and type `python --version`
2. Check your API key is correct in the `.env` file
3. Try deleting `jobtrack.db` and restarting (this resets your data)
4. [Report a bug](https://github.com/gabrielajoy/jobtrack/issues)

---

## 🛠️ For Developers

<details>
<summary>Click to expand developer setup</summary>

### Manual Setup

```bash
# Clone the repository
git clone https://github.com/gabrielajoy/jobtrack.git
cd jobtrack

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run the server
uvicorn backend.app.main:app --reload
```

### Project Structure

```
jobtrack/
├── backend/
│   └── app/
│       ├── main.py          # FastAPI endpoints
│       ├── database.py      # SQLite setup
│       ├── models.py        # Pydantic models
│       ├── ats_service.py   # AI analysis
│       └── file_service.py  # PDF/DOCX parsing
├── frontend/
│   └── index.html           # Single-page app
├── tests/                   # Pytest tests
├── start.bat               # Windows launcher
├── start.sh                # Mac/Linux launcher
└── requirements.txt
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/jobs` | List all jobs |
| POST | `/api/jobs` | Create a job |
| PUT | `/api/jobs/{id}` | Update a job |
| DELETE | `/api/jobs/{id}` | Delete a job |
| POST | `/api/resumes/upload` | Upload resume file |
| GET | `/api/resumes/{id}/content` | Get resume text |
| POST | `/api/analyze-ats` | Analyze resume vs job |
| POST | `/api/generate-cover-letter` | Generate cover letter |

### Running Tests

```bash
pytest tests/ -v
```

</details>

---

## 📝 Feedback

This is an **alpha version**! We'd love your feedback:

- 🐛 [Report bugs](https://github.com/gabrielajoy/jobtrack/issues)
- 💡 [Suggest features](https://github.com/gabrielajoy/jobtrack/issues)
- ⭐ Star the repo if you find it useful!

---

## 📄 License

MIT License - feel free to use, modify, and share!

---

Made with ❤️ to help job seekers land their dream jobs.