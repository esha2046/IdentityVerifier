from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import hashlib
import secrets
import json

app = Flask(__name__)
CORS(app)

# Database configuration
DB_CONFIG = {
    'dbname': 'identity_verifier',
    'user': 'postgres',
    'password': 'password',  # CHANGE THIS to your PostgreSQL password
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def generate_public_key():
    """Generate a cryptographic public key (simulated)"""
    random_bytes = secrets.token_bytes(32)
    return hashlib.sha256(random_bytes).hexdigest()

def generate_verification_token():
    """Generate a verification token"""
    return secrets.token_urlsafe(32)

def calculate_consistency_score():
    """Calculate a consistency score (simulated algorithm)"""
    import random
    return round(random.uniform(65.0, 98.0), 2)

# ============================================
# ENDPOINTS
# ============================================

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get dashboard statistics"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Total identities
        cur.execute("SELECT COUNT(*) as count FROM identity_anchors")
        total_identities = cur.fetchone()['count']
        
        # Total verifications
        cur.execute("SELECT COUNT(*) as count FROM platform_verifications")
        total_verifications = cur.fetchone()['count']
        
        # Average trust score
        cur.execute("SELECT AVG(trust_score) as avg FROM identity_anchors")
        avg_trust_result = cur.fetchone()['avg']
        avg_trust_score = float(avg_trust_result) if avg_trust_result else 0.0
        
        # Average consistency score
        cur.execute("SELECT AVG(consistency_score) as avg FROM consistency_checks")
        avg_consistency_result = cur.fetchone()['avg']
        avg_consistency_score = float(avg_consistency_result) if avg_consistency_result else 0.0
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_identities': total_identities,
                'total_verifications': total_verifications,
                'avg_trust_score': avg_trust_score,
                'avg_consistency_score': avg_consistency_score
            }
        })
    
    except Exception as e:
        print(f"Error fetching statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/identity', methods=['POST'])
def create_identity():
    """Create a new identity anchor"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Generate public key
        public_key = generate_public_key()
        
        # Insert new identity
        cur.execute("""
            INSERT INTO identity_anchors (user_pub_key, trust_score)
            VALUES (%s, %s)
            RETURNING anchor_id, user_pub_key, trust_score, created_at
        """, (public_key, 50.0))
        
        identity = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'identity': dict(identity)
        })
    
    except Exception as e:
        print(f"Error creating identity: {e}")
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/identities', methods=['GET'])
def get_identities():
    """Get all identity anchors"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT anchor_id, user_pub_key, trust_score, created_at
            FROM identity_anchors
            ORDER BY created_at DESC
        """)
        
        identities = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'identities': [dict(i) for i in identities]
        })
    
    except Exception as e:
        print(f"Error fetching identities: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/identity/<int:anchor_id>', methods=['GET'])
def get_identity_details(anchor_id):
    """Get detailed information about a specific identity"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get identity
        cur.execute("""
            SELECT * FROM identity_anchors WHERE anchor_id = %s
        """, (anchor_id,))
        identity = cur.fetchone()
        
        if not identity:
            return jsonify({'success': False, 'error': 'Identity not found'}), 404
        
        # Get verifications
        cur.execute("""
            SELECT * FROM platform_verifications 
            WHERE anchor_id = %s
            ORDER BY verified_at DESC
        """, (anchor_id,))
        verifications = cur.fetchall()
        
        # Get events
        cur.execute("""
            SELECT * FROM reputation_events 
            WHERE anchor_id = %s
            ORDER BY time_stamp DESC
        """, (anchor_id,))
        events = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'identity': dict(identity),
            'verifications': [dict(v) for v in verifications],
            'events': [dict(e) for e in events]
        })
    
    except Exception as e:
        print(f"Error fetching identity details: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verification', methods=['POST'])
def add_verification():
    """Add a platform verification"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        anchor_id = data.get('anchor_id')
        platform_name = data.get('platform_name')
        profile_url = data.get('profile_url')
        
        if not all([anchor_id, platform_name, profile_url]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if identity exists
        cur.execute("SELECT * FROM identity_anchors WHERE anchor_id = %s", (anchor_id,))
        if not cur.fetchone():
            return jsonify({'success': False, 'error': 'Identity anchor not found'}), 404
        
        # Generate verification token
        token = generate_verification_token()
        
        # Insert verification
        cur.execute("""
            INSERT INTO platform_verifications 
            (anchor_id, platform_name, profile_url, verification_token)
            VALUES (%s, %s, %s, %s)
            RETURNING verification_id, anchor_id, platform_name, profile_url, 
                      verification_token, verified_at
        """, (anchor_id, platform_name, profile_url, token))
        
        verification = cur.fetchone()
        
        # Update trust score (+5 for each verification)
        cur.execute("""
            UPDATE identity_anchors 
            SET trust_score = LEAST(trust_score + 5, 100)
            WHERE anchor_id = %s
            RETURNING trust_score
        """, (anchor_id,))
        
        new_trust_score = cur.fetchone()['trust_score']
        
        # Log reputation event
        cur.execute("""
            INSERT INTO reputation_events (anchor_id, event_type, platform)
            VALUES (%s, %s, %s)
        """, (anchor_id, 'successful_verification', platform_name))
        
        conn.commit()
        cur.close()
        conn.close()
        
        verification_dict = dict(verification)
        verification_dict['trust_score'] = new_trust_score
        
        return jsonify({
            'success': True,
            'verification': verification_dict
        })
    
    except Exception as e:
        print(f"Error adding verification: {e}")
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/verifications', methods=['GET'])
def get_verifications():
    """Get all platform verifications"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT v.*, i.trust_score
            FROM platform_verifications v
            JOIN identity_anchors i ON v.anchor_id = i.anchor_id
            ORDER BY v.verified_at DESC
        """)
        
        verifications = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'verifications': [dict(v) for v in verifications]
        })
    
    except Exception as e:
        print(f"Error fetching verifications: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/consistency-check', methods=['POST'])
def run_consistency_check():
    """Run a consistency check between two platforms"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        user_group = data.get('user_group')
        platform_a = data.get('platform_a')
        platform_b = data.get('platform_b')
        
        if not all([user_group, platform_a, platform_b]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if platform_a == platform_b:
            return jsonify({'success': False, 'error': 'Platforms must be different'}), 400
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Calculate consistency score (simulated algorithm)
        consistency_score = calculate_consistency_score()
        
        # Insert consistency check
        cur.execute("""
            INSERT INTO consistency_checks 
            (user_group, platform_a, platform_b, consistency_score)
            VALUES (%s, %s, %s, %s)
            RETURNING check_id, user_group, platform_a, platform_b, 
                      consistency_score, checked_at
        """, (user_group, platform_a, platform_b, consistency_score))
        
        check = cur.fetchone()
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'check': dict(check)
        })
    
    except Exception as e:
        print(f"Error running consistency check: {e}")
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/consistency-checks', methods=['GET'])
def get_consistency_checks():
    """Get all consistency checks"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT * FROM consistency_checks
            ORDER BY checked_at DESC
        """)
        
        checks = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'checks': [dict(c) for c in checks]
        })
    
    except Exception as e:
        print(f"Error fetching consistency checks: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reputation-event', methods=['POST'])
def log_reputation_event():
    """Log a reputation event"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'error': 'Database connection failed'}), 500
    
    try:
        data = request.get_json()
        anchor_id = data.get('anchor_id')
        event_type = data.get('event_type')
        platform = data.get('platform', '')
        score_impact = data.get('score_impact', 0)
        
        if not all([anchor_id, event_type]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check if identity exists
        cur.execute("SELECT * FROM identity_anchors WHERE anchor_id = %s", (anchor_id,))
        if not cur.fetchone():
            return jsonify({'success': False, 'error': 'Identity anchor not found'}), 404
        
        # Insert event
        cur.execute("""
            INSERT INTO reputation_events (anchor_id, event_type, platform)
            VALUES (%s, %s, %s)
            RETURNING event_id, anchor_id, event_type, platform, time_stamp
        """, (anchor_id, event_type, platform))
        
        event = cur.fetchone()
        
        # Update trust score based on event type and score_impact
        if score_impact != 0:
            cur.execute("""
                UPDATE identity_anchors 
                SET trust_score = GREATEST(LEAST(trust_score + %s, 100), 0)
                WHERE anchor_id = %s
                RETURNING trust_score
            """, (score_impact, anchor_id))
            
            new_trust_score = cur.fetchone()['trust_score']
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'event': dict(event)
        })
    
    except Exception as e:
        print(f"Error logging event: {e}")
        if conn:
            conn.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    conn = get_db_connection()
    if conn:
        conn.close()
        return jsonify({'success': True, 'status': 'healthy'})
    return jsonify({'success': False, 'status': 'unhealthy'}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Cross-Platform Digital Identity Verifier - Backend Server")
    print("=" * 60)
    print(f"Server starting on http://localhost:5000")
    print(f"API endpoints available at http://localhost:5000/api/")
    print("\nMake sure to:")
    print("1. Update DB_CONFIG with your PostgreSQL password")
    print("2. Create the database and tables using database_schema.sql")
    print("3. Keep this terminal open while using the application")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)