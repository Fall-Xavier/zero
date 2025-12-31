from fastapi import Header, HTTPException
from app.core.security import decode_token, is_access_token_valid, should_refresh, create_access_token

async def get_current_user(Authorization: str = Header(None)):
    if not Authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    try:
        scheme, token = Authorization.split()
    except:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authorization must use Bearer token")
    if not is_access_token_valid(token):
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    payload = decode_token(token)

    new_access_token = None
    if should_refresh(payload):
        new_access_token = create_access_token(payload["sub"])
    return {
        "user_id": payload["sub"],
        "new_access_token": new_access_token
    }