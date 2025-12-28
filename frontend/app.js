/* ========================================
   JobTrack Dashboard Application
   Version 1.1 - With URL extraction & job description reuse
   ======================================== */

// API Configuration
const API_BASE = 'http://localhost:8000';

// State
let allJobs = [];
let jobsWithDescriptions = [];
let currentJobDescription = '';

// ========================================
// Page Navigation
// ========================================

function showPage(pageName) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === pageName) {
            item.classList.add('active');
        }
    });
    
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(`page-${pageName}`).classList.add('active');
    
    if (pageName === 'dashboard') {
        loadDashboard();
    } else if (pageName === 'jobs') {
        loadJobs();
    } else if (pageName === 'ats') {
        loadJobsForATS();
    }
}

// ========================================
// Dashboard
// ========================================

async function loadDashboard() {
    try {
        const statsResponse = await fetch(`${API_BASE}/api/stats`);
        const stats = await statsResponse.json();
        
        document.getElementById('stat-total').textContent = stats.total_jobs || 0;
        document.getElementById('stat-wishlist').textContent = stats.by_status?.wishlist || 0;
        document.getElementById('stat-applied').textContent = stats.by_status?.applied || 0;
        document.getElementById('stat-interviewing').textContent = stats.by_status?.interviewing || 0;
        document.getElementById('stat-offer').textContent = stats.by_status?.offer || 0;
        
        updateStatusChart(stats.by_status || {});
        updateActivityChart(stats.recent_activity || []);
        
        const jobsResponse = await fetch(`${API_BASE}/api/jobs`);
        allJobs = await jobsResponse.json();
        displayRecentJobs(allJobs.slice(0, 5));
        
    } catch (error) {
        console.error('Failed to load dashboard:', error);
        showToast('Failed to load dashboard data', 'error');
    }
}

function displayRecentJobs(jobs) {
    const container = document.getElementById('recent-jobs');
    
    if (jobs.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>No applications yet. Add your first job!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = jobs.map(job => `
        <div class="job-card" onclick="openJobModal(${job.id})">
            <div class="job-info">
                <h4>${escapeHtml(job.company)}</h4>
                <p>${escapeHtml(job.position)}${job.location ? ` • ${escapeHtml(job.location)}` : ''}</p>
            </div>
            <div class="job-meta">
                ${job.salary_min ? `<span class="job-salary">$${formatNumber(job.salary_min)}${job.salary_max ? ` - $${formatNumber(job.salary_max)}` : ''}</span>` : ''}
                <span class="job-status status-${job.status}">${job.status}</span>
            </div>
        </div>
    `).join('');
}

// ========================================
// Charts
// ========================================

let statusChart = null;
let activityChart = null;

function updateStatusChart(byStatus) {
    const ctx = document.getElementById('statusChart').getContext('2d');
    
    const labels = ['Wishlist', 'Applied', 'Interviewing', 'Offer', 'Rejected'];
    const data = [
        byStatus.wishlist || 0,
        byStatus.applied || 0,
        byStatus.interviewing || 0,
        byStatus.offer || 0,
        byStatus.rejected || 0
    ];
    
    const colors = [
        'rgba(234, 179, 8, 0.8)',
        'rgba(59, 130, 246, 0.8)',
        'rgba(168, 85, 247, 0.8)',
        'rgba(16, 185, 129, 0.8)',
        'rgba(239, 68, 68, 0.8)'
    ];
    
    if (statusChart) {
        statusChart.destroy();
    }
    
    statusChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a1a1aa',
                        padding: 16,
                        font: { size: 12 }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

function updateActivityChart(activity) {
    const ctx = document.getElementById('activityChart').getContext('2d');
    
    const labels = [];
    const data = [];
    const activityMap = {};
    
    activity.forEach(item => {
        activityMap[item.date] = item.count;
    });
    
    for (let i = 29; i >= 0; i--) {
        const date = new Date();
        date.setDate(date.getDate() - i);
        const dateStr = date.toISOString().split('T')[0];
        labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        data.push(activityMap[dateStr] || 0);
    }
    
    if (activityChart) {
        activityChart.destroy();
    }
    
    activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Applications',
                data: data,
                borderColor: 'rgba(59, 130, 246, 1)',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: {
                    grid: { display: false },
                    ticks: { color: '#71717a', maxTicksLimit: 6 }
                },
                y: {
                    grid: { color: '#27272a' },
                    ticks: { color: '#71717a', stepSize: 1 },
                    beginAtZero: true
                }
            }
        }
    });
}

// ========================================
// Jobs List
// ========================================

async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE}/api/jobs`);
        allJobs = await response.json();
        displayJobsTable(allJobs);
    } catch (error) {
        console.error('Failed to load jobs:', error);
        showToast('Failed to load jobs', 'error');
    }
}

function displayJobsTable(jobs) {
    const tbody = document.getElementById('jobs-table-body');
    
    if (jobs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" style="text-align: center; padding: 40px; color: var(--text-muted);">
                    No applications found. Add your first job!
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = jobs.map(job => `
        <tr>
            <td><strong>${escapeHtml(job.company)}</strong></td>
            <td>${escapeHtml(job.position)}</td>
            <td>${escapeHtml(job.location || '-')}</td>
            <td>${job.salary_min ? `$${formatNumber(job.salary_min)}${job.salary_max ? ` - $${formatNumber(job.salary_max)}` : ''}` : '-'}</td>
            <td><span class="job-status status-${job.status}">${job.status}</span></td>
            <td>${formatDate(job.date_added)}</td>
            <td>
                <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 12px;" onclick="openJobModal(${job.id})">View</button>
            </td>
        </tr>
    `).join('');
}

function filterJobs() {
    const status = document.getElementById('filter-status').value;
    if (status) {
        displayJobsTable(allJobs.filter(job => job.status === status));
    } else {
        displayJobsTable(allJobs);
    }
}

// ========================================
// Add Job - URL Extraction
// ========================================

async function extractFromURL() {
    const url = document.getElementById('job-url-input').value.trim();
    
    if (!url) {
        showToast('Please enter a job posting URL', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/ats/extract-from-url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });
        
        if (response.ok) {
            const extracted = await response.json();
            
            if (extracted.job_description) {
                document.getElementById('job-description-input').value = extracted.job_description;
                currentJobDescription = extracted.job_description;
            }
            
            document.getElementById('company').value = extracted.company || '';
            document.getElementById('position').value = extracted.position || '';
            document.getElementById('location').value = extracted.location || '';
            document.getElementById('salary_min').value = extracted.salary_min || '';
            document.getElementById('salary_max').value = extracted.salary_max || '';
            document.getElementById('job_url').value = url;
            
            document.getElementById('step-paste').classList.add('hidden');
            document.getElementById('step-review').classList.remove('hidden');
            
            showToast('Job details extracted from URL!', 'success');
        } else {
            const error = await response.json();
            showToast(error.detail || 'Failed to extract from URL. Try pasting the description instead.', 'error');
        }
    } catch (error) {
        console.error('URL extraction failed:', error);
        showToast('Failed to fetch URL. Try pasting the job description instead.', 'error');
    } finally {
        showLoading(false);
    }
}

async function extractJobDetails() {
    const description = document.getElementById('job-description-input').value.trim();
    
    if (!description) {
        showToast('Please paste a job description first', 'error');
        return;
    }
    
    currentJobDescription = description;
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/ats/extract-job`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ job_description: description })
        });
        
        if (response.ok) {
            const extracted = await response.json();
            
            document.getElementById('company').value = extracted.company || '';
            document.getElementById('position').value = extracted.position || '';
            document.getElementById('location').value = extracted.location || '';
            document.getElementById('salary_min').value = extracted.salary_min || '';
            document.getElementById('salary_max').value = extracted.salary_max || '';
            
            showToast('Job details extracted successfully!', 'success');
        }
        
        document.getElementById('step-paste').classList.add('hidden');
        document.getElementById('step-review').classList.remove('hidden');
        
    } catch (error) {
        console.error('Extraction failed:', error);
        document.getElementById('step-paste').classList.add('hidden');
        document.getElementById('step-review').classList.remove('hidden');
        showToast('Please fill in the job details manually', 'error');
    } finally {
        showLoading(false);
    }
}

function resetAddJob() {
    document.getElementById('job-url-input').value = '';
    document.getElementById('job-description-input').value = '';
    document.getElementById('job-form').reset();
    document.getElementById('step-paste').classList.remove('hidden');
    document.getElementById('step-review').classList.add('hidden');
    currentJobDescription = '';
}

// Form submission
document.addEventListener('DOMContentLoaded', () => {
    const jobForm = document.getElementById('job-form');
    if (jobForm) {
        jobForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(jobForm);
            const jobData = {
                company: formData.get('company'),
                position: formData.get('position'),
                location: formData.get('location') || null,
                job_url: formData.get('job_url') || null,
                salary_min: formData.get('salary_min') ? parseInt(formData.get('salary_min')) : null,
                salary_max: formData.get('salary_max') ? parseInt(formData.get('salary_max')) : null,
                status: formData.get('status'),
                notes: formData.get('notes') || null,
                job_description: currentJobDescription || null
            };
            
            showLoading(true);
            
            try {
                const response = await fetch(`${API_BASE}/api/jobs`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(jobData)
                });
                
                if (response.ok) {
                    showToast('Job application saved!', 'success');
                    resetAddJob();
                    showPage('jobs');
                } else {
                    throw new Error('Failed to save job');
                }
            } catch (error) {
                console.error('Failed to save job:', error);
                showToast('Failed to save job application', 'error');
            } finally {
                showLoading(false);
            }
        });
    }
});

// ========================================
// ATS Analyzer - With Saved Job Selection
// ========================================

async function loadJobsForATS() {
    try {
        const response = await fetch(`${API_BASE}/api/jobs/with-descriptions`);
        jobsWithDescriptions = await response.json();
        
        const select = document.getElementById('saved-job-select');
        const section = document.getElementById('saved-jobs-section');
        
        if (select && jobsWithDescriptions.length > 0) {
            select.innerHTML = `
                <option value="">-- Select a saved job --</option>
                ${jobsWithDescriptions.map(job => `
                    <option value="${job.id}">${escapeHtml(job.company)} - ${escapeHtml(job.position)}</option>
                `).join('')}
            `;
            if (section) section.classList.remove('hidden');
        } else if (section) {
            section.classList.add('hidden');
        }
    } catch (error) {
        console.error('Failed to load jobs for ATS:', error);
    }
}

function loadSavedJobDescription() {
    const select = document.getElementById('saved-job-select');
    const jobId = parseInt(select.value);
    
    if (!jobId) return;
    
    const job = jobsWithDescriptions.find(j => j.id === jobId);
    if (job && job.job_description) {
        document.getElementById('job-desc-ats').value = job.job_description;
        document.getElementById('company-name-cl').value = job.company || '';
        showToast(`Loaded: ${job.company} - ${job.position}`, 'success');
    }
}

async function analyzeATS() {
    const resumeText = document.getElementById('resume-text').value.trim();
    const jobDesc = document.getElementById('job-desc-ats').value.trim();
    
    if (!resumeText || !jobDesc) {
        showToast('Please fill in both resume and job description', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/ats/analyze`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_text: resumeText, job_description: jobDesc })
        });
        
        if (!response.ok) throw new Error('Analysis failed');
        
        const result = await response.json();
        
        document.getElementById('ats-score-value').textContent = result.score;
        
        const scoreCard = document.querySelector('.ats-score-card');
        if (result.score >= 70) {
            scoreCard.style.background = 'linear-gradient(135deg, #22c55e, #10b981)';
        } else if (result.score >= 50) {
            scoreCard.style.background = 'linear-gradient(135deg, #eab308, #f59e0b)';
        } else {
            scoreCard.style.background = 'linear-gradient(135deg, #ef4444, #dc2626)';
        }
        
        const keywordsContainer = document.getElementById('missing-keywords');
        if (result.missing_keywords?.length > 0) {
            keywordsContainer.innerHTML = result.missing_keywords.map(kw => 
                `<span class="keyword-tag">${escapeHtml(kw)}</span>`
            ).join('');
        } else {
            keywordsContainer.innerHTML = '<p style="color: var(--accent-green);">Great! No critical keywords missing.</p>';
        }
        
        const suggestionsList = document.getElementById('suggestions-list');
        if (result.suggestions?.length > 0) {
            suggestionsList.innerHTML = result.suggestions.map(s => `<li>${escapeHtml(s)}</li>`).join('');
        } else {
            suggestionsList.innerHTML = '<li>Your resume looks well-optimized!</li>';
        }
        
        document.getElementById('ats-summary').textContent = result.summary || 'Analysis complete.';
        document.getElementById('ats-results').classList.remove('hidden');
        
        showToast('Analysis complete!', 'success');
        
    } catch (error) {
        console.error('ATS analysis failed:', error);
        showToast('Failed to analyze resume. Please try again.', 'error');
    } finally {
        showLoading(false);
    }
}

async function generateCoverLetter() {
    const resumeText = document.getElementById('resume-text').value.trim();
    const jobDesc = document.getElementById('job-desc-ats').value.trim();
    const companyName = document.getElementById('company-name-cl').value.trim();
    const tone = document.getElementById('tone-cl').value;
    
    if (!resumeText || !jobDesc || !companyName) {
        showToast('Please fill in resume, job description, and company name', 'error');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/api/ats/cover-letter`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_text: resumeText, job_description: jobDesc, company_name: companyName, tone: tone })
        });
        
        if (!response.ok) throw new Error('Generation failed');
        
        const result = await response.json();
        
        document.getElementById('cover-letter-text').textContent = result.cover_letter;
        document.getElementById('cover-letter-output').classList.remove('hidden');
        
        showToast('Cover letter generated!', 'success');
        
    } catch (error) {
        console.error('Cover letter generation failed:', error);
        showToast('Failed to generate cover letter', 'error');
    } finally {
        showLoading(false);
    }
}

function copyCoverLetter() {
    const text = document.getElementById('cover-letter-text').textContent;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// ========================================
// Job Modal
// ========================================

async function openJobModal(jobId) {
    const job = allJobs.find(j => j.id === jobId);
    if (!job) return;
    
    document.getElementById('modal-title').textContent = `${job.company} - ${job.position}`;
    
    document.getElementById('modal-body').innerHTML = `
        <div class="job-detail-grid">
            <div class="detail-item">
                <label>Company</label>
                <p>${escapeHtml(job.company)}</p>
            </div>
            <div class="detail-item">
                <label>Position</label>
                <p>${escapeHtml(job.position)}</p>
            </div>
            <div class="detail-item">
                <label>Location</label>
                <p>${escapeHtml(job.location || 'Not specified')}</p>
            </div>
            <div class="detail-item">
                <label>Salary Range</label>
                <p>${job.salary_min ? `$${formatNumber(job.salary_min)}${job.salary_max ? ` - $${formatNumber(job.salary_max)}` : ''}` : 'Not specified'}</p>
            </div>
            <div class="detail-item">
                <label>Status</label>
                <p><span class="job-status status-${job.status}">${job.status}</span></p>
            </div>
            <div class="detail-item">
                <label>Date Added</label>
                <p>${formatDate(job.date_added)}</p>
            </div>
            ${job.job_url ? `
            <div class="detail-item full-width">
                <label>Job URL</label>
                <p><a href="${escapeHtml(job.job_url)}" target="_blank" style="color: var(--accent-blue);">${escapeHtml(job.job_url)}</a></p>
            </div>` : ''}
            ${job.notes ? `
            <div class="detail-item full-width">
                <label>Notes</label>
                <p>${escapeHtml(job.notes)}</p>
            </div>` : ''}
            ${job.job_description ? `
            <div class="detail-item full-width">
                <label>Job Description</label>
                <p style="max-height: 150px; overflow-y: auto; font-size: 13px; color: var(--text-secondary);">${escapeHtml(job.job_description).substring(0, 500)}${job.job_description.length > 500 ? '...' : ''}</p>
            </div>` : ''}
        </div>
        
        <div class="modal-actions" style="margin-top: 24px; display: flex; gap: 12px; flex-wrap: wrap;">
            <select id="modal-status-update" class="filter-select" style="flex: 1; min-width: 150px;">
                <option value="wishlist" ${job.status === 'wishlist' ? 'selected' : ''}>Wishlist</option>
                <option value="applied" ${job.status === 'applied' ? 'selected' : ''}>Applied</option>
                <option value="interviewing" ${job.status === 'interviewing' ? 'selected' : ''}>Interviewing</option>
                <option value="offer" ${job.status === 'offer' ? 'selected' : ''}>Offer</option>
                <option value="rejected" ${job.status === 'rejected' ? 'selected' : ''}>Rejected</option>
            </select>
            <button class="btn btn-primary" onclick="updateJobStatus(${job.id})">Update Status</button>
            ${job.job_description ? `<button class="btn btn-secondary" onclick="analyzeJobFromModal(${job.id})">Analyze with ATS</button>` : ''}
            <button class="btn btn-secondary" style="color: var(--accent-red);" onclick="deleteJob(${job.id})">Delete</button>
        </div>
    `;
    
    document.getElementById('job-modal').classList.remove('hidden');
}

function analyzeJobFromModal(jobId) {
    const job = allJobs.find(j => j.id === jobId);
    if (job && job.job_description) {
        closeModal();
        showPage('ats');
        setTimeout(() => {
            document.getElementById('job-desc-ats').value = job.job_description;
            document.getElementById('company-name-cl').value = job.company || '';
            showToast(`Loaded: ${job.company}. Now paste your resume!`, 'success');
        }, 100);
    }
}

function closeModal() {
    document.getElementById('job-modal').classList.add('hidden');
}

async function updateJobStatus(jobId) {
    const newStatus = document.getElementById('modal-status-update').value;
    
    try {
        const response = await fetch(`${API_BASE}/api/jobs/${jobId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: newStatus })
        });
        
        if (response.ok) {
            showToast('Status updated!', 'success');
            closeModal();
            loadJobs();
            loadDashboard();
        } else {
            throw new Error('Update failed');
        }
    } catch (error) {
        showToast('Failed to update status', 'error');
    }
}

async function deleteJob(jobId) {
    if (!confirm('Are you sure you want to delete this job application?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/jobs/${jobId}`, { method: 'DELETE' });
        
        if (response.ok) {
            showToast('Job deleted', 'success');
            closeModal();
            loadJobs();
            loadDashboard();
        } else {
            throw new Error('Delete failed');
        }
    } catch (error) {
        showToast('Failed to delete job', 'error');
    }
}

// ========================================
// Utilities
// ========================================

function showLoading(show) {
    const overlay = document.getElementById('loading');
    if (show) overlay.classList.remove('hidden');
    else overlay.classList.add('hidden');
}

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// ========================================
// Initialize
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', () => showPage(item.dataset.page));
    });
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });
    
    checkApiConnection();
    loadDashboard();
});

async function checkApiConnection() {
    try {
        const response = await fetch(`${API_BASE}/`);
        document.querySelector('.status-dot').style.background = response.ok ? 'var(--accent-green)' : 'var(--accent-red)';
    } catch (error) {
        document.querySelector('.status-dot').style.background = 'var(--accent-red)';
        showToast('API not connected. Make sure the server is running.', 'error');
    }
}