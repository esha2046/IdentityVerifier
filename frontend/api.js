const API_URL = 'http://localhost:5000/api';

// Get statistics
function getStatistics() {
    return fetch(`${API_URL}/statistics`).then(response => response.json());
}

// Create new identity
function createIdentity() {
    return fetch(`${API_URL}/identity`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    }).then(response => response.json());
}

// Get all identities
function getIdentities() {
    return fetch(`${API_URL}/identities`).then(response => response.json());
}

// Search identities
function searchIdentities(searchTerm) {
    return fetch(`${API_URL}/identities/search?q=${encodeURIComponent(searchTerm)}`)
        .then(response => response.json());
}

// Get single identity details
function getIdentityDetails(id) {
    return fetch(`${API_URL}/identity/${id}`).then(response => response.json());
}

// Export identity data
function exportIdentity(id) {
    return fetch(`${API_URL}/identity/${id}/export`).then(response => response.json());
}

// Get trust score history
function getTrustHistory(id) {
    return fetch(`${API_URL}/identity/${id}/history`).then(response => response.json());
}

// Add platform verification
function addVerification(data) {
    return fetch(`${API_URL}/verification`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => response.json());
}

// Get all verifications
function getVerifications() {
    return fetch(`${API_URL}/verifications`).then(response => response.json());
}

// Run consistency check
function runConsistencyCheck(data) {
    return fetch(`${API_URL}/consistency-check`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => response.json());
}

// Get all consistency checks
function getConsistencyChecks() {
    return fetch(`${API_URL}/consistency-checks`).then(response => response.json());
}

// Log reputation event
function logReputationEvent(data) {
    return fetch(`${API_URL}/reputation-event`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    }).then(response => response.json());
}

// Health check
function healthCheck() {
    return fetch(`${API_URL}/health`).then(response => response.json());
}