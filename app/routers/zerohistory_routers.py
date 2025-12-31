import uuid
from fastapi import APIRouter, Query, Body
from app.config.supabase import supabase
from app.helpers.date_utils import time_now
from app.helpers.response import format_response

zerohistory = APIRouter(prefix="/history")

@zerohistory.get("/get")
def get_history():
    try:
        supa = supabase.table("zerohistory").select("*").eq("user_id", user_id).execute()
        return format_response("success", "success get history from account", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerohistory.post("/add")
def add_history(
    user_id: str = Query(None),
    komik_id: str = Query(None),
    title: str = Query(None),
    cover: str = Query(None),
    chapter_id: str = Query(None),
    chapter_number: str = Query(None),
):
    try:
        supa = supabase.table("zerohistory").insert({
            "history_id": str(uuid.uuid4()),
            "user_id": user_id,
            "komik_id": komik_id,
            "title": title,
            "cover": cover,
            "chapter_id": chapter_id,
            "chapter_number": chapter_number,
            "update_at": time_now(),
        }).execute()
        return format_response("success", "success add history", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerohistory.delete("/delete")
def delete_history(history_id: str = Query(...)):
    try:
        supa = supabase.table("zerohistory").delete().eq("history_id", history_id).execute()
        return format_response("success", "success delete history", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)