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
        const tooltip = 'How reliable this identity anchor is, based on successful verifications and events.';
        return `<span class="trust-score ${cls}" title="${tooltip}">${score}</span>`;
    },

    consistencyBadge(score) {
        const cls = score >= 75 ? 'score-high' : score >= 50 ? 'score-medium' : 'score-low';
        const tooltip = 'How similar this identity looks across the two selected platforms.';
        return `<span class="trust-score ${cls}" title="${tooltip}">${score}</span>`;
    },

    formatDate(dateString) {
        return new Date(dateString).toLocaleString();
    },

    relativeTime(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now - date;
        const diffSecs = Math.floor(diffMs / 1000);
        const diffMins = Math.floor(diffSecs / 60);
        const diffHours = Math.floor(diffMins / 60);
        const diffDays = Math.floor(diffHours / 24);
        const diffMonths = Math.floor(diffDays / 30);
        const diffYears = Math.floor(diffDays / 365);

        if (diffSecs < 60) return 'Just now';
        if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`;
        if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
        if (diffDays < 30) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
        if (diffMonths < 12) return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
        return `${diffYears} year${diffYears > 1 ? 's' : ''} ago`;
    },

    platformIcon(platform) {
        const icons = {
            'Instagram': '📷',
            'LinkedIn': '💼',
            'X': '🐦',
            'Twitter': '🐦',
            'Facebook': '👥',
            'GitHub': '💻'
        };
        return icons[platform] || '🔗';
    },

    shortenUrl(url, max = 40) {
        return url.length > max ? url.substring(0, max) + '...' : url;
    },

    copyToClipboard(text, successMessage = 'Copied to clipboard!') {
        navigator.clipboard.writeText(text).then(() => {
            // Show temporary toast
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = successMessage;
            document.body.appendChild(toast);
            setTimeout(() => {
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                    setTimeout(() => toast.remove(), 300);
                }, 2000);
            }, 10);
        }).catch(err => {
            console.error('Failed to copy:', err);
        });
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

    showLoading(elementId, show = true) {
        const el = document.getElementById(elementId);
        if (!el) return;
        if (show) {
            el.innerHTML = '<div class="loading-spinner"></div><span>Loading...</span>';
            el.className = 'loading-state';
            el.style.display = 'flex';
        } else {
            el.style.display = 'none';
        }
    },

    showTab(tabName) {
        document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.getElementById(tabName).classList.add('active');
        event.target.classList.add('active');
        
        if (tabName === 'identities') loadIdentities();
        if (tabName === 'verifications') loadVerifications();
        if (tabName === 'consistency') loadConsistencyChecks();
    },

    paginate(items, page = 1, perPage = 10) {
        const start = (page - 1) * perPage;
        const end = start + perPage;
        return {
            data: items.slice(start, end),
            currentPage: page,
            totalPages: Math.ceil(items.length / perPage),
            totalItems: items.length,
            hasNext: end < items.length,
            hasPrev: page > 1
        };
    },

    renderPagination(containerId, pagination, onPageChange) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        if (pagination.totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '<div class="pagination">';
        
        // Previous button
        html += `<button class="page-btn" ${!pagination.hasPrev ? 'disabled' : ''} onclick="${onPageChange}(${pagination.currentPage - 1})">‹ Prev</button>`;
        
        // Page numbers
        const maxVisible = 5;
        let startPage = Math.max(1, pagination.currentPage - Math.floor(maxVisible / 2));
        let endPage = Math.min(pagination.totalPages, startPage + maxVisible - 1);
        
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }
        
        if (startPage > 1) {
            html += `<button class="page-btn" onclick="${onPageChange}(1)">1</button>`;
            if (startPage > 2) html += '<span class="page-ellipsis">...</span>';
        }
        
        for (let i = startPage; i <= endPage; i++) {
            html += `<button class="page-btn ${i === pagination.currentPage ? 'active' : ''}" onclick="${onPageChange}(${i})">${i}</button>`;
        }
        
        if (endPage < pagination.totalPages) {
            if (endPage < pagination.totalPages - 1) html += '<span class="page-ellipsis">...</span>';
            html += `<button class="page-btn" onclick="${onPageChange}(${pagination.totalPages})">${pagination.totalPages}</button>`;
        }
        
        // Next button
        html += `<button class="page-btn" ${!pagination.hasNext ? 'disabled' : ''} onclick="${onPageChange}(${pagination.currentPage + 1})">Next ›</button>`;
        
        html += `<span class="page-info">Showing ${((pagination.currentPage - 1) * 10) + 1}-${Math.min(pagination.currentPage * 10, pagination.totalItems)} of ${pagination.totalItems}</span>`;
        html += '</div>';
        
        container.innerHTML = html;
    }
};

// Pagination state
let identitiesPage = 1;
let verificationsPage = 1;
let consistencyPage = 1;
let allIdentities = [];
let allVerifications = [];
let allConsistencyChecks = [];

// Display functions
function displayIdentities(identities, page = 1) {
    const tbody = document.querySelector('#identitiesTable tbody');
    if (!identities || identities.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="no-data">No identities found. Create your first identity anchor above!</td></tr>`;
        document.getElementById('identitiesPagination').innerHTML = '';
        return;
    }
    
    allIdentities = identities;
    identitiesPage = page;
    const pagination = ui.paginate(identities, page, 10);
    
    tbody.innerHTML = pagination.data.map(id => `
        <tr>
            <td>${id.anchor_id}</td>
            <td>
                <span class="copyable-key" onclick="ui.copyToClipboard('${id.user_pub_key}', 'Public key copied!')" title="Click to copy full key">
                    ${id.user_pub_key.substring(0, 40)}...
                    <span class="copy-icon">📋</span>
                </span>
            </td>
            <td>${ui.trustBadge(id.trust_score)}</td>
            <td title="${ui.formatDate(id.created_at)}">${ui.relativeTime(id.created_at)}</td>
            <td class="action-buttons">
                <button onclick="viewIdentity(${id.anchor_id})">View</button>
                <button onclick="exportIdentity(${id.anchor_id})">Export</button>
                <button onclick="viewTrustHistory(${id.anchor_id})">History</button>
            </td>
        </tr>
    `).join('');
    
    ui.renderPagination('identitiesPagination', pagination, 'goToIdentitiesPage');
}

function goToIdentitiesPage(page) {
    displayIdentities(allIdentities, page);
}

function displayVerifications(verifications, page = 1) {
    const tbody = document.querySelector('#verificationsTable tbody');
    if (!verifications || verifications.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="no-data">No verifications found. Add your first platform verification above!</td></tr>`;
        document.getElementById('verificationsPagination').innerHTML = '';
        return;
    }
    
    allVerifications = verifications;
    verificationsPage = page;
    const pagination = ui.paginate(verifications, page, 10);
    
    tbody.innerHTML = pagination.data.map(v => `
        <tr>
            <td>${v.verification_id}</td>
            <td>${v.anchor_id}</td>
            <td>
                <span class="platform-badge">
                    <span class="platform-icon">${ui.platformIcon(v.platform_name)}</span>
                    ${v.platform_name}
                </span>
            </td>
            <td><a href="${v.profile_url}" target="_blank">${ui.shortenUrl(v.profile_url)}</a></td>
            <td title="${ui.formatDate(v.verified_at)}">${ui.relativeTime(v.verified_at)}</td>
            <td>${ui.trustBadge(v.trust_score)}</td>
        </tr>
    `).join('');
    
    ui.renderPagination('verificationsPagination', pagination, 'goToVerificationsPage');
}

function goToVerificationsPage(page) {
    displayVerifications(allVerifications, page);
}

function displayConsistencyChecks(checks, page = 1) {
    const tbody = document.querySelector('#consistencyTable tbody');
    if (!checks || checks.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="no-data">No consistency checks found. Run your first check above!</td></tr>`;
        document.getElementById('consistencyPagination').innerHTML = '';
        return;
    }
    
    allConsistencyChecks = checks;
    consistencyPage = page;
    const pagination = ui.paginate(checks, page, 10);
    
    tbody.innerHTML = pagination.data.map(c => `
        <tr>
            <td>${c.check_id}</td>
            <td>${c.user_group}</td>
            <td>
                <span class="platform-badge">
                    <span class="platform-icon">${ui.platformIcon(c.platform_a)}</span>
                    ${c.platform_a}
                </span>
            </td>
            <td>
                <span class="platform-badge">
                    <span class="platform-icon">${ui.platformIcon(c.platform_b)}</span>
                    ${c.platform_b}
                </span>
            </td>
            <td>${ui.consistencyBadge(c.consistency_score)}</td>
            <td title="${ui.formatDate(c.checked_at)}">${ui.relativeTime(c.checked_at)}</td>
        </tr>
    `).join('');
    
    ui.renderPagination('consistencyPagination', pagination, 'goToConsistencyPage');
}

function goToConsistencyPage(page) {
    displayConsistencyChecks(allConsistencyChecks, page);
}

function displayTrustHistory(anchorId, history, currentScore) {
    const modal = document.getElementById('historyModal');
    const content = document.getElementById('historyContent');
    
    const historyRows = history && history.length > 0 
        ? history.map(h => `
            <tr>
                <td>${h.event_type}</td>
                <td>${h.platform || 'N/A'}</td>
                <td title="${ui.formatDate(h.time_stamp)}">${ui.relativeTime(h.time_stamp)}</td>
            </tr>
        `).join('')
        : '<tr><td colspan="3" class="no-data">No history available</td></tr>';
    
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
                ${historyRows}
            </tbody>
        </table>
    `;
    modal.style.display = 'block';
}