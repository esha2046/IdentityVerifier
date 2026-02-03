const API_URL = 'http://localhost:5000/api';

const api = {
    // Statistics
    getStatistics: () => 
        fetch(`${API_URL}/statistics`).then(r => r.json()),
    
    // Identities
    createIdentity: () => 
        fetch(`${API_URL}/identity`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        }).then(r => r.json()),
    
    getIdentities: () => 
        fetch(`${API_URL}/identities`).then(r => r.json()),
    
    searchIdentities: (term) => 
        fetch(`${API_URL}/identities/search?q=${encodeURIComponent(term)}`).then(r => r.json()),
    
    getIdentityDetails: (id) => 
        fetch(`${API_URL}/identity/${id}`).then(r => r.json()),
    
    exportIdentity: (id) => 
        fetch(`${API_URL}/identity/${id}/export`).then(r => r.json()),
    
    getTrustHistory: (id) => 
        fetch(`${API_URL}/identity/${id}/history`).then(r => r.json()),
    
    // Verifications
    addVerification: (data) =>
        fetch(`${API_URL}/verification`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(r => r.json()),
    
    getVerifications: () => 
        fetch(`${API_URL}/verifications`).then(r => r.json()),
    
    // Consistency Checks
    runConsistencyCheck: (data) =>
        fetch(`${API_URL}/consistency-check`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(r => r.json()),
    
    getConsistencyChecks: () => 
        fetch(`${API_URL}/consistency-checks`).then(r => r.json()),
    
    // Reputation Events
    logEvent: (data) =>
        fetch(`${API_URL}/reputation-event`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(r => r.json()),
    
    // Health Check
    healthCheck: () =>
        fetch(`${API_URL}/health`).then(r => r.json())
};