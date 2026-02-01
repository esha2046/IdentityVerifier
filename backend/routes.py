from flask import jsonify, request
from datetime import datetime
import models

def send_success(data):
    return jsonify({'success': True, **data})

def send_error(message, status=400):
    return jsonify({'success': False, 'error': message}), status

# Dashboard statistics
def get_statistics():
    stats, error = models.get_statistics()
    if error:
        return send_error(error, 500)
    
    return send_success({
        'statistics': {
            'total_identities': stats['total_identities'],
            'total_verifications': stats['total_verifications'],
            'avg_trust_score': float(stats['avg_trust']),
            'avg_consistency_score': float(stats['avg_consistency'])
        }
    })

# Create new identity
def create_identity():
    identity, error = models.create_identity()
    if error:
        return send_error(error, 500)
    return send_success({'identity': dict(identity)})

# Get all identities
def get_identities():
    identities, error = models.get_all_identities()
    if error:
        return send_error(error, 500)
    return send_success({'identities': [dict(i) for i in identities]})

# Search identities
def search_identities():
    search_term = request.args.get('q', '')
    identities, error = models.search_identities(search_term)
    if error:
        return send_error(error, 500)
    return send_success({'identities': [dict(i) for i in identities]})

# Get single identity details
def get_identity_details(anchor_id):
    data, error = models.get_identity_details(anchor_id)
    if error:
        status = 404 if 'not found' in error.lower() else 500
        return send_error(error, status)
    
    return send_success({
        'identity': dict(data['identity']),
        'verifications': [dict(v) for v in data['verifications']],
        'events': [dict(e) for e in data['events']]
    })

# Export identity data
def export_identity(anchor_id):
    data, error = models.get_identity_details(anchor_id)
    if error:
        status = 404 if 'not found' in error.lower() else 500
        return send_error(error, status)
    
    return send_success({
        'data': {
            'export_date': datetime.now().isoformat(),
            'identity': dict(data['identity']),
            'verifications': [dict(v) for v in data['verifications']],
            'events': [dict(e) for e in data['events']],
            'statistics': {
                'total_verifications': len(data['verifications']),
                'total_events': len(data['events'])
            }
        }
    })

# Get trust score history
def get_trust_history(anchor_id):
    data, error = models.get_trust_history(anchor_id)
    if error:
        status = 404 if 'not found' in error.lower() else 500
        return send_error(error, status)
    return send_success(data)

# Add platform verification
def add_verification():
    data = request.get_json()
    anchor_id = data.get('anchor_id')
    platform = data.get('platform_name')
    url = data.get('profile_url')
    
    if not anchor_id or not platform or not url:
        return send_error('Missing required fields: anchor_id, platform_name, profile_url')
    
    verification, error = models.create_verification(anchor_id, platform, url)
    if error:
        status = 404 if 'not found' in error.lower() else 500
        return send_error(error, status)
    
    return send_success({'verification': dict(verification)})

# Get all verifications
def get_verifications():
    verifications, error = models.get_all_verifications()
    if error:
        return send_error(error, 500)
    return send_success({'verifications': [dict(v) for v in verifications]})

# Run consistency check
def run_consistency_check():
    data = request.get_json()
    user_group = data.get('user_group')
    platform_a = data.get('platform_a')
    platform_b = data.get('platform_b')
    
    if not user_group or not platform_a or not platform_b:
        return send_error('Missing required fields: user_group, platform_a, platform_b')
    
    check, error = models.create_consistency_check(user_group, platform_a, platform_b)
    if error:
        return send_error(error, 500)
    
    return send_success({'check': dict(check)})

# Get all consistency checks
def get_consistency_checks():
    checks, error = models.get_all_consistency_checks()
    if error:
        return send_error(error, 500)
    return send_success({'checks': [dict(c) for c in checks]})

# Log reputation event
def log_reputation_event():
    data = request.get_json()
    anchor_id = data.get('anchor_id')
    event_type = data.get('event_type')
    platform = data.get('platform', '')
    score_change = data.get('score_impact', 0)
    
    if not anchor_id or not event_type:
        return send_error('Missing required fields: anchor_id, event_type')
    
    event, error = models.create_reputation_event(anchor_id, event_type, platform, score_change)
    if error:
        status = 404 if 'not found' in error.lower() else 500
        return send_error(error, status)
    
    return send_success({'event': dict(event)})

# Health check
def health_check():
    from database import connect_db
    conn = connect_db()
    if conn:
        conn.close()
        return send_success({'status': 'healthy', 'message': 'Database connection OK'})
    return send_error('Database connection failed', 500)