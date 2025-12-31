from PIL import Image
from io import BytesIO

def convert_to_jpeg(img: Image.Image) -> Image.Image:
    if img.mode in ("RGBA", "LA"):
        # convert transparent backgrounds to white
        background = Image.new("RGB", img.size, (255, 255, 255))
        background.paste(img, mask=img.split()[-1])  # paste using alpha channel
        return background
    return img.convert("RGB")

def compress_image_bytes(file_bytes: bytes, max_size_kb: int = 300, max_dim: int = 400) -> bytes:
    img = Image.open(BytesIO(file_bytes))
    img = convert_to_jpeg(img)

    img.thumbnail((max_dim, max_dim))

    quality = 85
    buffer = BytesIO()
    while True:
        buffer.seek(0)
        buffer.truncate()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        size_kb = len(buffer.getvalue()) / 1024
        if size_kb <= max_size_kb or quality <= 20:
            break
        quality -= 5

    return buffer.getvalue()
    
    
# main.py
import uuid
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .config import supabase, SUPABASE_BUCKET
from .auth import get_current_user
from .compress import compress_image_bytes
from typing import Optional

app = FastAPI(title="Profile Photo Upload - Supabase")

# CORS - sesuaikan origin dengan frontend kamu
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_UPLOAD_MB = 5  # batas maksimal upload dari client (safety)
ALLOWED_MIME = ["image/jpeg", "image/png", "image/webp"]


@app.post("/upload-profile")
async def upload_profile(
    file: UploadFile = File(...),
    authorization_payload: dict = Depends(get_current_user),
):
    user_id = authorization_payload.get("sub") or authorization_payload.get("user_id") or authorization_payload.get("id")
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

    # Build filename and upload
    filename = f"{user_id}/{user_id}-{uuid.uuid4().hex}.jpg"  # store in folder per user
    try:
        supabase.storage.from_(SUPABASE_BUCKET).upload(filename, compressed, {"content-type": "image/jpeg"})
    except Exception as e:
        raise HTTPException(500, f"Gagal upload ke storage: {e}")

    try:
        resp = supabase.table("zerouser").select("user_id,avatar").eq("user_id", user_id).limit(1).execute()
        current_photo_path = None
        if resp and getattr(resp, "data", None) is not None:
            data = resp.data
            if data and len(data) > 0:
                current_photo_path = data[0].get("avatar")

        if current_photo_path and current_photo_path != filename:
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([current_photo_path])
            except Exception:
                pass
        # 3) Update users table with new path and public url
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename).get("publicURL") \
                     if isinstance(supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename), dict) \
                     else supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        # Attempt to be robust: some clients return dict { "publicURL": "..."} others return string
        # Upsert user row (if user exists update, otherwise insert minimal)
        update_resp = supabase.table("zerouser").upsert({"user_id": user_id, "avatar": public_url}).execute()
    except Exception as e:
        return {
            "status": "warning",
            "message": "Upload berhasil tetapi gagal update data user",
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