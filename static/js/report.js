document.addEventListener('DOMContentLoaded', async () => {
    const token = getToken();
    if (!token) { window.location.href = '/login'; return; }

    const reportId = document.querySelector('main').dataset.reportId || window.location.pathname.split('/').pop();
    const loading = document.getElementById('reportLoading');
    const report = document.getElementById('fullReport');

    try {
        const res = await fetch(`/api/report/${reportId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!res.ok) throw new Error('Not found');
        const data = await res.json();
        loading.classList.add('hidden');
        report.classList.remove('hidden');

        const result = typeof data.full_result === 'string' ? JSON.parse(data.full_result) : data.full_result;

        document.getElementById('reportTitle').textContent = data.title || 'Untitled';
        document.getElementById('reportDate').textContent = new Date(data.created_at).toLocaleString();

        const ai = result.ai_detection || {};
        const plag = result.plagiarism || {};

        setRing('repAiRing', 'repAiText', ai.ai_score || 0);
        setRing('repHumanRing', 'repHumanText', ai.human_score || 0);
        setRing('repPlagRing', 'repPlagText', plag.plagiarism_score || 0);

        const modelList = document.getElementById('repModelList');
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
            modelList.innerHTML = '<p class="empty-state">Details unavailable</p>';
        }

        document.getElementById('repTextPreview').textContent = result.text_preview || data.text || '';

        const sourcesList = document.getElementById('repSourcesList');
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
    } catch (e) {
        loading.textContent = 'Report not found or access denied.';
    }
});

function setRing(ringId, textId, value) {
    const circumference = 100;
    const offset = circumference - Math.min(value, 100);
    document.getElementById(ringId).setAttribute('stroke-dasharray', `${circumference - offset} ${offset}`);
    document.getElementById(textId).textContent = Math.round(value) + '%';
}
