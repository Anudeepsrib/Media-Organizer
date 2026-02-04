/**
 * Mobile Media Organizer - Dashboard Application
 * Handles API communication, SSE streaming, and UI state management
 */

// ========================================
// State
// ========================================

const state = {
    selectedOperation: null,
    currentJobId: null,
    eventSource: null,
    startTime: null
};

// Operation configurations
const OPERATIONS = {
    media_organize: {
        title: 'Organize Media',
        endpoint: '/media/organize',
        requiresDest: true,
        icon: '📅'
    },
    expand_dates: {
        title: 'Expand to Days',
        endpoint: '/media/subfolders',
        requiresDest: false,
        icon: '📁'
    },
    android_clean: {
        title: 'Clean Android Backup',
        endpoint: '/android/clean',
        requiresDest: false,
        showThreshold: true,
        icon: '🤖'
    },
    organize_types: {
        title: 'Organize by Type',
        endpoint: '/files/organize-types',
        requiresDest: true,
        icon: '📦'
    },
    consolidate_pdfs: {
        title: 'Consolidate PDFs',
        endpoint: '/files/consolidate-pdfs',
        requiresDest: true,
        icon: '📄'
    },
    analyze_extensions: {
        title: 'Analyze Extensions',
        endpoint: '/files/analyze',
        requiresDest: false,
        icon: '📊'
    }
};

// ========================================
// DOM Elements
// ========================================

const elements = {
    // Sections
    configPanel: document.getElementById('configPanel'),
    progressSection: document.getElementById('progressSection'),
    resultsSection: document.getElementById('resultsSection'),

    // Config Form
    configTitle: document.getElementById('configTitle'),
    configForm: document.getElementById('configForm'),
    sourceDir: document.getElementById('sourceDir'),
    destDir: document.getElementById('destDir'),
    destDirGroup: document.getElementById('destDirGroup'),
    thresholdGroup: document.getElementById('thresholdGroup'),
    threshold: document.getElementById('threshold'),
    dryRun: document.getElementById('dryRun'),
    cancelBtn: document.getElementById('cancelBtn'),
    startBtn: document.getElementById('startBtn'),

    // Progress
    progressTitle: document.getElementById('progressTitle'),
    progressFill: document.getElementById('progressFill'),
    progressPercent: document.getElementById('progressPercent'),
    progressCount: document.getElementById('progressCount'),
    currentFileName: document.getElementById('currentFileName'),
    statusMessage: document.getElementById('statusMessage'),
    abortBtn: document.getElementById('abortBtn'),

    // Results
    resultsTitle: document.getElementById('resultsTitle'),
    resultsBadge: document.getElementById('resultsBadge'),
    movedCount: document.getElementById('movedCount'),
    errorCount: document.getElementById('errorCount'),
    duration: document.getElementById('duration'),
    detailsContent: document.getElementById('detailsContent'),
    newOperationBtn: document.getElementById('newOperationBtn'),

    // Jobs
    jobsList: document.getElementById('jobsList'),

    // Modal
    abortModal: document.getElementById('abortModal'),
    abortCancelBtn: document.getElementById('abortCancelBtn'),
    abortConfirmBtn: document.getElementById('abortConfirmBtn')
};

// ========================================
// API Functions
// ========================================

async function apiRequest(endpoint, method = 'GET', body = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };

    if (body) {
        options.body = JSON.stringify(body);
    }

    const response = await fetch(endpoint, options);

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || 'Request failed');
    }

    return response.json();
}

async function startOperation(operation, config) {
    const op = OPERATIONS[operation];
    const body = {
        source_dir: config.sourceDir,
        dry_run: config.dryRun
    };

    if (op.requiresDest) {
        body.dest_dir = config.destDir;
    }

    if (op.showThreshold) {
        body.threshold_mb = config.threshold;
    }

    return apiRequest(op.endpoint, 'POST', body);
}

async function abortJob(jobId) {
    return apiRequest(`/jobs/${jobId}/abort`, 'POST');
}

async function fetchJobs() {
    return apiRequest('/jobs');
}

async function fetchJobStatus(jobId) {
    return apiRequest(`/jobs/${jobId}`);
}

// ========================================
// SSE Streaming
// ========================================

function connectJobStream(jobId) {
    if (state.eventSource) {
        state.eventSource.close();
    }

    state.eventSource = new EventSource(`/jobs/${jobId}/stream`);

    state.eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            updateProgress(data);

            // Check if job finished
            if (['completed', 'aborted', 'failed'].includes(data.status)) {
                state.eventSource.close();
                state.eventSource = null;
                showResults(data);
            }
        } catch (e) {
            console.error('SSE parse error:', e);
        }
    };

    state.eventSource.onerror = (error) => {
        console.error('SSE error:', error);
        state.eventSource.close();
        state.eventSource = null;

        // Fall back to polling
        pollJobStatus(jobId);
    };
}

async function pollJobStatus(jobId) {
    try {
        const data = await fetchJobStatus(jobId);
        updateProgress(data);

        if (['completed', 'aborted', 'failed'].includes(data.status)) {
            showResults(data);
        } else {
            setTimeout(() => pollJobStatus(jobId), 500);
        }
    } catch (e) {
        console.error('Polling error:', e);
    }
}

// ========================================
// UI Updates
// ========================================

function selectOperation(operation) {
    // Clear previous selection
    document.querySelectorAll('.operation-card').forEach(card => {
        card.classList.remove('selected');
    });

    // Select new
    const card = document.querySelector(`[data-operation="${operation}"]`);
    if (card) {
        card.classList.add('selected');
    }

    state.selectedOperation = operation;
    showConfigPanel(operation);
}

function showConfigPanel(operation) {
    const op = OPERATIONS[operation];

    elements.configTitle.textContent = `Configure: ${op.title}`;
    elements.destDirGroup.style.display = op.requiresDest ? 'block' : 'none';
    elements.thresholdGroup.style.display = op.showThreshold ? 'block' : 'none';

    if (op.requiresDest) {
        elements.destDir.required = true;
    } else {
        elements.destDir.required = false;
    }

    elements.configPanel.style.display = 'block';
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
}

function hideConfigPanel() {
    elements.configPanel.style.display = 'none';
    document.querySelectorAll('.operation-card').forEach(card => {
        card.classList.remove('selected');
    });
    state.selectedOperation = null;
}

function showProgressSection(operation) {
    const op = OPERATIONS[operation];

    elements.configPanel.style.display = 'none';
    elements.progressSection.style.display = 'block';
    elements.resultsSection.style.display = 'none';

    elements.progressTitle.textContent = `${op.icon} ${op.title}`;
    elements.progressFill.style.width = '0%';
    elements.progressPercent.textContent = '0%';
    elements.progressCount.textContent = '0 / 0 files';
    elements.currentFileName.textContent = 'Starting...';
    elements.statusMessage.textContent = 'Initializing operation...';
}

function updateProgress(data) {
    elements.progressFill.style.width = `${data.progress}%`;
    elements.progressPercent.textContent = `${data.progress}%`;
    elements.progressCount.textContent = `${data.current} / ${data.total} files`;
    elements.currentFileName.textContent = data.current_file || 'Processing...';
    elements.statusMessage.textContent = data.message || 'Processing...';
}

function showResults(data) {
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'block';

    // Calculate duration
    const duration = state.startTime
        ? Math.round((Date.now() - state.startTime) / 1000)
        : 0;

    // Set badge
    let badgeClass = 'success';
    let badgeText = 'Success';

    if (data.status === 'aborted') {
        badgeClass = 'warning';
        badgeText = 'Aborted';
        elements.resultsTitle.textContent = 'Operation Aborted';
    } else if (data.status === 'failed') {
        badgeClass = 'error';
        badgeText = 'Failed';
        elements.resultsTitle.textContent = 'Operation Failed';
    } else {
        elements.resultsTitle.textContent = 'Operation Complete';
    }

    elements.resultsBadge.className = `results-badge ${badgeClass}`;
    elements.resultsBadge.textContent = badgeText;

    // Stats
    const result = data.result || {};
    elements.movedCount.textContent = result.moved || data.current || 0;
    elements.errorCount.textContent = result.errors || 0;
    elements.duration.textContent = `${duration}s`;

    // Details
    if (result.details && result.details.length > 0) {
        const detailsHtml = result.details.slice(0, 100).map(d => {
            const status = d.status === 'moved' ? '✓' : d.status === 'dry_run' ? '👁' : '✗';
            const file = d.src ? d.src.split(/[/\\]/).pop() : d.file || 'unknown';
            return `<div>${status} ${file} → ${d.reason || ''}</div>`;
        }).join('');

        elements.detailsContent.innerHTML = detailsHtml;

        if (result.details.length > 100) {
            elements.detailsContent.innerHTML += `<div>... and ${result.details.length - 100} more</div>`;
        }
    } else if (result.counts) {
        // Extension analysis results
        const countsHtml = Object.entries(result.counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 50)
            .map(([ext, count]) => `<div>${ext}: ${count} files</div>`)
            .join('');
        elements.detailsContent.innerHTML = countsHtml;
    } else {
        elements.detailsContent.innerHTML = '<div>No details available</div>';
    }

    // Reset state
    state.currentJobId = null;
    state.startTime = null;

    // Refresh jobs list
    refreshJobsList();
}

async function refreshJobsList() {
    try {
        const data = await fetchJobs();

        if (data.jobs && data.jobs.length > 0) {
            elements.jobsList.innerHTML = data.jobs
                .slice(0, 10)
                .map(job => {
                    const op = Object.entries(OPERATIONS).find(([key, val]) =>
                        job.job_type.includes(key.replace('_', ''))
                    );
                    const title = op ? op[1].title : job.job_type;
                    const time = new Date(job.started_at).toLocaleTimeString();

                    return `
                        <div class="job-item" data-job-id="${job.id}">
                            <div class="job-status ${job.status}"></div>
                            <div class="job-info">
                                <div class="job-type">${title}</div>
                                <div class="job-time">${time}</div>
                            </div>
                            <div class="job-progress">${job.progress}%</div>
                        </div>
                    `;
                })
                .join('');
        } else {
            elements.jobsList.innerHTML = '<p class="no-jobs">No recent jobs</p>';
        }
    } catch (e) {
        console.error('Failed to fetch jobs:', e);
    }
}

function resetToOperations() {
    hideConfigPanel();
    elements.progressSection.style.display = 'none';
    elements.resultsSection.style.display = 'none';
    refreshJobsList();
}

function showAbortModal() {
    elements.abortModal.classList.add('show');
}

function hideAbortModal() {
    elements.abortModal.classList.remove('show');
}

// ========================================
// Event Handlers
// ========================================

// Operation card clicks
document.querySelectorAll('.operation-card').forEach(card => {
    card.addEventListener('click', () => {
        const operation = card.dataset.operation;
        selectOperation(operation);
    });
});

// Cancel button
elements.cancelBtn.addEventListener('click', hideConfigPanel);

// Form submission
elements.configForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    if (!state.selectedOperation) return;

    const config = {
        sourceDir: elements.sourceDir.value.trim(),
        destDir: elements.destDir.value.trim(),
        dryRun: elements.dryRun.checked,
        threshold: parseInt(elements.threshold.value) || 50
    };

    // Disable button
    elements.startBtn.disabled = true;
    elements.startBtn.querySelector('.btn-text').textContent = 'Starting...';
    elements.startBtn.querySelector('.btn-loader').style.display = 'inline-block';

    try {
        state.startTime = Date.now();
        const response = await startOperation(state.selectedOperation, config);

        if (response.job_id) {
            state.currentJobId = response.job_id;
            showProgressSection(state.selectedOperation);
            connectJobStream(response.job_id);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        elements.startBtn.disabled = false;
        elements.startBtn.querySelector('.btn-text').textContent = 'Start Operation';
        elements.startBtn.querySelector('.btn-loader').style.display = 'none';
    }
});

// Abort button
elements.abortBtn.addEventListener('click', showAbortModal);

// Modal buttons
elements.abortCancelBtn.addEventListener('click', hideAbortModal);

elements.abortConfirmBtn.addEventListener('click', async () => {
    hideAbortModal();

    if (state.currentJobId) {
        try {
            await abortJob(state.currentJobId);
            elements.statusMessage.textContent = 'Abort requested, waiting for operation to stop...';
        } catch (e) {
            console.error('Abort failed:', e);
        }
    }
});

// New operation button
elements.newOperationBtn.addEventListener('click', resetToOperations);

// ========================================
// Initialize
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    refreshJobsList();

    // Refresh jobs list periodically
    setInterval(refreshJobsList, 5000);
});
