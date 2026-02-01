// Show success or error message
function showMessage(elementId, message, type) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    element.textContent = message;
    element.className = `message ${type}`;
    element.style.display = 'block';
    
    // Hide after 5 seconds
    setTimeout(() => {
        element.style.display = 'none';
    }, 5000);
}

// Color-coded trust score badge
function getTrustBadge(score) {
    let colorClass = 'score-low';
    if (score >= 75) colorClass = 'score-high';
    else if (score >= 50) colorClass = 'score-medium';
    
    return `<span class="trust-score ${colorClass}">${score}</span>`;
}

// Format date to readable format
function formatDate(dateString) {
    return new Date(dateString).toLocaleString();
}

// Shorten long URLs
function shortenUrl(url, maxLength) {
    if (!maxLength) maxLength = 40;
    if (url.length > maxLength) {
        return url.substring(0, maxLength) + '...';
    }
    return url;
}

// Download data as JSON file
function downloadJSON(data, filename) {
    const jsonText = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonText], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.click();
    
    URL.revokeObjectURL(url);
}

// Switch between tabs
function showTab(tabName) {
    // Hide all sections
    const sections = document.querySelectorAll('.content-section');
    sections.forEach(section => section.classList.remove('active'));
    
    // Remove active from all tabs
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Show selected section
    document.getElementById(tabName).classList.add('active');
    event.target.classList.add('active');
    
    // Load data for the tab
    if (tabName === 'identities') loadIdentities();
    if (tabName === 'verifications') loadVerifications();
    if (tabName === 'consistency') loadConsistencyChecks();
}

// Display identities in table
function displayIdentities(identities) {
    const tableBody = document.querySelector('#identitiesTable tbody');
    
    const rows = identities.map(identity => {
        const shortKey = identity.user_pub_key.substring(0, 40) + '...';
        return `
            <tr>
                <td>${identity.anchor_id}</td>
                <td>${shortKey}</td>
                <td>${getTrustBadge(identity.trust_score)}</td>
                <td>${formatDate(identity.created_at)}</td>
                <td class="action-buttons">
                    <button onclick="viewIdentity(${identity.anchor_id})">View</button>
                    <button onclick="exportIdentity(${identity.anchor_id})">Export</button>
                    <button onclick="viewTrustHistory(${identity.anchor_id})">History</button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = rows.join('');
}

// Display verifications in table
function displayVerifications(verifications) {
    const tableBody = document.querySelector('#verificationsTable tbody');
    
    const rows = verifications.map(v => `
        <tr>
            <td>${v.verification_id}</td>
            <td>${v.anchor_id}</td>
            <td>${v.platform_name}</td>
            <td><a href="${v.profile_url}" target="_blank">${shortenUrl(v.profile_url)}</a></td>
            <td>${formatDate(v.verified_at)}</td>
            <td>${getTrustBadge(v.trust_score)}</td>
        </tr>
    `);
    
    tableBody.innerHTML = rows.join('');
}

// Display consistency checks in table
function displayConsistencyChecks(checks) {
    const tableBody = document.querySelector('#consistencyTable tbody');
    
    const rows = checks.map(check => `
        <tr>
            <td>${check.check_id}</td>
            <td>${check.user_group}</td>
            <td>${check.platform_a}</td>
            <td>${check.platform_b}</td>
            <td>${getTrustBadge(check.consistency_score)}</td>
            <td>${formatDate(check.checked_at)}</td>
        </tr>
    `);
    
    tableBody.innerHTML = rows.join('');
}

// Display trust history in modal
function displayTrustHistory(anchorId, history, currentScore) {
    const modal = document.getElementById('historyModal');
    const content = document.getElementById('historyContent');
    
    const historyRows = history.map(event => `
        <tr>
            <td>${event.event_type}</td>
            <td>${event.platform || 'N/A'}</td>
            <td>${formatDate(event.time_stamp)}</td>
        </tr>
    `);
    
    content.innerHTML = `
        <h3>Trust Score History - Identity #${anchorId}</h3>
        <p><strong>Current Score:</strong> ${getTrustBadge(currentScore)}</p>
        <table>
            <thead>
                <tr>
                    <th>Event Type</th>
                    <th>Platform</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                ${historyRows.join('')}
            </tbody>
        </table>
    `;
    
    modal.style.display = 'block';
}