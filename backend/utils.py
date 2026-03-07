"""Helper functions for cryptography, key generation, signing and scoring"""
import hashlib
import secrets
import random
import base64
import json
from datetime import datetime

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import (
    Encoding, PublicFormat, PrivateFormat, NoEncryption
)
from cryptography.fernet import Fernet
from cryptography.exceptions import InvalidSignature

import os

# ── Fernet encryption (for storing private keys safely) ───────────────────────
FERNET_KEY = os.getenv('FERNET_KEY')
if not FERNET_KEY:
    raise ValueError("FERNET_KEY not found in environment. Add it to your .env file.")
fernet = Fernet(FERNET_KEY.encode())


# ── Ed25519 Key Generation ─────────────────────────────────────────────────────

def generate_keypair():
    """
    Generate a real Ed25519 public/private key pair.
    Returns:
        public_key_hex  — the public key as a hex string (safe to store/display)
        public_key_b64  — the public key as base64 (used for QR code)
        private_key_enc — the private key encrypted with Fernet (safe to store in DB)
    """
    private_key = Ed25519PrivateKey.generate()

    # Serialize public key to raw bytes then encode
    pub_bytes      = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    public_key_hex = pub_bytes.hex()
    public_key_b64 = base64.b64encode(pub_bytes).decode()

    # Serialize private key to raw bytes then encrypt
    priv_bytes         = private_key.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    private_key_enc    = fernet.encrypt(priv_bytes).decode()

    return public_key_hex, public_key_b64, private_key_enc


def load_private_key(private_key_enc: str) -> Ed25519PrivateKey:
    """Decrypt and load a private key from its encrypted stored form"""
    priv_bytes = fernet.decrypt(private_key_enc.encode())
    return Ed25519PrivateKey.from_private_bytes(priv_bytes)


def load_public_key(public_key_hex: str):
    """Load a public key from its hex string form"""
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    pub_bytes = bytes.fromhex(public_key_hex)
    return Ed25519PublicKey.from_public_bytes(pub_bytes)


# ── Signing & Verification ─────────────────────────────────────────────────────

def sign_verification_claim(private_key_enc: str, claim: dict) -> str:
    """
    Sign a verification claim dict with the identity's private key.
    The claim is serialized to a canonical JSON string before signing.
    Returns the signature as a base64 string.
    """
    private_key    = load_private_key(private_key_enc)
    claim_bytes    = json.dumps(claim, sort_keys=True, separators=(',', ':')).encode()
    signature_bytes = private_key.sign(claim_bytes)
    return base64.b64encode(signature_bytes).decode()


def verify_signature(public_key_hex: str, claim: dict, signature_b64: str) -> bool:
    """
    Verify a signature against a claim using the identity's public key.
    Returns True if valid, False if tampered or invalid.
    """
    try:
        public_key     = load_public_key(public_key_hex)
        claim_bytes    = json.dumps(claim, sort_keys=True, separators=(',', ':')).encode()
        sig_bytes      = base64.b64decode(signature_b64)
        public_key.verify(sig_bytes, claim_bytes)
        return True
    except (InvalidSignature, Exception):
        return False


def build_verification_claim(anchor_id, platform, profile_url, verified_at=None) -> dict:
    """
    Build the canonical claim dict that gets signed.
    This is what proves: "identity #anchor_id owns this platform account"
    """
    return {
        "anchor_id":   anchor_id,
        "platform":    platform,
        "profile_url": profile_url,
        "verified_at": verified_at or datetime.utcnow().isoformat(),
        "issuer":      "CrossPlatformIdentityVerifier/v1"
    }


# ── QR Code Generation ─────────────────────────────────────────────────────────

def generate_qr_code_base64(public_key_b64: str, anchor_id: int) -> str:
    """
    Generate a QR code image containing the identity's public key.
    Returns the image as a base64 PNG string (embeddable directly in HTML).
    """
    import qrcode
    import io

    # The QR code encodes a JSON payload with the public key and anchor ID
    payload = json.dumps({
        "anchor_id":  anchor_id,
        "public_key": public_key_b64,
        "issuer":     "CrossPlatformIdentityVerifier/v1"
    })

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=6,
        border=4
    )
    qr.add_data(payload)
    qr.make(fit=True)

    img        = qr.make_image(fill_color="black", back_color="white")
    buffer     = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    return base64.b64encode(buffer.getvalue()).decode()


# ── Legacy helpers (kept for backwards compatibility) ─────────────────────────

def generate_key():
    """Legacy: generate a random hex key — replaced by generate_keypair()"""
    random_bytes = secrets.token_bytes(32)
    return hashlib.sha256(random_bytes).hexdigest()

def generate_token():
    """Generate a secure random verification token"""
    return secrets.token_urlsafe(32)

def calc_consistency_score(identity_anchor, platform_a, platform_b):
    """Placeholder consistency score — replaced in Week 4 with real ML"""
    seed_string = f"{identity_anchor}-{platform_a}-{platform_b}"
    seed_hash   = int(hashlib.md5(seed_string.encode()).hexdigest(), 16)
    random.seed(seed_hash)
    base_score  = random.uniform(65.0, 98.0)
    random.seed()
    return round(base_score, 2)