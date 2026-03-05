from flask import Flask, jsonify
from flask_cors import CORS
from config import API_HOST, API_PORT, DEBUG
import routes

app = Flask(__name__)

# ── CORS ───────────────────────────────────────────────────────────────────────
# Only allow requests from your actual frontend origins.
# Add or remove origins here as needed (e.g. when you deploy).
CORS(app, resources={r"/api/*": {
    "origins": [
        "http://localhost:3000",     # React dev server (if used later)
        "http://localhost:5500",     # VS Code Live Server
        "http://127.0.0.1:5500",    # VS Code Live Server (alternate)
        "http://localhost:5000",     # Flask serving its own frontend
        "null"                       # Opening HTML file directly in browser
    ],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# ── Routes ─────────────────────────────────────────────────────────────────────

# Public routes (no token required)
app.add_url_rule('/api/register', 'register', routes.register, methods=['POST'])
app.add_url_rule('/api/login',    'login',    routes.login,    methods=['POST'])
app.add_url_rule('/api/health',   'health',   routes.health_check, methods=['GET'])

# Protected routes (JWT required — wrapped with token_required in routes)
from auth import token_required

app.add_url_rule('/api/statistics',                        'statistics',        token_required(routes.get_statistics),        methods=['GET'])
app.add_url_rule('/api/identity',                          'create_identity',   token_required(routes.create_identity),       methods=['POST'])
app.add_url_rule('/api/identities',                        'identities',        token_required(routes.get_identities),        methods=['GET'])
app.add_url_rule('/api/identities/search',                 'search',            token_required(routes.search_identities),     methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>',          'identity_details',  token_required(routes.get_identity_details),  methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/export',   'export',            token_required(routes.export_identity),       methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/history',  'history',           token_required(routes.get_trust_history),     methods=['GET'])
app.add_url_rule('/api/verification',                      'add_verification',  token_required(routes.add_verification),      methods=['POST'])
app.add_url_rule('/api/verifications',                     'verifications',     token_required(routes.get_verifications),     methods=['GET'])
app.add_url_rule('/api/consistency-check',                 'consistency_check', token_required(routes.run_consistency_check), methods=['POST'])
app.add_url_rule('/api/consistency-checks',                'consistency_checks',token_required(routes.get_consistency_checks),methods=['GET'])
app.add_url_rule('/api/reputation-event',                  'reputation_event',  token_required(routes.log_reputation_event),  methods=['POST'])
app.add_url_rule('/api/reputation-events',                 'reputation_events', token_required(routes.get_reputation_events), methods=['GET'])

# ── Error Handlers ─────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

# ── Entry Point ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("Cross-Platform Digital Identity Verifier")
    print("=" * 60)
    print(f"Server: http://localhost:{API_PORT}")
    print(f"API:    http://localhost:{API_PORT}/api/")
    print("\nSetup checklist:")
    print("  update your database password in config.py")
    print("  run database_schema.sql in the repo to sync")
    print("  keep this terminal open")
    print("=" * 60)

    app.run(debug=DEBUG, host=API_HOST, port=API_PORT)