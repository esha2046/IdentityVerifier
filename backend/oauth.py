"""OAuth routes for GitHub and Google"""
import os
import json
import requests
from flask import redirect, request, jsonify, url_for
from cryptography.fernet import Fernet
from database import execute_query
from auth import generate_token
from config import (
    GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET,
    GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET
)

# ── Encryption key for storing OAuth tokens safely ─────────────────────────────
# We generate one and store it in .env — if it doesn't exist yet we create it
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    # Auto-generate and print so you can save it to .env
    new_key = Fernet.generate_key().decode()
    print(f"\n⚠️  Add this to your .env file:\nFERNET_KEY={new_key}\n")
    FERNET_KEY = new_key

fernet = Fernet(FERNET_KEY.encode())

def encrypt_token(token: str) -> str:
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted: str) -> str:
    return fernet.decrypt(encrypted.encode()).decode()

# ── Helpers ────────────────────────────────────────────────────────────────────

def error_response(message, status=400):
    return jsonify({'success': False, 'error': message}), status

def success_response(data):
    return jsonify({'success': True, **data})

def save_oauth_verification(user_id, platform, platform_user_id, username, profile_url, access_token):
    """Store OAuth verification in DB, update trust score, log event"""

    # Check if this platform account is already connected to ANY identity
    existing, _ = execute_query(
        "SELECT id FROM oauth_verifications WHERE platform = %s AND platform_user_id = %s",
        (platform, str(platform_user_id)),
        fetchone=True
    )
    if existing:
        return None, f"This {platform} account is already connected to an identity"

    # Encrypt the access token before storing
    encrypted_token = encrypt_token(access_token)

    # Find the identity anchor for this user
    identity, _ = execute_query(
        "SELECT anchor_id FROM identity_anchors WHERE user_id = %s ORDER BY created_at DESC LIMIT 1",
        (user_id,),
        fetchone=True
    )

    anchor_id = identity['anchor_id'] if identity else None

    # Save verification
    result, error = execute_query(
        """
        INSERT INTO oauth_verifications 
            (user_id, anchor_id, platform, platform_user_id, platform_username, profile_url, encrypted_token)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id, platform, platform_username, profile_url, connected_at
        """,
        (user_id, anchor_id, platform, str(platform_user_id), username, profile_url, encrypted_token),
        fetchone=True,
        commit=True
    )

    if error:
        return None, error

    if anchor_id:
        execute_query(
            """
            INSERT INTO platform_verifications (anchor_id, platform_name, profile_url, verification_token)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (anchor_id, platform, profile_url, 'oauth_verified'),
            commit=True
        )

    return result, None


# ── GitHub OAuth ───────────────────────────────────────────────────────────────

def github_login():
    """Step 1 — Redirect user to GitHub authorization page"""
    # Get user_id from query param so we know who's connecting
    user_id = request.args.get('user_id')
    if not user_id:
        return error_response('user_id is required')

    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&scope=read:user"
        f"&state={user_id}"   # we pass user_id as state so callback knows who this is
    )
    return redirect(github_auth_url)


def github_callback():
    """Step 2 — GitHub redirects back here with an auth code"""
    code    = request.args.get('code')
    user_id = request.args.get('state')  # we put user_id in state earlier

    if not code:
        return error_response('No authorization code received from GitHub')

    # Exchange code for access token
    token_res = requests.post(
        'https://github.com/login/oauth/access_token',
        data={
            'client_id':     GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code':          code
        },
        headers={'Accept': 'application/json'}
    )
    token_data   = token_res.json()
    access_token = token_data.get('access_token')

    if not access_token:
        return error_response('Failed to get access token from GitHub')

    # Fetch GitHub profile
    profile_res  = requests.get(
        'https://api.github.com/user',
        headers={
            'Authorization': f'token {access_token}',
            'Accept':        'application/json'
        }
    )
    profile      = profile_res.json()
    github_id    = profile.get('id')
    username     = profile.get('login')
    profile_url  = profile.get('html_url')

    if not github_id:
        return error_response('Failed to fetch GitHub profile')

    # Save to DB
    result, error = save_oauth_verification(
        user_id, 'GitHub', github_id, username, profile_url, access_token
    )
    if error:
        return redirect(f"https://identity-verifier-tt63.onrender.com/?oauth_error={error}")

    return redirect(f"https://identity-verifier-tt63.onrender.com/?oauth_success=true&platform=GitHub&username={username}")




# ── Google OAuth ───────────────────────────────────────────────────────────────

def google_login():
    """Step 1 — Redirect user to Google authorization page"""
    user_id = request.args.get('user_id')
    if not user_id:
        return error_response('user_id is required')

    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri=https://identity-verifier-tt63.onrender.com/api/oauth/google/callback"
        f"&response_type=code"
        f"&scope=openid%20email%20profile"
        f"&state={user_id}"
    )
    return redirect(google_auth_url)


def google_callback():
    """Step 2 — Google redirects back here with an auth code"""
    code    = request.args.get('code')
    user_id = request.args.get('state')

    if not code:
        return error_response('No authorization code received from Google')

    # Exchange code for access token
    token_res = requests.post(
        'https://oauth2.googleapis.com/token',
        data={
            'client_id':     GOOGLE_CLIENT_ID,
            'client_secret': GOOGLE_CLIENT_SECRET,
            'code':          code,
            'grant_type':    'authorization_code',
            'redirect_uri': 'https://identity-verifier-tt63.onrender.com/api/oauth/google/callback'
        }
    )
    token_data   = token_res.json()
    access_token = token_data.get('access_token')

    if not access_token:
        return error_response('Failed to get access token from Google')

    # Fetch Google profile
    profile_res = requests.get(
        'https://www.googleapis.com/oauth2/v2/userinfo',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    profile     = profile_res.json()
    google_id   = profile.get('id')
    username    = profile.get('name')
    email       = profile.get('email')
    profile_url = profile.get('link', f"https://accounts.google.com")

    if not google_id:
        return error_response('Failed to fetch Google profile')

    result, error = save_oauth_verification(
        user_id, 'Google', google_id, username or email, profile_url, access_token
    )
    if error:
        return redirect(f"https://identity-verifier-tt63.onrender.com/?oauth_error={error}")

    return redirect(f"https://identity-verifier-tt63.onrender.com/?oauth_success=true&platform=Google&username={username or email}")



# ── Get connected accounts ─────────────────────────────────────────────────────

def get_oauth_verifications():
    """Return all OAuth verifications for the logged-in user"""
    user_id = request.user.get('user_id')

    verifications, error = execute_query(
        """
        SELECT id, platform, platform_username, profile_url, connected_at
        FROM oauth_verifications
        WHERE user_id = %s
        ORDER BY connected_at DESC
        """,
        (user_id,)
    )
    if error:
        return error_response(error, 500)

    return success_response({
        'verifications': [dict(v) for v in verifications] if verifications else []
    })