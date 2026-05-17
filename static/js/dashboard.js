document.addEventListener('DOMContentLoaded', () => {
    const token = getToken();
    if (!token) { window.location.href = '/login'; return; }
    document.getElementById('userEmail').textContent = getUserEmail();
    loadHistory();
    updateCharCount();
    document.getElementById('textInput').addEventListener('input', updateCharCount);
});

function updateCharCount() {
    const el = document.getElementById('textInput');
    document.getElementById('charCount').textContent = el.value.length;
}

async function runCheck() {
    const text = document.getElementById('textInput').value;
    const title = document.getElementById('title').value;
    const btn = document.getElementById('checkBtn');
    const errEl = document.getElementById('checkError');
    errEl.classList.add('hidden');

    if (text.length < 50) {
        errEl.textContent = 'Text must be at least 50 characters.';
        errEl.classList.remove('hidden');
        return;
    }

    btn.disabled = true;
    btn.querySelector('.btn-text').classList.add('hidden');
    btn.querySelector('.btn-loader').classList.remove('hidden');

    try {
        const res = await fetch('/api/check', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': `Bearer ${getToken()}`,
            },
            body: new URLSearchParams({ text, title }).toString(),
        });
        const data = await res.json();
        if (data.success) {
            displayResults(data.result);
            loadHistory();
        } else {
            errEl.textContent = data.error || 'Check failed';
            errEl.classList.remove('hidden');
        }
    } catch (e) {
        errEl.textContent = 'Network error. Please try again.';
        errEl.classList.remove('hidden');
    } finally {
        btn.disabled = false;
        btn.querySelector('.btn-text').classList.remove('hidden');
        btn.querySelector('.btn-loader').classList.add('hidden');
    }
}

function displayResults(result) {
    const section = document.getElementById('results');
    section.classList.remove('hidden');

    const ai = result.ai_detection;
    const plag = result.plagiarism;

    setRing('aiRing', 'aiScoreText', ai.ai_score, 'AI');
    setRing('humanRing', 'humanScoreText', ai.human_score, 'Human');
    setRing('plagRing', 'plagScoreText', plag.plagiarism_score, 'Plagiarism');

    const confEl = document.getElementById('aiConfidence');
    confEl.textContent = ai.confidence.charAt(0).toUpperCase() + ai.confidence.slice(1);
    confEl.className = 'confidence-badge ' + ai.confidence;

    document.getElementById('matchesCount').textContent = plag.matches_found + ' sources';

    const modelList = document.getElementById('modelList');
    modelList.innerHTML = '';
    if (ai.models && ai.models.length) {
        ai.models.forEach(m => {
            modelList.innerHTML += `
                <div class="model-item">
                    <span class="model-name">${m.model}</span>
                    <div class="model-scores">
                        <span class="model-ai">AI: ${m.ai_score}%</span>
                        <span class="model-human">Human: ${m.human_score}%</span>
                    </div>
                </div>`;
        });
    } else {
        modelList.innerHTML = '<p class="empty-state">Model details unavailable</p>';
    }

    const sourcesList = document.getElementById('sourcesList');
    sourcesList.innerHTML = '';
    if (plag.matches && plag.matches.length) {
        plag.matches.forEach(m => {
            sourcesList.innerHTML += `
                <div class="source-item">
                    <div class="source-badge">${m.source || 'web'}</div>
                    <div class="source-title">
                        <a href="${m.link}" target="_blank" rel="noopener">${m.title || 'Untitled'}</a>
                    </div>
                    <div class="source-snippet">${m.snippet || ''}</div>
                </div>`;
        });
    } else {
        sourcesList.innerHTML = '<p class="empty-state">No matching sources found</p>';
    }

    const reportBtn = document.getElementById('viewReportBtn');
    if (result.report_id) {
        reportBtn.href = `/report/${result.report_id}`;
        reportBtn.classList.remove('hidden');
    } else {
        reportBtn.classList.add('hidden');
    }

    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function setRing(ringId, textId, value, label) {
    const circumference = 100;
    const offset = circumference - Math.min(value, 100);
    document.getElementById(ringId).setAttribute('stroke-dasharray', `${circumference - offset} ${offset}`);
    document.getElementById(textId).textContent = Math.round(value) + '%';
}

async function loadHistory() {
    try {
        const res = await fetch('/api/reports', {
            headers: { 'Authorization': `Bearer ${getToken()}` }
        });
        const data = await res.json();
        const list = document.getElementById('historyList');
        if (!data.reports || !data.reports.length) {
            list.innerHTML = '<p class="empty-state">No checks yet. Run your first analysis above.</p>';
            return;
        }
        list.innerHTML = data.reports.map(r => `
            <a href="/report/${r.id}" class="history-item" style="text-decoration:none;color:inherit;display:flex;">
                <div class="history-item-left">
                    <div class="history-title">${r.title || 'Untitled'}</div>
                    <div class="history-meta">${new Date(r.created_at).toLocaleString()} &middot; ${r.text ? r.text.length + ' chars' : ''}</div>
                </div>
                <div class="history-scores">
                    <span class="history-score ai">AI: ${r.ai_score || 0}%</span>
                    <span class="history-score plag">P: ${r.plagiarism_score || 0}%</span>
                </div>
            </a>
        `).join('');
    } catch (e) {
        // silently fail
    }
}
