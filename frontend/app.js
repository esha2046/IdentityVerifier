async function loadStatistics() {
    try {
        const data = await api.getStatistics();
        if (data.success) {
            const stats = data.statistics;
            document.getElementById('totalIdentities').textContent = stats.total_identities;
            document.getElementById('totalVerifications').textContent = stats.total_verifications;
            document.getElementById('avgTrustScore').textContent = stats.avg_trust_score.toFixed(1);
            document.getElementById('avgConsistency').textContent = stats.avg_consistency_score.toFixed(1);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Identity operations
async function createIdentity() {
    try {
        const data = await api.createIdentity();
        if (data.success) {
            ui.showMessage('identityMessage', 'Identity created successfully!', 'success');
            loadIdentities();
            loadStatistics();
        } else {
            ui.showMessage('identityMessage', 'Error: ' + data.error, 'error');
        }
    } catch (error) {
        ui.showMessage('identityMessage', 'Error creating identity', 'error');
    }
}

async function loadIdentities() {
    try {
        const data = await api.getIdentities();
        if (data.success) displayIdentities(data.identities);
    } catch (error) {
        console.error('Error loading identities:', error);
    }
}


async function viewIdentity(anchorId) {
    try {
        const data = await api.getIdentityDetails(anchorId);
        if (data.success) {
            const { identity, verifications, events } = data;
            
            let msg = `=== IDENTITY DETAILS ===\n\n`;
            msg += `Anchor ID: ${identity.anchor_id}\n`;
            msg += `Public Key: ${identity.user_pub_key.substring(0, 50)}...\n`;
            msg += `Trust Score: ${identity.trust_score}\n`;
            msg += `Created: ${ui.formatDate(identity.created_at)}\n\n`;
            
            msg += `--- VERIFICATIONS (${verifications.length}) ---\n`;
            verifications.forEach((v, i) => {
                msg += `${i+1}. ${v.platform_name}: ${v.profile_url}\n`;
            });
            
            msg += `\n--- EVENTS (${events.length}) ---\n`;
            events.slice(0, 5).forEach((e, i) => {
                msg += `${i+1}. ${e.event_type} on ${e.platform || 'N/A'}\n`;
            });
            
            alert(msg);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading identity details');
    }
}

async function exportIdentity(anchorId) {
    try {
        const data = await api.exportIdentity(anchorId);
        if (data.success) {
            const filename = `identity_${anchorId}_export_${new Date().toISOString().split('T')[0]}.json`;
            ui.downloadJSON(data.data, filename);
            ui.showMessage('identityMessage', `âœ… Identity ${anchorId} exported successfully!`, 'success');
        } else {
            alert('Error exporting: ' + data.error);
        }
    } catch (error) {
        alert('Error exporting identity');
    }
}

async function viewTrustHistory(anchorId) {
    try {
        const data = await api.getTrustHistory(anchorId);
        if (data.success) {
            displayTrustHistory(anchorId, data.history, data.current_score);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading trust history');
    }
}

// Verification operations
async function addVerification(event) {
    event.preventDefault();
    
    const data = {
        anchor_id: document.getElementById('verifyAnchorId').value,
        platform_name: document.getElementById('verifyPlatform').value,
        profile_url: document.getElementById('verifyUrl').value
    };

    try {
        const result = await api.addVerification(data);
        if (result.success) {
            ui.showMessage('verificationMessage', 'Verification added successfully!', 'success');
            event.target.reset();
            loadVerifications();
            loadStatistics();
        } else {
            ui.showMessage('verificationMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        ui.showMessage('verificationMessage', 'Error adding verification', 'error');
    }
}

async function loadVerifications() {
    try {
        const data = await api.getVerifications();
        if (data.success) displayVerifications(data.verifications);
    } catch (error) {
        console.error('Error loading verifications:', error);
    }
}

// Consistency check operations
async function runConsistencyCheck(event) {
    event.preventDefault();
    
    const data = {
        user_group: document.getElementById('userGroup').value,
        platform_a: document.getElementById('platformA').value,
        platform_b: document.getElementById('platformB').value
    };

    try {
        const result = await api.runConsistencyCheck(data);
        if (result.success) {
            ui.showMessage('consistencyMessage', 'Consistency check completed!', 'success');
            event.target.reset();
            loadConsistencyChecks();
            loadStatistics();
        } else {
            ui.showMessage('consistencyMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        ui.showMessage('consistencyMessage', 'Error running check', 'error');
    }
}

async function loadConsistencyChecks() {
    try {
        const data = await api.getConsistencyChecks();
        if (data.success) displayConsistencyChecks(data.checks);
    } catch (error) {
        console.error('Error loading consistency checks:', error);
    }
}

// Reputation event operations
async function logEvent(event) {
    event.preventDefault();
    
    const data = {
        anchor_id: document.getElementById('eventAnchorId').value,
        event_type: document.getElementById('eventType').value,
        platform: document.getElementById('eventPlatform').value,
        score_impact: parseFloat(document.getElementById('scoreImpact').value)
    };

    try {
        const result = await api.logEvent(data);
        if (result.success) {
            ui.showMessage('eventMessage', 'Event logged successfully!', 'success');
            event.target.reset();
            loadStatistics();
        } else {
            ui.showMessage('eventMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        ui.showMessage('eventMessage', 'Error logging event', 'error');
    }
}

// Modal controls
function closeHistoryModal() {
    document.getElementById('historyModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('historyModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Statistics
async function loadStatistics() {
    try {
        const data = await api.getStatistics();
        if (data.success) {
            const s = data.statistics;
            document.getElementById('totalIdentities').textContent = s.total_identities;
            document.getElementById('totalVerifications').textContent = s.total_verifications;
            document.getElementById('avgTrustScore').textContent = s.avg_trust_score.toFixed(1);
            document.getElementById('avgConsistency').textContent = s.avg_consistency_score.toFixed(1);
        }
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

// Identity operations
async function createIdentity() {
    try {
        const data = await api.createIdentity();
        if (data.success) {
            ui.showMessage('identityMessage', 'Identity created successfully!', 'success');
            loadIdentities();
            loadStatistics();
        } else {
            ui.showMessage('identityMessage', 'Error: ' + data.error, 'error');
        }
    } catch (error) {
        ui.showMessage('identityMessage', 'Error creating identity', 'error');
    }
}

async function loadIdentities() {
    try {
        const data = await api.getIdentities();
        if (data.success) displayIdentities(data.identities);
    } catch (error) {
        console.error('Error loading identities:', error);
    }
}

let searchTimeout;
async function searchIdentities() {
    clearTimeout(searchTimeout);
    const term = document.getElementById('searchBox').value.trim();
    
    if (!term) {
        loadIdentities();
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const data = await api.searchIdentities(term);
            if (data.success) displayIdentities(data.identities);
        } catch (error) {
            console.error('Error searching identities:', error);
        }
    }, 300);
}

async function viewIdentity(anchorId) {
    try {
        const data = await api.getIdentityDetails(anchorId);
        if (data.success) {
            const { identity, verifications, events } = data;
            
            let msg = `=== IDENTITY DETAILS ===\n\n`;
            msg += `Anchor ID: ${identity.anchor_id}\n`;
            msg += `Public Key: ${identity.user_pub_key.substring(0, 50)}...\n`;
            msg += `Trust Score: ${identity.trust_score}\n`;
            msg += `Created: ${ui.formatDate(identity.created_at)}\n\n`;
            
            msg += `--- VERIFICATIONS (${verifications.length}) ---\n`;
            verifications.forEach((v, i) => {
                msg += `${i+1}. ${v.platform_name}: ${v.profile_url}\n`;
            });
            
            msg += `\n--- EVENTS (${events.length}) ---\n`;
            events.slice(0, 5).forEach((e, i) => {
                msg += `${i+1}. ${e.event_type} on ${e.platform || 'N/A'}\n`;
            });
            
            alert(msg);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading identity details');
    }
}

async function exportIdentity(anchorId) {
    try {
        const data = await api.exportIdentity(anchorId);
        if (data.success) {
            const filename = `identity_${anchorId}_export_${new Date().toISOString().split('T')[0]}.json`;
            ui.downloadJSON(data.data, filename);
            ui.showMessage('identityMessage', `âœ… Identity ${anchorId} exported successfully!`, 'success');
        } else {
            alert('Error exporting: ' + data.error);
        }
    } catch (error) {
        alert('Error exporting identity');
    }
}

async function viewTrustHistory(anchorId) {
    try {
        const data = await api.getTrustHistory(anchorId);
        if (data.success) {
            displayTrustHistory(anchorId, data.history, data.current_score);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading trust history');
    }
}

// Verification operations
async function addVerification(event) {
    event.preventDefault();
    
    const data = {
        anchor_id: document.getElementById('verifyAnchorId').value,
        platform_name: document.getElementById('verifyPlatform').value,
        profile_url: document.getElementById('verifyUrl').value
    };

    try {
        const result = await api.addVerification(data);
        if (result.success) {
            ui.showMessage('verificationMessage', 'Verification added successfully!', 'success');
            event.target.reset();
            loadVerifications();
            loadStatistics();
        } else {
            ui.showMessage('verificationMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        ui.showMessage('verificationMessage', 'Error adding verification', 'error');
    }
}

async function loadVerifications() {
    try {
        const data = await api.getVerifications();
        if (data.success) displayVerifications(data.verifications);
    } catch (error) {
        console.error('Error loading verifications:', error);
    }
}

// Consistency check operations
async function runConsistencyCheck(event) {
    event.preventDefault();
    
    const data = {
        user_group: document.getElementById('userGroup').value,
        platform_a: document.getElementById('platformA').value,
        platform_b: document.getElementById('platformB').value
    };

    try {
        const result = await api.runConsistencyCheck(data);
        if (result.success) {
            ui.showMessage('consistencyMessage', 'Consistency check completed!', 'success');
            event.target.reset();
            loadConsistencyChecks();
            loadStatistics();
        } else {
            ui.showMessage('consistencyMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        ui.showMessage('consistencyMessage', 'Error running check', 'error');
    }
}

async function loadConsistencyChecks() {
    try {
        const data = await api.getConsistencyChecks();
        if (data.success) displayConsistencyChecks(data.checks);
    } catch (error) {
        console.error('Error loading consistency checks:', error);
    }
}

// Reputation event operations
async function logEvent(event) {
    event.preventDefault();
    
    const data = {
        anchor_id: document.getElementById('eventAnchorId').value,
        event_type: document.getElementById('eventType').value,
        platform: document.getElementById('eventPlatform').value,
        score_impact: parseFloat(document.getElementById('scoreImpact').value)
    };

    try {
        const result = await api.logEvent(data);
        if (result.success) {
            ui.showMessage('eventMessage', 'Event logged successfully!', 'success');
            event.target.reset();
            loadStatistics();
        } else {
            ui.showMessage('eventMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        ui.showMessage('eventMessage', 'Error logging event', 'error');
    }
}

// Modal controls
function closeHistoryModal() {
    document.getElementById('historyModal').style.display = 'none';
}

window.onclick = function(event) {
    const modal = document.getElementById('historyModal');
    if (event.target == modal) modal.style.display = 'none';
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
    loadIdentities();
});