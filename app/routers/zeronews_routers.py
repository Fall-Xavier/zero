import uuid
from fastapi import APIRouter, Query, Body
from app.config.supabase import supabase
from app.helpers.date_utils import time_now

zeronews = APIRouter(prefix="/news")

@zeronews.get("/get")
def get_news():
    try:
        supa = supabase.table("zeronews").select("*").execute()
        return format_response("success", "success get news", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zeronews.post("/add")
def add_news(
    news_title: str = Query(None),
    news_text: str = Query(None),
    news_cover: str = Query(None),
    news_source: str = Query(None)
):
    try:
        supa = supabase.table("zeronews").insert({
            "news_id": str(uuid.uuid4()),
            "news_title": news_title,
            "news_text": news_text,
            "news_cover": news_cover,
            "news_source": news_source,
            "news_created_at": time_now(),
        }).execute()
        return format_response("success", "success add news", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zeronews.delete("/delete")
def delete_news(news_id: str = Query(...)):
    try:
        supa = supabase.table("zeronews").delete().eq("news_id", news_id).execute()
        return format_response("success", "success delete news", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)