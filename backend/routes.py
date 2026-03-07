"""API route handlers"""
from flask import jsonify, request
from datetime import datetime
import re
from models import Identity, Verification, ConsistencyCheck, ReputationEvent
from database import execute_query
from auth import hash_password, check_password, generate_token

# ── Helpers ────────────────────────────────────────────────────────────────────

def success_response(data):
    return jsonify({'success': True, **data})

def error_response(message, status=400):
    return jsonify({'success': False, 'error': message}), status

ALLOWED_PLATFORMS = {'Instagram', 'LinkedIn', 'X', 'Facebook', 'GitHub', 'Kaggle'}
ALLOWED_EVENT_TYPES = {'successful_verification', 'suspicious_activity', 'profile_update', 're_verification'}

def is_valid_email(email):
    """Basic but solid email format check"""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def is_valid_url(url):
    """Check URL starts with http/https"""
    return url.startswith('http://') or url.startswith('https://')

def is_valid_password(password):
    """
    Password must:
    - Be at least 8 characters
    - Contain at least one number
    - Contain at least one letter
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters'
    if not re.search(r'[A-Za-z]', password):
        return False, 'Password must contain at least one letter'
    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number'
    return True, None

# ── Auth ───────────────────────────────────────────────────────────────────────

def register():
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON')

    username = data.get('username', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Presence check
    if not all([username, email, password]):
        return error_response('Missing required fields: username, email, password')

    # Username
    if len(username) < 3:
        return error_response('Username must be at least 3 characters')
    if len(username) > 50:
        return error_response('Username must be 50 characters or fewer')
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return error_response('Username can only contain letters, numbers, and underscores')

    # Email
    if not is_valid_email(email):
        return error_response('Invalid email format')

    # Password
    valid, msg = is_valid_password(password)
    if not valid:
        return error_response(msg)

    # Duplicate check
    existing, _ = execute_query(
        "SELECT user_id FROM users WHERE email = %s OR username = %s",
        (email, username),
        fetchone=True
    )
    if existing:
        return error_response('Email or username already taken')

    # Create user
    user, error = execute_query(
        """
        INSERT INTO users (username, email, password_hash)
        VALUES (%s, %s, %s)
        RETURNING user_id, username, email, created_at
        """,
        (username, email, hash_password(password)),
        fetchone=True,
        commit=True
    )
    if error:
        return error_response(error, 500)

    token = generate_token(user['user_id'], user['username'])
    return success_response({'token': token, 'user': dict(user)})


def login():
    data = request.get_json()
    if not data:
        return error_response('Request body must be JSON')

    email    = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not all([email, password]):
        return error_response('Missing required fields: email, password')

    if not is_valid_email(email):
        return error_response('Invalid email format')

    user, error = execute_query(
        "SELECT * FROM users WHERE email = %s",
        (email,),
        fetchone=True
    )
    # Same error message for both "not found" and "wrong password" — avoids user enumeration
    if error or not user:
        return error_response('Invalid email or password', 401)

    if not check_password(password, user['password_hash']):
        return error_response('Invalid email or password', 401)

    token = generate_token(user['user_id'], user['username'])
    return success_response({
        'token': token,
        'user': {
            'user_id':  user['user_id'],
            'username': user['username'],
            'email':    user['email']
        }
    })

# ── Statistics ─────────────────────────────────────────────────────────────────

def get_statistics():
    stats, error = Identity.get_statistics()
    if error:
        return error_response(error, 500)
    return success_response({
        'statistics': {
            'total_identities':      stats['total_identities'],
            'total_verifications':   stats['total_verifications'],
            'avg_trust_score':       float(stats['avg_trust']),
            'avg_consistency_score': float(stats['avg_consistency'])
        }
    })

# ── Identity ───────────────────────────────────────────────────────────────────

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
    term = request.args.get('q', '').strip()
    if not term:
        return error_response('Search term is required')
    identities, error = Identity.search(term)
    if error:
        return error_response(error, 500)
    return success_response({'identities': [dict(i) for i in identities]})

def get_identity_details(anchor_id):
    data, error = Identity.get_details(anchor_id)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    return success_response({
        'identity':      dict(data['identity']),
        'verifications': [dict(v) for v in data['verifications']],
        'events':        [dict(e) for e in data['events']]
    })

def export_identity(anchor_id):
    data, error = Identity.get_details(anchor_id)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    return success_response({
        'data': {
            'export_date':   datetime.now().isoformat(),
            'identity':      dict(data['identity']),
            'verifications': [dict(v) for v in data['verifications']],
            'events':        [dict(e) for e in data['events']],
            'statistics': {
                'total_verifications': len(data['verifications']),
                'total_events':        len(data['events'])
            }
        }
    })

def get_trust_history(anchor_id):
    data, error = Identity.get_trust_history(anchor_id)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    return success_response(data)

# ── Verification ───────────────────────────────────────────────────────────────

def add_verification():
    data      = request.get_json()
    anchor_id = data.get('anchor_id')
    platform  = data.get('platform_name', '').strip()
    url       = data.get('profile_url', '').strip()

    if not all([anchor_id, platform, url]):
        return error_response('Missing required fields: anchor_id, platform_name, profile_url')

    if not isinstance(anchor_id, int) or anchor_id <= 0:
        return error_response('anchor_id must be a positive integer')

    if platform not in ALLOWED_PLATFORMS:
        return error_response(f'Invalid platform. Allowed: {", ".join(ALLOWED_PLATFORMS)}')

    if not is_valid_url(url):
        return error_response('profile_url must start with http:// or https://')

    if len(url) > 500:
        return error_response('profile_url is too long (max 500 characters)')

    verification, error = Verification.create(anchor_id, platform, url)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    return success_response({'verification': dict(verification)})

def get_verifications():
    verifications, error = Verification.get_all()
    if error:
        return error_response(error, 500)
    return success_response({'verifications': [dict(v) for v in verifications]})

# ── Consistency Check ──────────────────────────────────────────────────────────

def run_consistency_check():
    data            = request.get_json()
    identity_anchor = data.get('identity_anchor', '').strip() if data.get('identity_anchor') else None
    platform_a      = data.get('platform_a', '').strip()
    platform_b      = data.get('platform_b', '').strip()

    if not all([identity_anchor, platform_a, platform_b]):
        return error_response('Missing required fields: identity_anchor, platform_a, platform_b')

    if platform_a not in ALLOWED_PLATFORMS or platform_b not in ALLOWED_PLATFORMS:
        return error_response(f'Invalid platform. Allowed: {", ".join(ALLOWED_PLATFORMS)}')

    if platform_a == platform_b:
        return error_response('Platform A and Platform B must be different')

    check, error = ConsistencyCheck.create(identity_anchor, platform_a, platform_b)
    if error:
        return error_response(error, 500)
    return success_response({'check': dict(check)})

def get_consistency_checks():
    checks, error = ConsistencyCheck.get_all()
    if error:
        return error_response(error, 500)
    return success_response({'checks': [dict(c) for c in checks]})

# ── Reputation Events ──────────────────────────────────────────────────────────

def log_reputation_event():
    data         = request.get_json()
    anchor_id    = data.get('anchor_id')
    event_type   = data.get('event_type', '').strip()
    platform     = data.get('platform', '').strip()
    score_impact = data.get('score_impact', 0)

    if not all([anchor_id, event_type]):
        return error_response('Missing required fields: anchor_id, event_type')

    if not isinstance(anchor_id, int) or anchor_id <= 0:
        return error_response('anchor_id must be a positive integer')

    if event_type not in ALLOWED_EVENT_TYPES:
        return error_response(f'Invalid event_type. Allowed: {", ".join(ALLOWED_EVENT_TYPES)}')

    if platform and platform not in ALLOWED_PLATFORMS:
        return error_response(f'Invalid platform. Allowed: {", ".join(ALLOWED_PLATFORMS)}')

    try:
        score_impact = float(score_impact)
    except (ValueError, TypeError):
        return error_response('score_impact must be a number')

    if not (-100 <= score_impact <= 100):
        return error_response('score_impact must be between -100 and 100')

    event, error = ReputationEvent.create(anchor_id, event_type, platform, score_impact)
    if error:
        return error_response(error, 404 if 'not found' in error.lower() else 500)
    return success_response({'event': dict(event)})

def get_reputation_events():
    events, error = ReputationEvent.get_all()
    if error:
        return error_response(error, 500)
    return success_response({'events': [dict(e) for e in events]})

# ── Health ─────────────────────────────────────────────────────────────────────

def health_check():
    from database import get_connection
    conn = get_connection()
    if conn:
        conn.close()
        return success_response({'status': 'healthy', 'message': 'Database connection OK'})
    return error_response('Database connection failed', 500)

def get_qr_code(anchor_id):
    """Generate and return a QR code for an identity's public key"""
    from utils import generate_qr_code_base64

    identity, error = Identity.get_by_id(anchor_id)
    if error or not identity:
        return error_response('Identity not found', 404)

    public_key_b64 = identity.get('public_key_b64')
    if not public_key_b64:
        return error_response('This identity has no cryptographic key yet. Re-create it to get one.', 400)

    qr_base64 = generate_qr_code_base64(public_key_b64, anchor_id)
    return success_response({
        'anchor_id':      anchor_id,
        'public_key':     identity['user_pub_key'],
        'public_key_b64': public_key_b64,
        'qr_code':        f"data:image/png;base64,{qr_base64}"
    })


def verify_claim():
    """Verify a verification signature — proves a claim hasn't been tampered with"""
    data         = request.get_json()
    anchor_id    = data.get('anchor_id')
    platform     = data.get('platform')
    profile_url  = data.get('profile_url')
    verified_at  = data.get('verified_at')
    signature    = data.get('signature')

    if not all([anchor_id, platform, profile_url, verified_at, signature]):
        return error_response('Missing fields: anchor_id, platform, profile_url, verified_at, signature')

    valid, error = Verification.verify_claim(anchor_id, platform, profile_url, verified_at, signature)
    if error:
        return error_response(error, 404)

    return success_response({
        'valid':   valid,
        'message': '✅ Signature is valid — this verification has not been tampered with.' if valid
                   else '❌ Signature is invalid — this verification may have been tampered with.'
    })
