from flask import Flask, jsonify
from flask_cors import CORS
from config import API_HOST, API_PORT, DEBUG
import routes

app = Flask(__name__)
CORS(app)

# reg routes
app.add_url_rule('/api/statistics', 'statistics', routes.get_statistics, methods=['GET'])
app.add_url_rule('/api/identity', 'create_identity', routes.create_identity, methods=['POST'])
app.add_url_rule('/api/identities', 'identities', routes.get_identities, methods=['GET'])
app.add_url_rule('/api/identities/search', 'search', routes.search_identities, methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>', 'identity_details', routes.get_identity_details, methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/export', 'export', routes.export_identity, methods=['GET'])
app.add_url_rule('/api/identity/<int:anchor_id>/history', 'history', routes.get_trust_history, methods=['GET'])
app.add_url_rule('/api/verification', 'add_verification', routes.add_verification, methods=['POST'])
app.add_url_rule('/api/verifications', 'verifications', routes.get_verifications, methods=['GET'])
app.add_url_rule('/api/consistency-check', 'consistency_check', routes.run_consistency_check, methods=['POST'])
app.add_url_rule('/api/consistency-checks', 'consistency_checks', routes.get_consistency_checks, methods=['GET'])
app.add_url_rule('/api/reputation-event', 'reputation_event', routes.log_reputation_event, methods=['POST'])
app.add_url_rule('/api/health', 'health', routes.health_check, methods=['GET'])

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Cross-Platform Digital Identity Verifier")
    print("=" * 60)
    print(f"Server: http://localhost:{API_PORT}")
    print(f"API: http://localhost:{API_PORT}/api/")
    print("\nSetup checklist:")
    print("update your database password in config.py")
    print("run database_schema.sql in the repo to sync")
    print("keep this terminal open")
    print("=" * 60)
    
    app.run(debug=DEBUG, host=API_HOST, port=API_PORT)