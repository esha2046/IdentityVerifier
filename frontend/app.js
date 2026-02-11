// OAuth Verification Simulation
const oauthSimulator = {
    platformConfigs: {
        'Instagram': {
            logo: '📷',
            color: 'instagram',
            steps: [
                { title: 'Redirecting to Instagram', description: 'Opening OAuth authorization page...', duration: 1500 },
                { title: 'Authenticating User', description: 'Verifying credentials with Instagram...', duration: 2000 },
                { title: 'Requesting Profile Access', description: 'Requesting permission to access profile data...', duration: 1800 },
                { title: 'Fetching Profile Data', description: 'Retrieving profile information...', duration: 2200 },
                { title: 'Validating Profile', description: 'Cross-referencing profile details...', duration: 1500 },
                { title: 'Verifying Identity', description: 'Matching identity anchor with profile...', duration: 2000 }
            ]
        },
        'LinkedIn': {
            logo: '💼',
            color: 'linkedin',
            steps: [
                { title: 'Redirecting to LinkedIn', description: 'Opening OAuth authorization page...', duration: 1500 },
                { title: 'Authenticating User', description: 'Verifying credentials with LinkedIn...', duration: 2000 },
                { title: 'Requesting Profile Access', description: 'Requesting permission to access profile data...', duration: 1800 },
                { title: 'Fetching Profile Data', description: 'Retrieving professional profile...', duration: 2500 },
                { title: 'Validating Profile', description: 'Cross-referencing profile details...', duration: 1500 },
                { title: 'Verifying Identity', description: 'Matching identity anchor with profile...', duration: 2000 }
            ]
        },
        'X': {
            logo: '🐦',
            color: 'twitter',
            steps: [
                { title: 'Redirecting to X', description: 'Opening OAuth authorization page...', duration: 1500 },
                { title: 'Authenticating User', description: 'Verifying credentials with X...', duration: 2000 },
                { title: 'Requesting Profile Access', description: 'Requesting permission to access profile data...', duration: 1800 },
                { title: 'Fetching Profile Data', description: 'Retrieving profile information...', duration: 2000 },
                { title: 'Validating Profile', description: 'Cross-referencing profile details...', duration: 1500 },
                { title: 'Verifying Identity', description: 'Matching identity anchor with profile...', duration: 2000 }
            ]
        },
        'Facebook': {
            logo: '👥',
            color: 'facebook',
            steps: [
                { title: 'Redirecting to Facebook', description: 'Opening OAuth authorization page...', duration: 1500 },
                { title: 'Authenticating User', description: 'Verifying credentials with Facebook...', duration: 2000 },
                { title: 'Requesting Profile Access', description: 'Requesting permission to access profile data...', duration: 1800 },
                { title: 'Fetching Profile Data', description: 'Retrieving profile information...', duration: 2200 },
                { title: 'Validating Profile', description: 'Cross-referencing profile details...', duration: 1500 },
                { title: 'Verifying Identity', description: 'Matching identity anchor with profile...', duration: 2000 }
            ]
        },
        'GitHub': {
            logo: '💻',
            color: 'github',
            steps: [
                { title: 'Redirecting to GitHub', description: 'Opening OAuth authorization page...', duration: 1500 },
                { title: 'Authenticating User', description: 'Verifying credentials with GitHub...', duration: 2000 },
                { title: 'Requesting Profile Access', description: 'Requesting permission to access profile data...', duration: 1800 },
                { title: 'Fetching Profile Data', description: 'Retrieving repository and profile data...', duration: 2500 },
                { title: 'Validating Profile', description: 'Cross-referencing profile details...', duration: 1500 },
                { title: 'Verifying Identity', description: 'Matching identity anchor with profile...', duration: 2000 }
            ]
        }
    },

    async simulateVerification(platform, anchorId, profileUrl) {
        const config = this.platformConfigs[platform] || this.platformConfigs['Instagram'];
        const modal = document.getElementById('oauthModal');
        const stepsContainer = document.getElementById('verificationSteps');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const oauthHeader = document.getElementById('oauthHeader');
        const oauthLogo = document.getElementById('oauthLogo');
        const oauthTitle = document.getElementById('oauthTitle');
        const statusDiv = document.getElementById('verificationStatus');
        const statusIcon = document.getElementById('statusIcon');
        const statusTitle = document.getElementById('statusTitle');
        const statusMessage = document.getElementById('statusMessage');

        // Setup modal
        oauthHeader.className = `oauth-header ${config.color}`;
        oauthLogo.textContent = config.logo;
        oauthTitle.textContent = `Connecting to ${platform}`;
        statusDiv.style.display = 'none';
        stepsContainer.innerHTML = '';
        stepsContainer.style.display = 'block';
        progressFill.style.width = '0%';

        // Create step elements
        config.steps.forEach((step, index) => {
            const stepEl = document.createElement('div');
            stepEl.className = 'verification-step';
            stepEl.id = `step-${index}`;
            stepEl.innerHTML = `
                <div class="step-icon">${index + 1}</div>
                <div class="step-content">
                    <div class="step-title">${step.title}</div>
                    <div class="step-description">${step.description}</div>
                </div>
            `;
            stepsContainer.appendChild(stepEl);
        });

        // Show modal
        modal.classList.add('active');

        // Simulate steps with delays
        let totalDuration = 0;
        const successRate = 1.0; // 85% success rate for realism
        const isSuccess = Math.random() > (1 - successRate);

        for (let i = 0; i < config.steps.length; i++) {
            const step = config.steps[i];
            const stepEl = document.getElementById(`step-${i}`);
            
            // Activate current step
            stepEl.classList.add('active');
            progressText.textContent = step.description;
            
            // Wait for step duration
            await this.delay(step.duration);
            
            // Update progress
            totalDuration += step.duration;
            const progress = ((i + 1) / config.steps.length) * 100;
            progressFill.style.width = `${progress}%`;
            
            // Complete step
            stepEl.classList.remove('active');
            
            // Check for failure (only on last step for dramatic effect)
            if (i === config.steps.length - 1 && !isSuccess) {
                stepEl.classList.add('failed');
                break;
            } else {
                stepEl.classList.add('completed');
            }
        }

        // Final delay before showing result
        await this.delay(500);

        // Show result
        stepsContainer.style.display = 'none';
        statusDiv.style.display = 'block';
        document.getElementById('oauthCloseBtn').style.display = 'block';

        if (isSuccess) {
            statusIcon.className = 'status-icon success';
            statusIcon.textContent = '✓';
            statusTitle.textContent = 'Verification Successful!';
            statusMessage.textContent = `Your ${platform} profile has been successfully verified and linked to Identity Anchor #${anchorId}.`;
            statusTitle.style.color = '#28a745';
        } else {
            statusIcon.className = 'status-icon failure';
            statusIcon.textContent = '✕';
            statusTitle.textContent = 'Verification Failed';
            statusMessage.textContent = `Unable to verify ${platform} profile. Please check your credentials and try again.`;
            statusTitle.style.color = '#dc3545';
        }

        // Auto-close after delay
        await this.delay(3000);
        this.closeModal();

        return isSuccess;
    },

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    closeModal() {
        const modal = document.getElementById('oauthModal');
        modal.classList.remove('active');
        
        // Reset progress
        document.getElementById('progressFill').style.width = '0%';
        document.getElementById('verificationSteps').style.display = 'block';
        document.getElementById('verificationStatus').style.display = 'none';
        document.getElementById('oauthCloseBtn').style.display = 'none';
    }
};

// Close modal on outside click
document.addEventListener('click', (e) => {
    const modal = document.getElementById('oauthModal');
    if (e.target === modal) {
        oauthSimulator.closeModal();
    }
});

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
    const tbody = document.querySelector('#identitiesTable tbody');
    tbody.innerHTML = '<tr><td colspan="5" class="loading-row"><div class="loading-spinner"></div> Loading identities...</td></tr>';
    
    try {
        const data = await api.getIdentities();
        if (data.success) {
            displayIdentities(data.identities);

            // Also populate the Consistency Check anchor selector so users must pick a real identity
            const select = document.getElementById('consistencyAnchorId');
            if (select) {
                const previousValue = select.value;
                select.innerHTML = '<option value=\"\">Select Anchor</option>' +
                    data.identities.map(id => `
                        <option value="${id.anchor_id}">
                            #${id.anchor_id} - ${id.user_pub_key.substring(0, 24)}...
                        </option>
                    `).join('');
                // Preserve selection if it still exists
                if (previousValue && data.identities.some(id => String(id.anchor_id) === previousValue)) {
                    select.value = previousValue;
                }
            }
        } else {
            tbody.innerHTML = `<tr><td colspan="5" class="no-data">Error loading identities: ${data.error || 'Unknown error'}</td></tr>`;
        }
    } catch (error) {
        console.error('Error loading identities:', error);
        tbody.innerHTML = `<tr><td colspan="5" class="no-data">Error loading identities: ${error.message}</td></tr>`;
    }
}


async function viewIdentity(anchorId) {
    const modal = document.getElementById('identityDetailsModal');
    const content = document.getElementById('identityDetailsContent');
    
    // Show loading
    content.innerHTML = '<div class="loading-spinner"></div><p>Loading identity details...</p>';
    modal.style.display = 'block';
    
    try {
        console.log('Viewing identity:', anchorId);
        const data = await api.getIdentityDetails(anchorId);
        if (data.success) {
            const { identity, verifications, events } = data;
            
            const verificationsHtml = verifications && verifications.length > 0
                ? verifications.map((v, i) => `
                    <div class="verification-item">
                        <span class="platform-badge">
                            <span class="platform-icon">${ui.platformIcon(v.platform_name)}</span>
                            ${v.platform_name}
                        </span>
                        <a href="${v.profile_url}" target="_blank">${ui.shortenUrl(v.profile_url, 50)}</a>
                    </div>
                `).join('')
                : '<p class="no-data">No verifications found.</p>';
            
            const eventsHtml = events && events.length > 0
                ? events.slice(0, 10).map((e, i) => `
                    <div class="event-item">
                        <span class="event-type">${e.event_type}</span>
                        <span class="event-platform">${e.platform || 'N/A'}</span>
                        <span class="event-time">${ui.relativeTime(e.time_stamp || e.created_at || new Date())}</span>
                    </div>
                `).join('')
                : '<p class="no-data">No events found.</p>';
            
            content.innerHTML = `
                <div class="identity-details">
                    <div class="detail-section">
                        <h3>Basic Information</h3>
                        <div class="detail-row">
                            <strong>Anchor ID:</strong> <span>${identity.anchor_id}</span>
                        </div>
                        <div class="detail-row">
                            <strong>Public Key:</strong> 
                            <span class="copyable-key" onclick="ui.copyToClipboard('${identity.user_pub_key}', 'Public key copied!')" title="Click to copy">
                                ${identity.user_pub_key ? identity.user_pub_key.substring(0, 60) + '...' : 'N/A'}
                                <span class="copy-icon">📋</span>
                            </span>
                        </div>
                        <div class="detail-row">
                            <strong>Trust Score:</strong> ${ui.trustBadge(identity.trust_score)}
                        </div>
                        <div class="detail-row">
                            <strong>Created:</strong> <span title="${ui.formatDate(identity.created_at)}">${ui.relativeTime(identity.created_at)}</span>
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3>Platform Verifications (${verifications ? verifications.length : 0})</h3>
                        <div class="verifications-list">
                            ${verificationsHtml}
                        </div>
                    </div>
                    
                    <div class="detail-section">
                        <h3>Recent Events (${events ? events.length : 0})</h3>
                        <div class="events-list">
                            ${eventsHtml}
                        </div>
                    </div>
                </div>
            `;
        } else {
            content.innerHTML = `<p class="error-message">Error: ${data.error || 'Unknown error'}</p>`;
        }
    } catch (error) {
        console.error('Error loading identity details:', error);
        content.innerHTML = `<p class="error-message">Error loading identity details: ${error.message}</p>`;
    }
}

function closeIdentityModal() {
    document.getElementById('identityDetailsModal').style.display = 'none';
}

async function exportIdentity(anchorId) {
    try {
        console.log('Exporting identity:', anchorId);
        const data = await api.exportIdentity(anchorId);
        if (data.success) {
            const filename = `identity_${anchorId}_export_${new Date().toISOString().split('T')[0]}.json`;
            ui.downloadJSON(data.data, filename);
            ui.showMessage('identityMessage', `✓ Identity ${anchorId} exported successfully!`, 'success');
        } else {
            alert('Error exporting: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error exporting identity:', error);
        alert('Error exporting identity: ' + error.message);
    }
}

async function viewTrustHistory(anchorId) {
    try {
        console.log('Loading trust history for identity:', anchorId);
        const data = await api.getTrustHistory(anchorId);
        if (data.success) {
            displayTrustHistory(anchorId, data.history || [], data.current_score || 0);
        } else {
            alert('Error: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error loading trust history:', error);
        alert('Error loading trust history: ' + error.message);
    }
}

// Verification operations
async function addVerification(event) {
    event.preventDefault();
    
    const anchorId = document.getElementById('verifyAnchorId').value;
    const platform = document.getElementById('verifyPlatform').value;
    const profileUrl = document.getElementById('verifyUrl').value;

    if (!anchorId || !platform || !profileUrl) {
        ui.showMessage('verificationMessage', 'Please fill in all fields', 'error');
        return;
    }

    // Show OAuth simulation
    const isSuccess = await oauthSimulator.simulateVerification(platform, anchorId, profileUrl);

    // Only proceed with API call if simulation was successful
    if (isSuccess) {
        const data = {
            anchor_id: anchorId,
            platform_name: platform,
            profile_url: profileUrl
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
    } else {
        ui.showMessage('verificationMessage', 'Verification failed. Please try again.', 'error');
    }
}

async function loadVerifications() {
    const tbody = document.querySelector('#verificationsTable tbody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading-row"><div class="loading-spinner"></div> Loading verifications...</td></tr>';
    
    try {
        const data = await api.getVerifications();
        if (data.success) {
            displayVerifications(data.verifications);
        } else {
            tbody.innerHTML = `<tr><td colspan="6" class="no-data">Error loading verifications: ${data.error || 'Unknown error'}</td></tr>`;
        }
    } catch (error) {
        console.error('Error loading verifications:', error);
        tbody.innerHTML = `<tr><td colspan="6" class="no-data">Error loading verifications: ${error.message}</td></tr>`;
    }
}

// Consistency check operations
async function runConsistencyCheck(event) {
    event.preventDefault();
    
    const anchorId = document.getElementById('consistencyAnchorId').value;
    const platformA = document.getElementById('platformA').value;
    const platformB = document.getElementById('platformB').value;

    if (!anchorId || !platformA || !platformB) {
        ui.showMessage('consistencyMessage', 'Please fill in all fields', 'error');
        return;
    }

    const data = {
        identity_anchor: anchorId,
        platform_a: platformA,
        platform_b: platformB
    };

    try {
        const result = await api.runConsistencyCheck(data);
        if (result.success) {
            ui.showMessage('consistencyMessage', 'Consistency check completed!', 'success');
            event.target.reset();
            loadConsistencyChecks();
            loadStatistics();
        } else {
            ui.showMessage('consistencyMessage', 'Error: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Consistency check error:', error);
        ui.showMessage('consistencyMessage', 'Error running check: ' + error.message, 'error');
    }
}

async function loadConsistencyChecks() {
    const tbody = document.querySelector('#consistencyTable tbody');
    tbody.innerHTML = '<tr><td colspan="6" class="loading-row"><div class="loading-spinner"></div> Loading consistency checks...</td></tr>';
    
    try {
        const data = await api.getConsistencyChecks();
        if (data.success) {
            displayConsistencyChecks(data.checks);
        } else {
            tbody.innerHTML = `<tr><td colspan="6" class="no-data">Error loading checks: ${data.error || 'Unknown error'}</td></tr>`;
        }
    } catch (error) {
        console.error('Error loading consistency checks:', error);
        tbody.innerHTML = `<tr><td colspan="6" class="no-data">Error loading checks: ${error.message}</td></tr>`;
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
    const historyModal = document.getElementById('historyModal');
    const identityModal = document.getElementById('identityDetailsModal');
    if (event.target == historyModal) {
        historyModal.style.display = 'none';
    }
    if (event.target == identityModal) {
        identityModal.style.display = 'none';
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
    loadIdentities();
});