from flask import Flask, jsonify
from flask_cors import CORS
from config import API_HOST, API_PORT, DEBUG
import routes
import oauth

app = Flask(__name__)

# ── CORS ───────────────────────────────────────────────────────────────────────
CORS(app, resources={r"/api/*": {
    "origins": [
        "http://localhost:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:5000",
        "null"
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# ── Auth routes (public) ───────────────────────────────────────────────────────
app.add_url_rule('/api/register', 'register', routes.register,     methods=['POST'])
app.add_url_rule('/api/login',    'login',    routes.login,         methods=['POST'])
app.add_url_rule('/api/health',   'health',   routes.health_check,  methods=['GET'])

# ── OAuth routes (public — browser redirects, no JWT header possible) ──────────
app.add_url_rule('/api/oauth/github',            'github_login',    oauth.github_login,    methods=['GET'])
app.add_url_rule('/api/oauth/github/callback',   'github_callback', oauth.github_callback, methods=['GET'])
app.add_url_rule('/api/oauth/google',            'google_login',    oauth.google_login,    methods=['GET'])
app.add_url_rule('/api/oauth/google/callback',   'google_callback', oauth.google_callback, methods=['GET'])

# ── Protected routes (JWT required) ───────────────────────────────────────────
from auth import token_required

app.add_url_rule('/api/oauth/verifications',                   'oauth_verifications', token_required(oauth.get_oauth_verifications), methods=['GET'])
app.add_url_rule('/api/statistics',                            'statistics',          token_required(routes.get_statistics),          methods=['GET'])
app.add_url_rule('/api/identity',                              'create_identity',     token_required(routes.create_identity),         methods=['POST'])
app.add_url_rule('/api/identities',                            'identities',          token_required(routes.get_identities),          methods=['GET'])
app.add_url_rule('/api/identities/search',                     'search',              token_required(routes.search_identities),        methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>',              'identity_details',    token_required(routes.get_identity_details),     methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/export',       'export',              token_required(routes.export_identity),          methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/history',      'history',             token_required(routes.get_trust_history),        methods=['GET'])
app.add_url_rule('/api/verification',                          'add_verification',    token_required(routes.add_verification),         methods=['POST'])
app.add_url_rule('/api/verifications',                         'verifications',       token_required(routes.get_verifications),        methods=['GET'])
app.add_url_rule('/api/consistency-check',                     'consistency_check',   token_required(routes.run_consistency_check),    methods=['POST'])
app.add_url_rule('/api/consistency-checks',                    'consistency_checks',  token_required(routes.get_consistency_checks),   methods=['GET'])
app.add_url_rule('/api/reputation-event',                      'reputation_event',    token_required(routes.log_reputation_event),     methods=['POST'])
app.add_url_rule('/api/reputation-events',                     'reputation_events',   token_required(routes.get_reputation_events),    methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/qr',  'qr_code',     token_required(routes.get_qr_code),    methods=['GET'])
app.add_url_rule('/api/verify-claim',                  'verify_claim', token_required(routes.verify_claim),   methods=['POST'])

# ── Error handlers ─────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("Cross-Platform Digital Identity Verifier")
    print("=" * 60)
    print(f"Server: http://localhost:{API_PORT}")
    print(f"API:    http://localhost:{API_PORT}/api/")
    print("=" * 60)
    app.run(debug=DEBUG, host=API_HOST, port=API_PORT)