const API_URL = 'https://identity-verifier-tt63.onrender.com/api';

// Attach JWT token to every request automatically
function authHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    };
}

// Handle 401 responses globally — redirect to login if token expired
async function apiFetch(url, options = {}) {
    const res = await fetch(url, {
        ...options,
        headers: { ...authHeaders(), ...(options.headers || {}) }
    });
    if (res.status === 401) {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('jwt_expiry');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
        return;
    }
    return res.json();
}

const api = {
    // Statistics
    getStatistics: () => apiFetch(`${API_URL}/statistics`),

    // Identities
    createIdentity: () =>
        apiFetch(`${API_URL}/identity`, { method: 'POST' }),

    getIdentities: () => apiFetch(`${API_URL}/identities`),

    searchIdentities: (term) =>
        apiFetch(`${API_URL}/identities/search?q=${encodeURIComponent(term)}`),

    getIdentityDetails: (id) => apiFetch(`${API_URL}/identity/${id}`),

    exportIdentity: (id) => apiFetch(`${API_URL}/identity/${id}/export`),

    getTrustHistory: (id) => apiFetch(`${API_URL}/identity/${id}/history`),

    getQrCode: (id) => apiFetch(`${API_URL}/identity/${id}/qr`),

    // Verifications
    addVerification: (data) =>
        apiFetch(`${API_URL}/verification`, {
            method: 'POST',
            body: JSON.stringify(data)
        }),

    getVerifications: () => apiFetch(`${API_URL}/verifications`),

    // Consistency Checks
    runConsistencyCheck: (data) =>
        apiFetch(`${API_URL}/consistency-check`, {
            method: 'POST',
            body: JSON.stringify(data)
        }),

    getConsistencyChecks: () => apiFetch(`${API_URL}/consistency-checks`),

    getConsistencyReport: (checkId) => apiFetch(`${API_URL}/consistency-check/${checkId}/report`),

    storeOnBlockchain: (verificationId, anchorId, platform, profileUrl) =>
        apiFetch(`${API_URL}/blockchain/store`, {
            method: 'POST',
            body: JSON.stringify({
                verification_id: verificationId,
                anchor_id:       anchorId,
                platform:        platform,
                profile_url:     profileUrl
            })
        }),

    // Reputation Events
    logEvent: (data) =>
        apiFetch(`${API_URL}/reputation-event`, {
            method: 'POST',
            body: JSON.stringify(data)
        }),

    getReputationEvents: () => apiFetch(`${API_URL}/reputation-events`),

    // Health Check
    healthCheck: () => apiFetch(`${API_URL}/health`)
};