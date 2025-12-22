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

def calc_consistency_score():
    """Calculate consistency score (simulated)"""
    return round(random.uniform(65.0, 98.0), 2)