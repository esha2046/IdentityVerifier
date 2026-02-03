"""Data models with static methods for database operations"""
from database import execute_query
from utils import generate_key, generate_token, calc_consistency_score

class Identity:
    """Identity Anchor model"""
    
    @staticmethod
    def create():
        """Create new identity"""
        query = """
            INSERT INTO identity_anchors (user_pub_key, trust_score)
            VALUES (%s, %s)
            RETURNING anchor_id, user_pub_key, trust_score, created_at
        """
        return execute_query(query, (generate_key(), 50.0), fetchone=True, commit=True)
    
    @staticmethod
    def get_all():
        """Get all identities"""
        query = """
            SELECT anchor_id, user_pub_key, trust_score, created_at
            FROM identity_anchors
            ORDER BY created_at DESC
        """
        return execute_query(query)
    
    @staticmethod
    def get_by_id(anchor_id):
        """Get identity by ID"""
        query = "SELECT * FROM identity_anchors WHERE anchor_id = %s"
        return execute_query(query, (anchor_id,), fetchone=True)
    
    @staticmethod
    def search(term):
        """Search identities"""
        query = """
            SELECT anchor_id, user_pub_key, trust_score, created_at
            FROM identity_anchors
            WHERE CAST(anchor_id AS TEXT) LIKE %s 
               OR user_pub_key LIKE %s
            ORDER BY created_at DESC
        """
        search_term = f"%{term}%"
        return execute_query(query, (search_term, search_term))
    
    @staticmethod
    def get_details(anchor_id):
        """Get complete identity details"""
        identity, error = Identity.get_by_id(anchor_id)
        if error or not identity:
            return None, error or "Identity not found"
        
        verifications, _ = execute_query(
            "SELECT * FROM platform_verifications WHERE anchor_id = %s ORDER BY verified_at DESC",
            (anchor_id,)
        )
        
        events, _ = execute_query(
            "SELECT * FROM reputation_events WHERE anchor_id = %s ORDER BY time_stamp DESC",
            (anchor_id,)
        )
        
        return {
            'identity': identity,
            'verifications': verifications or [],
            'events': events or []
        }, None
    
    @staticmethod
    def get_trust_history(anchor_id):
        """Get trust score history"""
        identity, error = Identity.get_by_id(anchor_id)
        if error or not identity:
            return None, error or "Identity not found"
        
        events, _ = execute_query(
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
    
    @staticmethod
    def update_trust_score(anchor_id, impact):
        """Update trust score"""
        query = """
            UPDATE identity_anchors 
            SET trust_score = GREATEST(LEAST(trust_score + %s, 100), 0)
            WHERE anchor_id = %s
            RETURNING trust_score
        """
        return execute_query(query, (impact, anchor_id), fetchone=True, commit=True)
    
    @staticmethod
    def get_statistics():
        """Get dashboard statistics"""
        stats = {}
        
        result, _ = execute_query("SELECT COUNT(*) as count FROM identity_anchors", fetchone=True)
        stats['total_identities'] = result['count'] if result else 0
        
        result, _ = execute_query("SELECT COUNT(*) as count FROM platform_verifications", fetchone=True)
        stats['total_verifications'] = result['count'] if result else 0
        
        result, _ = execute_query("SELECT AVG(trust_score) as avg FROM identity_anchors", fetchone=True)
        stats['avg_trust'] = result['avg'] if result and result['avg'] else 0.0
        
        result, _ = execute_query("SELECT AVG(consistency_score) as avg FROM consistency_checks", fetchone=True)
        stats['avg_consistency'] = result['avg'] if result and result['avg'] else 0.0
        
        return stats, None


class Verification:
    """Platform Verification model"""
    
    @staticmethod
    def create(anchor_id, platform, url):
        """Create new verification"""
        # Check if identity exists
        identity, error = Identity.get_by_id(anchor_id)
        if error or not identity:
            return None, "Identity not found"
        
        # Insert verification
        query = """
            INSERT INTO platform_verifications 
            (anchor_id, platform_name, profile_url, verification_token)
            VALUES (%s, %s, %s, %s)
            RETURNING verification_id, anchor_id, platform_name, profile_url, 
                      verification_token, verified_at
        """
        verification, error = execute_query(
            query, 
            (anchor_id, platform, url, generate_token()), 
            fetchone=True, 
            commit=True
        )
        
        if error:
            return None, error
        
        # Update trust score
        result, _ = Identity.update_trust_score(anchor_id, 5.0)
        if result:
            verification['trust_score'] = result['trust_score']
        
        # Log event
        execute_query(
            "INSERT INTO reputation_events (anchor_id, event_type, platform) VALUES (%s, %s, %s)",
            (anchor_id, 'successful_verification', platform),
            commit=True
        )
        
        return verification, None
    
    @staticmethod
    def get_all():
        """Get all verifications"""
        query = """
            SELECT v.*, i.trust_score
            FROM platform_verifications v
            JOIN identity_anchors i ON v.anchor_id = i.anchor_id
            ORDER BY v.verified_at DESC
        """
        return execute_query(query)


class ConsistencyCheck:
    """Consistency Check model"""
    
    @staticmethod
    def create(user_group, platform_a, platform_b):
        """Create consistency check"""
        if platform_a == platform_b:
            return None, "Platforms must be different"
        
        query = """
            INSERT INTO consistency_checks 
            (user_group, platform_a, platform_b, consistency_score)
            VALUES (%s, %s, %s, %s)
            RETURNING check_id, user_group, platform_a, platform_b, 
                      consistency_score, checked_at
        """
        return execute_query(
            query,
            (user_group, platform_a, platform_b, calc_consistency_score()),
            fetchone=True,
            commit=True
        )
    
    @staticmethod
    def get_all():
        """Get all checks"""
        query = "SELECT * FROM consistency_checks ORDER BY checked_at DESC"
        return execute_query(query)


class ReputationEvent:
    """Reputation Event model"""
    
    @staticmethod
    def create(anchor_id, event_type, platform, score_impact):
        """Create reputation event"""
        # Check if identity exists
        identity, error = Identity.get_by_id(anchor_id)
        if error or not identity:
            return None, "Identity not found"
        
        # Insert event
        query = """
            INSERT INTO reputation_events (anchor_id, event_type, platform)
            VALUES (%s, %s, %s)
            RETURNING event_id, anchor_id, event_type, platform, time_stamp
        """
        event, error = execute_query(
            query,
            (anchor_id, event_type, platform),
            fetchone=True,
            commit=True
        )
        
        if error:
            return None, error
        
        # Update trust score if impact provided
        if score_impact != 0:
            Identity.update_trust_score(anchor_id, score_impact)
        
        return event, None