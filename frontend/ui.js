// UI helper functions
const ui = {
    showMessage(elementId, message, type = 'success') {
        const el = document.getElementById(elementId);
        if (!el) return;
        el.textContent = message;
        el.className = `message ${type}`;
        el.style.display = 'block';
        setTimeout(() => el.style.display = 'none', 5000);
    },

    trustBadge(score) {
        const cls = score >= 75 ? 'score-high' : score >= 50 ? 'score-medium' : 'score-low';
        return `<span class="trust-score ${cls}">${score}</span>`;
    },

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    },

    shortenUrl(url, max = 40) {
        return url.length > max ? url.substring(0, max) + '...' : url;
    },

    downloadJSON(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    },

    showTab(tabName) {
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        event.target.classList.add('active');
        
        if (tabName === 'identities') loadIdentities();
        if (tabName === 'verifications') loadVerifications();
        if (tabName === 'consistency') loadConsistencyChecks();
    }
};

// Display functions
function displayIdentities(identities) {
    const tbody = document.querySelector('#identitiesTable tbody');
    tbody.innerHTML = identities.map(id => `
        <tr>
            <td>${id.anchor_id}</td>
            <td>${id.user_pub_key.substring(0, 40)}...</td>
            <td>${ui.trustBadge(id.trust_score)}</td>
            <td>${ui.formatDate(id.created_at)}</td>
            <td class="action-buttons">
                <button onclick="viewIdentity(${id.anchor_id})">View</button>
                <button onclick="exportIdentity(${id.anchor_id})">Export</button>
                <button onclick="viewTrustHistory(${id.anchor_id})">History</button>
            </td>
        </tr>
    `).join('');
}

function displayVerifications(verifications) {
    const tbody = document.querySelector('#verificationsTable tbody');
    tbody.innerHTML = verifications.map(v => `
        <tr>
            <td>${v.verification_id}</td>
            <td>${v.anchor_id}</td>
            <td>${v.platform_name}</td>
            <td><a href="${v.profile_url}" target="_blank">${ui.shortenUrl(v.profile_url)}</a></td>
            <td>${ui.formatDate(v.verified_at)}</td>
            <td>${ui.trustBadge(v.trust_score)}</td>
        </tr>
    `).join('');
}

function displayConsistencyChecks(checks) {
    const tbody = document.querySelector('#consistencyTable tbody');
    tbody.innerHTML = checks.map(c => `
        <tr>
            <td>${c.check_id}</td>
            <td>${c.user_group}</td>
            <td>${c.platform_a}</td>
            <td>${c.platform_b}</td>
            <td>${ui.trustBadge(c.consistency_score)}</td>
            <td>${ui.formatDate(c.checked_at)}</td>
        </tr>
    `).join('');
}

function displayTrustHistory(anchorId, history, currentScore) {
    const modal = document.getElementById('historyModal');
    const content = document.getElementById('historyContent');
    
    content.innerHTML = `
        <h3>Trust Score History - Identity #${anchorId}</h3>
        <p><strong>Current Score:</strong> ${ui.trustBadge(currentScore)}</p>
        <table>
            <thead>
                <tr>
                    <th>Event Type</th>
                    <th>Platform</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                ${history.map(h => `
                    <tr>
                        <td>${h.event_type}</td>
                        <td>${h.platform || 'N/A'}</td>
                        <td>${ui.formatDate(h.time_stamp)}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;
    modal.style.display = 'block';
}