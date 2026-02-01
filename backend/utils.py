import hashlib
import secrets
import random

def generate_key():
    random_bytes = secrets.token_bytes(32)
    return hashlib.sha256(random_bytes).hexdigest()

def generate_token():
    return secrets.token_urlsafe(32)

def calc_consistency_score():
    # Random score between 65 and 98 for simulation pp only
    return round(random.uniform(65.0, 98.0), 2)