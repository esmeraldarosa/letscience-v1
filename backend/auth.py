"""
Authentication module for LetScience Platform
Provides password hashing, JWT tokens, and TOTP-based 2FA
"""

from datetime import datetime, timedelta
from typing import Optional
import secrets
import hashlib
import hmac
import struct
import time
import base64

# Password hashing with bcrypt-like approach using hashlib
def hash_password(password: str) -> str:
    """Hash password with salt using SHA-256"""
    salt = secrets.token_hex(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    return f"{salt}${pw_hash.hex()}"

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    try:
        salt, pw_hash = hashed.split('$')
        new_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return hmac.compare_digest(new_hash.hex(), pw_hash)
    except:
        return False


# JWT-like token generation (simplified)
JWT_SECRET = secrets.token_hex(32)
TOKEN_EXPIRE_HOURS = 24

def create_token(user_id: int, username: str) -> str:
    """Create a simple signed token"""
    expires = int((datetime.utcnow() + timedelta(hours=TOKEN_EXPIRE_HOURS)).timestamp())
    payload = f"{user_id}:{username}:{expires}"
    signature = hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    token_data = base64.b64encode(f"{payload}:{signature}".encode()).decode()
    return token_data

def verify_token(token: str) -> Optional[dict]:
    """Verify token and return payload"""
    try:
        decoded = base64.b64decode(token.encode()).decode()
        parts = decoded.rsplit(':', 1)
        payload, signature = parts[0], parts[1]
        
        # Verify signature
        expected_sig = hmac.new(JWT_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        
        # Parse payload
        user_id, username, expires = payload.split(':')
        
        # Check expiration
        if int(expires) < int(datetime.utcnow().timestamp()):
            return None
            
        return {"user_id": int(user_id), "username": username}
    except:
        return None


# TOTP (Time-based One-Time Password) for 2FA
def generate_totp_secret() -> str:
    """Generate a new TOTP secret"""
    return base64.b32encode(secrets.token_bytes(20)).decode()

def get_totp_code(secret: str, time_step: int = 30) -> str:
    """Generate current TOTP code"""
    try:
        key = base64.b32decode(secret.upper())
        counter = int(time.time()) // time_step
        counter_bytes = struct.pack('>Q', counter)
        hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
        offset = hmac_hash[-1] & 0x0F
        code = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
        code = (code & 0x7FFFFFFF) % 1000000
        return f"{code:06d}"
    except:
        return ""

def verify_totp(secret: str, code: str, window: int = 1) -> bool:
    """Verify TOTP code with time window"""
    for i in range(-window, window + 1):
        time_step = 30
        counter = (int(time.time()) // time_step) + i
        try:
            key = base64.b32decode(secret.upper())
            counter_bytes = struct.pack('>Q', counter)
            hmac_hash = hmac.new(key, counter_bytes, hashlib.sha1).digest()
            offset = hmac_hash[-1] & 0x0F
            expected = struct.unpack('>I', hmac_hash[offset:offset+4])[0]
            expected = (expected & 0x7FFFFFFF) % 1000000
            if code == f"{expected:06d}":
                return True
        except:
            continue
    return False

def get_totp_uri(secret: str, username: str, issuer: str = "LetScience") -> str:
    """Generate otpauth URI for QR code"""
    return f"otpauth://totp/{issuer}:{username}?secret={secret}&issuer={issuer}"
