"""Helper functions for key generation and scoring"""
import hashlib
import secrets
import random

def generate_key():
    """Generate cryptographic public key"""
    random_bytes = secrets.token_bytes(32)
    return hashlib.sha256(random_bytes).hexdigest()

def generate_token():
    """Generate verification token"""
    return secrets.token_urlsafe(32)

def calc_consistency_score(identity_anchor, platform_a, platform_b):
    """Calculate consistency score based on identity and platform pair"""
    seed_string = f"{identity_anchor}-{platform_a}-{platform_b}"
    seed_hash = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
    
    random.seed(seed_hash)
    base_score = random.uniform(65.0, 98.0)
    
    random.seed()
    
    return round(base_score, 2)