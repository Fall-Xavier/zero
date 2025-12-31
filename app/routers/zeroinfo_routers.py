import uuid
from fastapi import APIRouter, Query, Body
from app.config.supabase import supabase
from app.helpers.date_utils import time_now

zeroinfo = APIRouter(prefix="/info")

@zeroinfo.get("/get")
def get_info():
    try:
        supa = supabase.table("zeroinfo").select("*").execute()
        return format_response("success", "success get history from account", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zeroinfo.post("/add")
def add_info(
    info_title: str = Query(None),
    info_text: str = Query(None),
):
    try:
        supa = supabase.table("zeroinfo").insert({
            "info_id": str(uuid.uuid4()),
            "info_title": info_title,
            "info_text": info_text,
            "info_created_at": time_now(),
        }).execute()
        return format_response("success", "success get history from account", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zeroinfo.delete("/delete")
def delete_info(info_id: str = Query(...)):
    try:
        supa = supabase.table("zeroinfo").delete().eq("info_id", info_id).execute()
        return format_response("success", "success get history from account", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)