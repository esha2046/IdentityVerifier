// Load and display statistics
async function loadStatistics() {
    try {
        const data = await getStatistics();
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

// Create new identity
async function createIdentity() {
    try {
        const data = await createIdentity();
        if (data.success) {
            showMessage('identityMessage', 'Identity created successfully!', 'success');
            loadIdentities();
            loadStatistics();
        } else {
            showMessage('identityMessage', 'Error: ' + data.error, 'error');
        }
    } catch (error) {
        showMessage('identityMessage', 'Error creating identity', 'error');
    }
}

// Load all identities
async function loadIdentities() {
    try {
        const data = await getIdentities();
        if (data.success) {
            displayIdentities(data.identities);
        }
    } catch (error) {
        console.error('Error loading identities:', error);
    }
}

// Search identities with delay to avoid too many requests
let searchTimer;
async function searchIdentities() {
    clearTimeout(searchTimer);
    
    const searchTerm = document.getElementById('searchBox').value.trim();
    
    if (!searchTerm) {
        loadIdentities();
        return;
    }

    // Wait 300ms before searching
    searchTimer = setTimeout(async () => {
        try {
            const data = await searchIdentities(searchTerm);
            if (data.success) {
                displayIdentities(data.identities);
            }
        } catch (error) {
            console.error('Error searching:', error);
        }
    }, 300);
}

// View identity details
async function viewIdentity(anchorId) {
    try {
        const data = await getIdentityDetails(anchorId);
        if (data.success) {
            const identity = data.identity;
            const verifications = data.verifications;
            const events = data.events;
            
            let message = '=== IDENTITY DETAILS ===\n\n';
            message += `Anchor ID: ${identity.anchor_id}\n`;
            message += `Public Key: ${identity.user_pub_key.substring(0, 50)}...\n`;
            message += `Trust Score: ${identity.trust_score}\n`;
            message += `Created: ${formatDate(identity.created_at)}\n\n`;
            
            message += `--- VERIFICATIONS (${verifications.length}) ---\n`;
            for (let i = 0; i < verifications.length; i++) {
                const v = verifications[i];
                message += `${i + 1}. ${v.platform_name}: ${v.profile_url}\n`;
            }
            
            message += `\n--- EVENTS (${events.length}) ---\n`;
            const recentEvents = events.slice(0, 5);
            for (let i = 0; i < recentEvents.length; i++) {
                const e = recentEvents[i];
                message += `${i + 1}. ${e.event_type} on ${e.platform || 'N/A'}\n`;
            }
            
            alert(message);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading identity details');
    }
}

// Export identity data
async function exportIdentity(anchorId) {
    try {
        const data = await exportIdentity(anchorId);
        if (data.success) {
            const today = new Date().toISOString().split('T')[0];
            const filename = `identity_${anchorId}_export_${today}.json`;
            downloadJSON(data.data, filename);
            showMessage('identityMessage', `✅ Identity ${anchorId} exported!`, 'success');
        } else {
            alert('Error exporting: ' + data.error);
        }
    } catch (error) {
        alert('Error exporting identity');
    }
}

// View trust history
async function viewTrustHistory(anchorId) {
    try {
        const data = await getTrustHistory(anchorId);
        if (data.success) {
            displayTrustHistory(anchorId, data.history, data.current_score);
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        alert('Error loading trust history');
    }
}

// Add verification
async function addVerification(event) {
    event.preventDefault();
    
    const verificationData = {
        anchor_id: document.getElementById('verifyAnchorId').value,
        platform_name: document.getElementById('verifyPlatform').value,
        profile_url: document.getElementById('verifyUrl').value
    };

    try {
        const result = await addVerification(verificationData);
        if (result.success) {
            showMessage('verificationMessage', 'Verification added!', 'success');
            event.target.reset();
            loadVerifications();
            loadStatistics();
        } else {
            showMessage('verificationMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('verificationMessage', 'Error adding verification', 'error');
    }
}

// Load all verifications
async function loadVerifications() {
    try {
        const data = await getVerifications();
        if (data.success) {
            displayVerifications(data.verifications);
        }
    } catch (error) {
        console.error('Error loading verifications:', error);
    }
}

// Run consistency check
async function runConsistencyCheck(event) {
    event.preventDefault();
    
    const checkData = {
        user_group: document.getElementById('userGroup').value,
        platform_a: document.getElementById('platformA').value,
        platform_b: document.getElementById('platformB').value
    };

    try {
        const result = await runConsistencyCheck(checkData);
        if (result.success) {
            showMessage('consistencyMessage', 'Consistency check completed!', 'success');
            event.target.reset();
            loadConsistencyChecks();
            loadStatistics();
        } else {
            showMessage('consistencyMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('consistencyMessage', 'Error running check', 'error');
    }
}

// Load all consistency checks
async function loadConsistencyChecks() {
    try {
        const data = await getConsistencyChecks();
        if (data.success) {
            displayConsistencyChecks(data.checks);
        }
    } catch (error) {
        console.error('Error loading checks:', error);
    }
}

// Log reputation event
async function logEvent(event) {
    event.preventDefault();
    
    const eventData = {
        anchor_id: document.getElementById('eventAnchorId').value,
        event_type: document.getElementById('eventType').value,
        platform: document.getElementById('eventPlatform').value,
        score_impact: parseFloat(document.getElementById('scoreImpact').value)
    };

    try {
        const result = await logReputationEvent(eventData);
        if (result.success) {
            showMessage('eventMessage', 'Event logged!', 'success');
            event.target.reset();
            loadStatistics();
        } else {
            showMessage('eventMessage', 'Error: ' + result.error, 'error');
        }
    } catch (error) {
        showMessage('eventMessage', 'Error logging event', 'error');
    }
}

// Close history modal
function closeHistoryModal() {
    document.getElementById('historyModal').style.display = 'none';
}

// Click outside modal to close
window.onclick = function(event) {
    const modal = document.getElementById('historyModal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadStatistics();
    loadIdentities();
});