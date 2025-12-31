import uuid
from fastapi import APIRouter, Query, Body
from app.config.supabase import supabase
from app.helpers.date_utils import time_now
from app.helpers.response import format_response

zerobookmark = APIRouter(prefix="/bookmark")

@zerobookmark.get("/get")
def get_bookmark():
    try:
        supa = supabase.table("zerobookmark").select("*").eq("user_id", user_id).execute()
        return format_response("success", "success get bookmark from account", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerobookmark.post("/add")
def add_bookmark(
    user_id: str = Query(None),
    komik_id: str = Query(None),
    title: str = Query(None),
    cover: str = Query(None),
    last_chapter_id: str = Query(None),
    last_chapter_number: str = Query(None),
):
    try:
        supa = supabase.table("zerobookmark").insert({
            "bookmark_id": str(uuid.uuid4()),
            "user_id": user_id,
            "komik_id": komik_id,
            "title": title,
            "cover": cover,
            "last_chapter_id": chapter_id,
            "last_chapter_number": chapter_number,
        }).execute()
        return format_response("success", "success add bookmark", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerobookmark.delete("/delete")
def delete_bookmark(bookmark_id: str = Query(...)):
    try:
        supa = supabase.table("zerobookmark").delete().eq("bookmark_id", bookmark_id).execute()
        return format_response("success", "success delete bookmark", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)