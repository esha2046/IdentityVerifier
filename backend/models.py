from database import run_query
from utils import generate_key, generate_token, calc_consistency_score

# Identity functions

def create_identity():
    query = """
        INSERT INTO identity_anchors (user_pub_key, trust_score)
        VALUES (%s, %s)
        RETURNING anchor_id, user_pub_key, trust_score, created_at
    """
    return run_query(query, (generate_key(), 50.0))

def get_all_identities():
    query = """
        SELECT anchor_id, user_pub_key, trust_score, created_at
        FROM identity_anchors
        ORDER BY created_at DESC
    """
    return run_query(query)

def get_identity(anchor_id):
    query = "SELECT * FROM identity_anchors WHERE anchor_id = %s LIMIT 1"
    return run_query(query, (anchor_id,))

def search_identities(search_term):
    query = """
        SELECT anchor_id, user_pub_key, trust_score, created_at
        FROM identity_anchors
        WHERE CAST(anchor_id AS TEXT) LIKE %s OR user_pub_key LIKE %s
        ORDER BY created_at DESC
    """
    term = f"%{search_term}%"
    return run_query(query, (term, term))

def get_identity_details(anchor_id):
    identity, error = get_identity(anchor_id)
    if error or not identity:
        return None, error or "Identity not found"
    
    verifications, _ = run_query(
        "SELECT * FROM platform_verifications WHERE anchor_id = %s ORDER BY verified_at DESC",
        (anchor_id,)
    )
    
    events, _ = run_query(
        "SELECT * FROM reputation_events WHERE anchor_id = %s ORDER BY time_stamp DESC",
        (anchor_id,)
    )
    
    return {
        'identity': identity,
        'verifications': verifications or [],
        'events': events or []
    }, None

def get_trust_history(anchor_id):
    identity, error = get_identity(anchor_id)
    if error or not identity:
        return None, error or "Identity not found"
    
    # Get history with previous scores for comparison
    events, _ = run_query(
        """
        SELECT event_type, platform, time_stamp, 
               LAG(trust_score) OVER (ORDER BY time_stamp) as prev_score
        FROM reputation_events
        WHERE anchor_id = %s
        ORDER BY time_stamp DESC
        LIMIT 20
        """,
        (anchor_id,)
    )
    
    return {
        'current_score': identity['trust_score'],
        'history': events or []
    }, None

def update_trust_score(anchor_id, change):
    # Keep score between 0 and 100
    query = """
        UPDATE identity_anchors 
        SET trust_score = GREATEST(LEAST(trust_score + %s, 100), 0)
        WHERE anchor_id = %s
        RETURNING trust_score
    """
    return run_query(query, (change, anchor_id))

def get_statistics():
    total_identities, _ = run_query("SELECT COUNT(*) as count FROM identity_anchors LIMIT 1")
    total_verifications, _ = run_query("SELECT COUNT(*) as count FROM platform_verifications LIMIT 1")
    avg_trust, _ = run_query("SELECT AVG(trust_score) as avg FROM identity_anchors LIMIT 1")
    avg_consistency, _ = run_query("SELECT AVG(consistency_score) as avg FROM consistency_checks LIMIT 1")
    
    return {
        'total_identities': total_identities['count'] if total_identities else 0,
        'total_verifications': total_verifications['count'] if total_verifications else 0,
        'avg_trust': avg_trust['avg'] if avg_trust and avg_trust['avg'] else 0.0,
        'avg_consistency': avg_consistency['avg'] if avg_consistency and avg_consistency['avg'] else 0.0
    }, None

# Verification functions

def create_verification(anchor_id, platform, url):
    identity, error = get_identity(anchor_id)
    if error or not identity:
        return None, "Identity not found"
    
    query = """
        INSERT INTO platform_verifications 
        (anchor_id, platform_name, profile_url, verification_token)
        VALUES (%s, %s, %s, %s)
        RETURNING verification_id, anchor_id, platform_name, profile_url, 
                  verification_token, verified_at
    """
    verification, error = run_query(query, (anchor_id, platform, url, generate_token()))
    
    if error:
        return None, error
    
    # Increase trust score
    result, _ = update_trust_score(anchor_id, 5.0)
    if result:
        verification['trust_score'] = result['trust_score']
    
    # Log the verification event
    run_query(
        "INSERT INTO reputation_events (anchor_id, event_type, platform) VALUES (%s, %s, %s)",
        (anchor_id, 'successful_verification', platform)
    )
    
    return verification, None

def get_all_verifications():
    query = """
        SELECT v.*, i.trust_score
        FROM platform_verifications v
        JOIN identity_anchors i ON v.anchor_id = i.anchor_id
        ORDER BY v.verified_at DESC
    """
    return run_query(query)

# Consistency check functions

def create_consistency_check(user_group, platform_a, platform_b):
    if platform_a == platform_b:
        return None, "Platforms must be different"
    
    query = """
        INSERT INTO consistency_checks 
        (user_group, platform_a, platform_b, consistency_score)
        VALUES (%s, %s, %s, %s)
        RETURNING check_id, user_group, platform_a, platform_b, 
                  consistency_score, checked_at
    """
    return run_query(query, (user_group, platform_a, platform_b, calc_consistency_score()))

def get_all_consistency_checks():
    query = "SELECT * FROM consistency_checks ORDER BY checked_at DESC"
    return run_query(query)

# Reputation event functions

def create_reputation_event(anchor_id, event_type, platform, score_change):
    identity, error = get_identity(anchor_id)
    if error or not identity:
        return None, "Identity not found"
    
    query = """
        INSERT INTO reputation_events (anchor_id, event_type, platform)
        VALUES (%s, %s, %s)
        RETURNING event_id, anchor_id, event_type, platform, time_stamp
    """
    event, error = run_query(query, (anchor_id, event_type, platform))
    
    if error:
        return None, error
    
    if score_change != 0:
        update_trust_score(anchor_id, score_change)
    
    return event, None