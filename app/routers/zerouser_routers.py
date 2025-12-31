import hashlib, uuid
from fastapi import APIRouter, Query, UploadFile, File, HTTPException, Depends
from app.helpers.response import format_response
from app.helpers.date_utils import time_now
from app.core.security import (
    decode_token, 
    is_refresh_token_valid, 
    is_access_token_valid,
    create_access_token, 
    create_refresh_token, 
    revoke_refresh_token
)
from app.core.auth_dependency import get_current_user
from app.schemas.zerouser_schemas import RefreshBody
from app.services.zerostats_services import create_stats
from app.config.supabase import supabase, SUPABASE_BUCKET

zerouser = APIRouter(prefix="/user")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

@zerouser.post("/register")
def register(
    name: str = Query(None),
    username: str = Query(None),
    email: str = Query(None),
    password: str = Query(None),
):
    try:
        check_username = supabase.table("zerouser").select("*").eq("username", username).execute()
        print(len(check_username.data))
        if len(check_username.data) > 0:
            return format_response("failed", "username already exists", None)
        check_email = supabase.table("zerouser").select("*").eq("email", email).execute()
        if len(check_email.data) > 0:
            return format_response("failed", "email already exists", None)
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        supa = supabase.table("zerouser").insert({
            "user_id": user_id,
            "role": "user",
            "username": username,
            "name": name,
            "email": email,
            "password": password_hash,
            "avatar": "https://i.pinimg.com/736x/8a/e9/e9/8ae9e92fa4e69967aa61bf2bda967b7b.jpg",
            "created_at": time_now()
        }).execute()
        print(supa)
        create_stats(user_id)

        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        return format_response("success", "success register user", {
            "role": "user",
            "access_token": access_token,
            "refresh_token": refresh_token,
        })
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerouser.post("/login")
def login(
    email: str = Query(None),
    password: str = Query(None),
):
    try:
        supa = supabase.table("zerouser").select("*").eq("email", email).execute()
        if not supa.data:
            return format_response("failed", "Email belum terdaftar", None)

        user = supa.data[0]
        password_hash = hash_password(password)
        if password_hash != user["password"]:
            return format_response("failed", "Password salah", None)

        access_token = create_access_token(user["user_id"])
        refresh_token = create_refresh_token(user["user_id"])
        return format_response("success", "success login user", {
            "role": user["role"],
            "access_token": access_token,
            "refresh_token": refresh_token
        })

    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerouser.get("/profile")
def profile(user = Depends(get_current_user)):
    supa = supabase.table("zerouser").select("*").eq("user_id", user["user_id"]).execute()
    user_supa = supa.data[0]
    data = {
        "username": user_supa["username"],
        "name": user_supa["name"],
        "email": user_supa["email"],
        "avatar": user_supa["avatar"],
        "created_at": user_supa["created_at"],
        "user_id": user["user_id"],
        "new_access_token": user["new_access_token"]  # auto refresh access token
    }
    return data

@zerouser.post("/refresh")
def refresh_token(body : RefreshBody):
    refresh_token = body.refresh_token
    if not is_refresh_token_valid(refresh_token):
        raise HTTPException(status_code=401, detail="Refresh token invalid")

    payload = decode_token(refresh_token)
    user_id = payload["sub"]
    jti = payload["jti"]
    revoke_refresh_token(jti)

    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)
    return format_response("success", "token refreshed", {
        "access_token": new_access,
        "refresh_token": new_refresh
    })

@zerouser.post("/logout")
def logout(body : RefreshBody):
    refresh_token = body.refresh_token
    try:
        payload = decode_token(refresh_token)
        jti = payload["jti"]
        revoke_refresh_token(jti)
        return format_response("success", "success logout user", None)
    except:
        return format_response("failed", "token invalid", None)
        
@zerouser.get("/user-information")
def user_information():
    user = supabase.table("zerouser").select("user_id", count="exact").execute()
    get_level = supabase.table("zerostats").select("level,total_read", count="exact").execute()
    avg_level = 0
    total_read = 0
    for item in get_level.data:
        avg_level += item["level"]
        total_read += item["total_read"]
    data = [
        {"name": "Total User", "count": user.count},
        {"name": "Rata-rata Level", "count": avg_level},
        {"name": "Total Chapter Dibaca", "count": total_read},
    ]
    return format_response("success", "success login user", data)
    
@zerouser.post("/upload-profile")
async def upload_profile(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    MAX_UPLOAD_MB = 5
    ALLOWED_MIME = ["image/jpeg", "image/png", "image/webp"]

    user_id = user["user_id"]
    if not user_id:
        raise HTTPException(400, "Token payload must contain user id (sub/user_id/id)")

    content_type = file.content_type
    if content_type not in ALLOWED_MIME:
        raise HTTPException(400, "File harus berformat JPG/PNG/WEBP")

    file_bytes = await file.read()
    size_mb = len(file_bytes) / (1024 * 1024)
    if size_mb > MAX_UPLOAD_MB:
        raise HTTPException(400, f"File terlalu besar. Maks {MAX_UPLOAD_MB} MB")

    try:
        compressed = compress_image_bytes(file_bytes, max_size_kb=300, max_dim=400)
    except Exception as e:
        raise HTTPException(500, f"Gagal memproses gambar: {e}")

    filename = f"{user_id}/{user_id}-{uuid.uuid4().hex}.jpg"  # store in folder per user
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(filename, compressed, {"content-type": "image/jpeg"})
    except Exception as e:
        raise HTTPException(500, f"Gagal upload ke storage: {e}")

    try:
        resp = supabase.table("zerouser").select("user_id,avatar").eq("user_id", user_id).limit(1).execute()
        current_photo_path = resp.data[0]["avatar"]
        if current_photo_path and current_photo_path != filename:
            supabase.storage.from_(SUPABASE_BUCKET).remove([current_photo_path])
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename).get("publicURL") \
                     if isinstance(supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename), dict) \
                     else supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        update_resp = supabase.table("zerouser").upsert({"user_id": user_id, "avatar": public_url}).execute()
    except Exception as e:
        return {
            "status": "failed",
            "message": "upload succes but failed update data user",
            "data": {
                "url": public_url,
                "size_kb": round(len(compressed) / 1024, 2),
                "detail": str(e)
            }
        }

    return {
        "status": "success",
        "message": "success update avatar",
        "data": {
            "url": public_url,
            "size_kb": round(len(compressed) / 1024, 2)
        }
    }