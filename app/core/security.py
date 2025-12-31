import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from app.config.supabase import supabase

JWT_SECRET = "ZERO_SUPER_SECRET_KEY"  # ganti dengan key panjang dan random
JWT_ALGO = "HS256"
ACCESS_EXPIRE_MIN = 10
REFRESH_EXPIRE_DAYS = 30

def create_access_token(user_id: str) -> str:
    payload = {
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_EXPIRE_MIN),
        "sub": user_id,
        "type": "access"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

def create_refresh_token(user_id: str, token_id: Optional[str] = None) -> str:
    token_id = token_id or str(uuid.uuid4())
    expire_dt = datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS)
    
    payload = {
        "exp": expire_dt,
        "sub": user_id,
        "jti": token_id,
        "type": "refresh"
    }
    
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)

    # Simpan ke DB, pakai expire_dt.isoformat() bukan payload["exp"]
    supabase.table("refresh_tokens").insert({
        "id": token_id,
        "user_id": user_id,
        "expires_at": expire_dt.isoformat(),
        "revoked": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }).execute()

    return token

def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
    except JWTError:
        raise ValueError("Token invalid atau expired")

def is_access_token_valid(token: str) -> bool:
    try:
        return decode_token(token).get("type") == "access"
    except ValueError:
        return False

def is_refresh_token_valid(token: str) -> bool:
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            return False
        return _is_refresh_token_valid_in_db(payload["jti"], payload["sub"])
    except ValueError:
        return False

def _is_refresh_token_valid_in_db(jti: str, user_id: str) -> bool:
    res = supabase.table("refresh_tokens") \
        .select("*").eq("id", jti).eq("user_id", user_id).eq("revoked", False).execute()
    return bool(res.data)

def revoke_refresh_token(jti: str):
    supabase.table("refresh_tokens").update({"revoked": True}).eq("id", jti).execute()

def should_refresh(payload: dict, threshold_seconds: int = 30) -> bool:
    """
    Cek apakah token access hampir expired.
    Jika kurang dari threshold (default 30 detik), return True.
    """
    exp_timestamp = payload.get("exp")
    if not exp_timestamp:
        return False

    now = datetime.utcnow().timestamp()
    return exp_timestamp - now < threshold_seconds