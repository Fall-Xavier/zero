from fastapi import APIRouter, Query
from app.config.supabase import supabase
from app.services.zerokomik_services import get_from_supabase, get_detail_komik, get_chapter_komik, get_from_providers
from app.helpers.response import format_response
from app.schemas.zerokomik_schemas import KomikSchema, ChapterSchema

zerokomik = APIRouter(prefix="/komik")

@zerokomik.get("/list")
def list(
    page: int = Query(1),
    limit: int = Query(14),
    sort_by: str = Query("latest"),
    status: str = Query(None),
    query: str = Query(None),
):
    try:
        data = get_from_supabase(
            page=page,
            limit=limit,
            sort_by=sort_by,
            status=status,
            query=query
        )
        return format_response("success", "success get list from supabase", data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerokomik.get("/detail")
def detail_komik(
    komik_id: str = Query(None),
):
    try:
        data = get_detail_komik(komik_id)
        return format_response("success", "success get list from supabase", data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)

@zerokomik.get("/chapter")
def detail_chapter(
    chapter_id: str = Query(None)
):
    try:
        data = get_chapter_komik(chapter_id)
        return format_response("success", "success get list from supabase", data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
    
@zerokomik.get("/update-komik")
async def update_komik():
    try:
        page = 1
        data = await get_from_providers(page)
        return format_response("success", "success get list from providers", data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
        
@zerokomik.get("/update-all")
async def update_komik():
    try:
        inserted, updated = 0, 0
        for page in range(1,500):
            data = await get_from_providers(page)
            inserted += data["inserted"]
            updated += data["inserted"]
        total = {"inserted": inserted, "updated": updated}
        return format_response("success", "success get list from providers", total)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
    
@zerokomik.post("/add-komik")
async def add_komik_manual(body: KomikSchema):
    try:
        data = body.model_dump()
        data["komik_id"] = str(uuid.uuid4())
        supa = supabase.table("zerokomik").insert(data).execute()
        return format_response("success", "success add new komik", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
    
@zerokomik.delete("/delete-komik")
async def delete_komik_manual(komik_id: str = Query(None)):
    try:
        supa = supabase.table("zerokomik").delete().eq("komik_id", komik_id).execute()
        return format_response("success", "success delete komik", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
    
@zerokomik.post("/add-chapter")
async def add_chapter_manual(body: ChapterSchema):
    try:
        data = body.model_dump()
        data["chapter_id"] = str(uuid.uuid4())
        supa = supabase.table("zerochapters").insert(data).execute()
        return format_response("success", "success add new chapter", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
    
@zerokomik.delete("/delete-chapter")
async def delete_chapter_manual(chapter_id: str = Query(None)):
    try:
        supa = supabase.table("zerochapters").delete().eq("chapter_id", chapter_id).execute()
        return format_response("success", "success delete chapter", supa.data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
        
@zerokomik.get("/komik-information")
def komik_information():
    try:
        komik = supabase.table("zerokomik").select("komik_id", count="exact").execute()
        manhwa = supabase.table("zerokomik").select("komik_id", count="exact").eq("country", "KR").execute()
        manhua = supabase.table("zerokomik").select("komik_id", count="exact").eq("country", "CN").execute()
        manga = supabase.table("zerokomik").select("komik_id", count="exact").eq("country", "JP").execute()
        
        ongoing = supabase.table("zerokomik").select("komik_id", count="exact").eq("status", "ongoing").execute()
        completed = supabase.table("zerokomik").select("komik_id", count="exact").eq("status", "completed").execute()
        hiatus = supabase.table("zerokomik").select("komik_id", count="exact").eq("status", "hiatus").execute()
        data = [
            {"name": "Total Komik", "count": komik.count or 0},
            {"name": "Total Manhwa", "count": manhwa.count or 0},
            {"name": "Total Manhua", "count": manhua.count or 0},
            {"name": "Total Manga", "count": manga.count or 0},
            {"name": "Total Completed", "count": completed.count or 0},
            {"name": "Total Ongoing", "count": ongoing.count or 0},
            {"name": "Total Hiatus", "count": hiatus.count or 0},
        ]
        return format_response("success", "success get information", data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)
    
@zerokomik.get("/schedule")
def schedule_komik():
    try:
        data = []
        day_name = ["senin", "selasa", "rabu", "kamis", "jumat", "sabtu", "minggu"]
        for day in day_name:
            supa = supabase.table("zerokomik").select("*").eq("release_day", day).execute()
            data.append({"day": day, "list":supa.data})
        return format_response("success", "success get schedule", data)
    except Exception as e:
        return format_response("failed", f"error : {e}", None)