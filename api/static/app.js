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

// UI Element IDs
const UI = {
    selectionSection: 'selectionSection',
    configSection: 'configSection',
    progressSection: 'progressSection',
    resultsSection: 'resultsSection'
};

// Operation configurations
const OPERATIONS = {
    media_organize: {
        title: 'Organize Media',
        endpoint: '/media/organize',
        requiresDest: true
    },
    subfolders: {
        title: 'Expand to Days',
        endpoint: '/media/subfolders',
        requiresDest: false
    },
    android_clean: {
        title: 'Clean Android Backup',
        endpoint: '/android/clean',
        requiresDest: false,
        showThreshold: true
    },
    organize_types: {
        title: 'Organize by Type',
        endpoint: '/files/organize-types',
        requiresDest: true
    },
    consolidate_pdfs: {
        title: 'Consolidate PDFs',
        endpoint: '/files/consolidate-pdfs',
        requiresDest: true
    },
    analyze: {
        title: 'Analyze Extensions',
        endpoint: '/files/analyze',
        requiresDest: false
    }
};

// ========================================
// DOM Elements
// ========================================

const elements = {
    // Sections
    selectionSection: document.getElementById('selectionSection'),
    configSection: document.getElementById('configSection'),
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
    safeMode: document.getElementById('safeMode'),
    cancelBtn: document.getElementById('cancelBtn'),
    startBtn: document.getElementById('startBtn'),

    // Progress
    progressFill: document.getElementById('progressFill'),
    progressPercent: document.getElementById('progressPercent'),
    progressCount: document.getElementById('progressCount'),
    currentFileName: document.getElementById('currentFileName'),
    statusMessage: document.getElementById('statusMessage'),
    abortBtn: document.getElementById('abortBtn'),

    // Results
    statMoved: document.getElementById('statMoved'),
    statErrors: document.getElementById('statErrors'),
    statDuration: document.getElementById('statDuration'),
    detailsContent: document.getElementById('detailsContent'),

    // Modal
    abortModal: document.getElementById('abortModal'),
    cancelAbortBtn: document.getElementById('cancelAbortBtn'),
    confirmAbortBtn: document.getElementById('confirmAbortBtn')
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
        dry_run: config.dryRun,
        safe_mode: config.safeMode
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
    // Highlight selection
    document.querySelectorAll('.operation-card').forEach(card => {
        if (card.dataset.op === operation) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    });

    state.selectedOperation = operation;
    showConfigPanel(operation);
}

function showConfigPanel(operation) {
    const op = OPERATIONS[operation];

    elements.configTitle.textContent = op.title;
    elements.destDirGroup.style.display = op.requiresDest ? 'block' : 'none';
    elements.thresholdGroup.style.display = op.showThreshold ? 'block' : 'none';

    elements.destDir.required = op.requiresDest;

    // Slide up animation
    elements.configSection.style.display = 'block';
    elements.selectionSection.style.display = 'none'; // Hide grid to focus
}

function hideConfigPanel() {
    elements.configSection.style.display = 'none';
    elements.selectionSection.style.display = 'block'; // Show grid again

    document.querySelectorAll('.operation-card').forEach(card => {
        card.classList.remove('selected');
    });
    state.selectedOperation = null;
}

function showProgressSection() {
    elements.configSection.style.display = 'none';
    elements.progressSection.style.display = 'block';

    elements.progressFill.style.width = '0%';
    elements.progressPercent.textContent = '0%';
    elements.progressCount.textContent = '0 / 0 files';
    elements.currentFileName.textContent = 'Connecting...';
    elements.statusMessage.textContent = 'Initializing secure operation...';
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

    const duration = state.startTime
        ? ((Date.now() - state.startTime) / 1000).toFixed(1)
        : 0;

    const result = data.result || {};
    elements.statMoved.textContent = result.moved || data.current || 0;
    elements.statErrors.textContent = result.errors || 0;
    elements.statDuration.textContent = `${duration}s`;

    // Render details
    renderDetails(result);

    // Reset state
    state.currentJobId = null;
    state.startTime = null;
}

function renderDetails(result) {
    if (result.details && result.details.length > 0) {
        const html = result.details.slice(0, 100).map(d => {
            const icon = d.status === 'moved' ? '✓' : d.status === 'dry_run' ? '👁' : '✗';
            const color = d.status === 'error' ? 'var(--danger)' : d.status === 'moved' ? 'var(--success)' : 'inherit';
            const file = d.src ? d.src.split(/[/\\]/).pop() : d.file || 'unknown';
            return `<div style="color:${color}; margin-bottom:4px;">[${icon}] ${file}<br><span style="color:var(--text-muted); font-size:0.8em; margin-left:1.5em;">${d.reason || ''} (${d.mode || 'standard'})</span></div>`;
        }).join('');
        elements.detailsContent.innerHTML = html;
        if (result.details.length > 100) elements.detailsContent.innerHTML += '...more...';
    } else if (result.counts) {
        // Analysis result
        const html = Object.entries(result.counts)
            .sort((a, b) => b[1] - a[1])
            .map(([ext, cnt]) => `<div>${ext}: ${cnt}</div>`)
            .join('');
        elements.detailsContent.innerHTML = html;
    } else {
        elements.detailsContent.textContent = "No actions performed.";
    }
}

// ========================================
// Event Listeners
// ========================================

// Card Selection
document.querySelectorAll('.operation-card').forEach(card => {
    card.addEventListener('click', () => {
        selectOperation(card.dataset.op);
    });
});

// Cancel Config
elements.cancelBtn.addEventListener('click', hideConfigPanel);

// Start Operation
elements.configForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!state.selectedOperation) return;

    const config = {
        sourceDir: elements.sourceDir.value.trim(),
        destDir: elements.destDir.value.trim(),
        dryRun: elements.dryRun.checked,
        safeMode: elements.safeMode.checked,
        threshold: parseInt(elements.threshold.value) || 50
    };

    elements.startBtn.disabled = true;
    elements.startBtn.textContent = 'Starting...';

    try {
        state.startTime = Date.now();
        const response = await startOperation(state.selectedOperation, config);

        if (response.job_id) {
            state.currentJobId = response.job_id;
            showProgressSection();
            connectJobStream(response.job_id);
        }
    } catch (error) {
        alert('Error: ' + error.message);
    } finally {
        elements.startBtn.disabled = false;
        elements.startBtn.textContent = 'Start Operation';
    }
});

// Abort Flow
elements.abortBtn.addEventListener('click', () => elements.abortModal.classList.add('show'));
elements.cancelAbortBtn.addEventListener('click', () => elements.abortModal.classList.remove('show'));
elements.confirmAbortBtn.addEventListener('click', async () => {
    elements.abortModal.classList.remove('show');
    if (state.currentJobId) {
        await abortJob(state.currentJobId);
        elements.statusMessage.textContent = 'Aborting...';
    }
});

// Initialize
// (No need for refreshJobsList loop yet? I removed the jobs widget from index layout)

// ========================================
// AI Tools
// ========================================

const aiElements = {
    searchInput: document.getElementById('aiSearchInput'),
    searchBtn: document.getElementById('aiSearchBtn'),
    indexCard: document.getElementById('aiIndexCard'),
    suggestCard: document.getElementById('aiSuggestCard'),
    indexConfig: document.getElementById('aiIndexConfig'),
    suggestConfig: document.getElementById('aiSuggestConfig'),
    indexCancel: document.getElementById('aiIndexCancel'),
    suggestCancel: document.getElementById('aiSuggestCancel'),
    indexStart: document.getElementById('aiIndexStart'),
    suggestStart: document.getElementById('aiSuggestStart'),
    sourceDir: document.getElementById('aiSourceDir'),
    suggestDir: document.getElementById('aiSuggestDir'),
    forceReindex: document.getElementById('aiForceReindex'),
    resultsSection: document.getElementById('aiSearchResults'),
    resultsTitle: document.getElementById('aiResultsTitle'),
    resultsGrid: document.getElementById('aiResultsGrid'),
    resultsClose: document.getElementById('aiResultsClose')
};

// Search
aiElements.searchBtn.addEventListener('click', searchMedia);
aiElements.searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchMedia();
});

async function searchMedia() {
    const query = aiElements.searchInput.value.trim();
    if (!query) return;

    aiElements.searchBtn.disabled = true;
    aiElements.searchBtn.textContent = 'Searching...';

    try {
        const data = await apiRequest('/ai/search', 'POST', { query, top_k: 20 });
        renderAIResults(data);
    } catch (error) {
        alert('Search Error: ' + error.message);
    } finally {
        aiElements.searchBtn.disabled = false;
        aiElements.searchBtn.textContent = 'Search';
    }
}

function renderAIResults(data) {
    const results = data.results || [];
    aiElements.resultsTitle.textContent = `${results.length} result${results.length !== 1 ? 's' : ''} for "${data.query}"`;
    aiElements.resultsSection.style.display = 'block';

    if (results.length === 0) {
        aiElements.resultsGrid.innerHTML = '<div class="ai-no-results">No matches found. Try indexing your library first.</div>';
        return;
    }

    aiElements.resultsGrid.innerHTML = results.map(r => `
        <div class="ai-result-card">
            <div class="ai-result-info">
                <h4>${r.file}</h4>
                <p class="ai-result-desc">${r.description || 'No description'}</p>
                <div class="ai-result-tags">
                    ${(r.tags || []).map(t => `<span class="ai-tag">${t}</span>`).join('')}
                </div>
                <div class="ai-result-meta">
                    <span class="ai-meta-scene">${r.scene || ''}</span>
                    <span class="ai-meta-score">Quality: ${r.quality_score || '?'}/10</span>
                    <span class="ai-meta-relevance">Match: ${Math.round((r.relevance_score || 0) * 100)}%</span>
                </div>
            </div>
        </div>
    `).join('');
}

aiElements.resultsClose.addEventListener('click', () => {
    aiElements.resultsSection.style.display = 'none';
});

// Index Library
aiElements.indexCard.addEventListener('click', () => {
    aiElements.indexConfig.style.display = 'block';
    aiElements.suggestConfig.style.display = 'none';
});

aiElements.indexCancel.addEventListener('click', () => {
    aiElements.indexConfig.style.display = 'none';
});

aiElements.indexStart.addEventListener('click', async () => {
    const sourceDir = aiElements.sourceDir.value.trim();
    if (!sourceDir) { alert('Please enter a directory path.'); return; }

    aiElements.indexStart.disabled = true;
    aiElements.indexStart.textContent = 'Starting...';

    try {
        state.startTime = Date.now();
        const response = await apiRequest('/ai/index', 'POST', {
            source_dir: sourceDir,
            force_reindex: aiElements.forceReindex.checked
        });

        if (response.job_id) {
            state.currentJobId = response.job_id;
            aiElements.indexConfig.style.display = 'none';
            // Hide the selection grid and AI section, show progress
            elements.selectionSection.style.display = 'none';
            document.getElementById('aiSection').style.display = 'none';
            showProgressSection();
            connectJobStream(response.job_id);
        }
    } catch (error) {
        alert('Index Error: ' + error.message);
    } finally {
        aiElements.indexStart.disabled = false;
        aiElements.indexStart.textContent = 'Start Indexing';
    }
});

// Smart Suggest
aiElements.suggestCard.addEventListener('click', () => {
    aiElements.suggestConfig.style.display = 'block';
    aiElements.indexConfig.style.display = 'none';
});

aiElements.suggestCancel.addEventListener('click', () => {
    aiElements.suggestConfig.style.display = 'none';
});

aiElements.suggestStart.addEventListener('click', async () => {
    const dir = aiElements.suggestDir.value.trim();
    if (!dir) { alert('Please enter a directory path.'); return; }

    aiElements.suggestStart.disabled = true;
    aiElements.suggestStart.textContent = 'Analyzing...';

    try {
        const data = await apiRequest('/ai/suggestions', 'POST', { file_path: dir });
        renderSuggestions(data);
    } catch (error) {
        alert('Suggestion Error: ' + error.message);
    } finally {
        aiElements.suggestStart.disabled = false;
        aiElements.suggestStart.textContent = 'Get Suggestions';
    }
});

function renderSuggestions(data) {
    if (data.error) {
        alert('Error: ' + data.error);
        return;
    }

    aiElements.resultsTitle.textContent = 'AI Organization Suggestions';
    aiElements.resultsSection.style.display = 'block';
    aiElements.suggestConfig.style.display = 'none';

    const structure = data.suggested_structure || {};
    const rationale = data.rationale || '';

    let html = `<div class="ai-suggestion-rationale">${rationale}</div>`;
    html += '<div class="ai-suggestion-folders">';

    for (const [folder, files] of Object.entries(structure)) {
        html += `
            <div class="ai-suggestion-folder">
                <div class="ai-folder-name">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
                    </svg>
                    ${folder}
                </div>
                <div class="ai-folder-files">${(files || []).map(f => `<span class="ai-tag">${f}</span>`).join('')}</div>
            </div>
        `;
    }
    html += '</div>';

    aiElements.resultsGrid.innerHTML = html;
}
