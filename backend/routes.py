"""API route handlers"""
from flask import jsonify, request
from datetime import datetime
from models import Identity, Verification, ConsistencyCheck, ReputationEvent

def success_response(data):
    """Return success response"""
    return jsonify({'success': True, **data})

def error_response(message, status=400):
    """Return error response"""
    return jsonify({'success': False, 'error': message}), status

# Statistics
def get_statistics():
    stats, error = Identity.get_statistics()
    if error:
        return error_response(error, 500)
    
    return success_response({
        'statistics': {
            'total_identities': stats['total_identities'],
            'total_verifications': stats['total_verifications'],
            'avg_trust_score': float(stats['avg_trust']),
            'avg_consistency_score': float(stats['avg_consistency'])
        }
    })

# Identity operations
def create_identity():
    identity, error = Identity.create()
    if error:
        return error_response(error, 500)
    return success_response({'identity': dict(identity)})

def get_identities():
    identities, error = Identity.get_all()
    if error:
        return error_response(error, 500)
    return success_response({'identities': [dict(i) for i in identities]})

def search_identities():
    term = request.args.get('q', '')
    identities, error = Identity.search(term)
    if error:
        return error_response(error, 500)
    return success_response({'identities': [dict(i) for i in identities]})

def get_identity_details(anchor_id):
    data, error = Identity.get_details(anchor_id)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    
    return success_response({
        'identity': dict(data['identity']),
        'verifications': [dict(v) for v in data['verifications']],
        'events': [dict(e) for e in data['events']]
    })

def export_identity(anchor_id):
    data, error = Identity.get_details(anchor_id)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    
    return success_response({
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

def get_trust_history(anchor_id):
    data, error = Identity.get_trust_history(anchor_id)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    return success_response(data)

# Verification operations
def add_verification():
    data = request.get_json()
    anchor_id = data.get('anchor_id')
    platform = data.get('platform_name')
    url = data.get('profile_url')
    
    if not all([anchor_id, platform, url]):
        return error_response('Missing required fields: anchor_id, platform_name, profile_url')
    
    verification, error = Verification.create(anchor_id, platform, url)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    
    return success_response({'verification': dict(verification)})

def get_verifications():
    verifications, error = Verification.get_all()
    if error:
        return error_response(error, 500)
    return success_response({'verifications': [dict(v) for v in verifications]})

# Consistency check operations
def run_consistency_check():
    data = request.get_json()
    user_group = data.get('user_group')
    platform_a = data.get('platform_a')
    platform_b = data.get('platform_b')
    
    if not all([user_group, platform_a, platform_b]):
        return error_response('Missing required fields: user_group, platform_a, platform_b')
    
    check, error = ConsistencyCheck.create(user_group, platform_a, platform_b)
    if error:
        return error_response(error, 500)
    
    return success_response({'check': dict(check)})

def get_consistency_checks():
    checks, error = ConsistencyCheck.get_all()
    if error:
        return error_response(error, 500)
    return success_response({'checks': [dict(c) for c in checks]})

# Reputation event operations
def log_reputation_event():
    data = request.get_json()
    anchor_id = data.get('anchor_id')
    event_type = data.get('event_type')
    platform = data.get('platform', '')
    score_impact = data.get('score_impact', 0)
    
    if not all([anchor_id, event_type]):
        return error_response('Missing required fields: anchor_id, event_type')
    
    event, error = ReputationEvent.create(anchor_id, event_type, platform, score_impact)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    
    return success_response({'event': dict(event)})

# Health check
def health_check():
    from database import get_connection
    conn = get_connection()
    if conn:
        conn.close()
        return success_response({'status': 'healthy', 'message': 'Database connection OK'})
    return error_response('Database connection failed', 500)