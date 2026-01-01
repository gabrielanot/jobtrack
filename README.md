# 💼 JobTrack

**Your AI-powered job application tracker**

Track job applications, analyze your resume against job descriptions, and generate tailored cover letters - all in one place.

---

## ✨ Features

- **📋 Job Tracking** - Track applications through different stages with inline status editing
- **🔗 URL Import** - Paste a job URL to auto-extract company, position, location, and description
- **📄 Resume Management** - Upload PDF, DOCX, or TXT resumes with automatic text extraction
- **🎯 ATS Analyzer** - Check how well your resume matches a job description
- **✉️ Cover Letter Generator** - Generate personalized cover letters with AI
- **📊 Dashboard** - Track your progress with visual statistics

## 🚀 Quick Start

### Windows
```
Double-click start.bat
```
### Run on Your Computer

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
Not necessarily! The score shows keyword match percentage. Even 60-70% can be good, but the advise is to rech 85%. Focus on the "missing keywords" and suggestions to improve.

### Can I use this offline?
Job tracking and resume storage work offline. AI features (ATS analysis, cover letter generation) require internet.

### Something's not working!
1. Make sure Python is installed: Open terminal/command prompt and type `python --version`
2. Check your API key is correct in the `.env` file
3. Try deleting `jobtrack.db` and restarting (this resets your data)
4. [Report a bug](https://github.com/gabrielajoy/jobtrack/issues)

---

### Mac/Linux
```bash
chmod +x start.sh
./start.sh
```

Then open http://localhost:8000

## 💰 Free vs Paid Mode

JobTrack offers two modes to accommodate different needs:

### 🆓 Free Mode (Default)
No API costs! Uses:
- **ATS Analysis**: Smart keyword matching algorithm
- **Cover Letters**: Ollama (free, runs locally)
- **URL Import**: HTML parsing with regex

**Setup for Cover Letters (Optional):**
1. Install Ollama: https://ollama.ai
2. Run: `ollama pull llama3.2`
3. That's it!

### 💳 Claude Mode (Paid)
Higher quality AI features using Claude API:
- More nuanced ATS analysis
- Better cover letter generation  
- Smarter URL extraction

**Setup:**
1. Get API key: https://console.anthropic.com/
2. Edit `backend/app/config.py`:
   ```python
   AI_MODE = "claude"
   ```
3. Create `.env` file:
   ```
   ANTHROPIC_API_KEY=your-key-here
   ```

## 📁 Project Structure

```
jobtrack/
├── backend/
│   └── app/
│       ├── main.py           # API endpoints
│       ├── database.py       # SQLite database
│       ├── models.py         # Data models
│       ├── config.py         # AI mode config
│       ├── ats_service.py    # Claude AI service (paid)
│       ├── ats_service_free.py  # Free alternatives
│       └── file_service.py   # Resume parsing
├── frontend/
│   └── index.html           # Web interface
├── start.bat                # Windows launcher
├── start.sh                 # Mac/Linux launcher
└── requirements.txt
```

## 🛠️ Manual Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/gabrielanot/jobtrack.git
   cd jobtrack
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Mac/Linux
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python -m uvicorn backend.app.main:app --reload
   ```

5. **Open** http://localhost:8000

## 📝 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/jobs` | GET, POST | List/create jobs |
| `/api/jobs/{id}` | GET, PUT, DELETE | Get/update/delete job |
| `/api/resumes` | GET, POST | List/create resumes |
| `/api/resumes/upload` | POST | Upload resume file |
| `/api/resumes/{id}/content` | GET | Get resume text |
| `/api/analyze-ats` | POST | Analyze resume vs job |
| `/api/generate-cover-letter` | POST | Generate cover letter |
| `/api/ats/extract-from-url` | POST | Extract job from URL |
| `/api/info` | GET | Get API/AI mode info |

## 🤝 Contributing

This is an open-source learning project! Contributions welcome.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - feel free to use and modify!

## 🐛 Issues & Feedback

Found a bug or have a suggestion? [Open an issue](https://github.com/gabrielanot/jobtrack/issues)

---

Made with ❤️ for job seekers everywhere
