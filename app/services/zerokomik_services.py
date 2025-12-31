import re
from rapidfuzz import fuzz

from app.schemas.zerokomik_schemas import KomikListResponse, Pagination, KomikSchema
from app.providers.shinigami import shinigami
from app.providers.bacakomik import bacakomik
from app.config.supabase import supabase
 
def normalize(text: str): 
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
    
def get_from_supabase(
    page: int,
    limit: int,
    query: str = None,
    sort_by: str = None,
    status: str = None
) -> KomikListResponse:
    try:
        from_index = (page - 1) * limit
        to_index = from_index + limit - 1
        supa_params = supabase.table("zerokomik").select("*", count="exact")

        if query:
            pattern = f"%{query}%"
            supa_params = supa_params.or_(
                f"title.ilike.{pattern},alternative_title.ilike.{pattern}"
            )
        if sort_by == "latest":
            supa_params = supa_params.order("updated_at", desc=True)
        elif sort_by == "popularity":
            supa_params = supa_params.order("readers", desc=True)
        if status:
            supa_params = supa_params.eq("status", status)

        supa = supa_params.range(from_index, to_index).execute()
        total_items = supa.count or 0
        total_pages = max(-(-total_items // limit), 1)

        return KomikListResponse(
            list=supa.data,
            pagination=Pagination(
                page=page,
                total_items=total_items,
                total_pages=total_pages,
                prev_page=page > 1,
                next_page=page < total_pages,
            )
        )

    except Exception as e:
        raise Exception(f" Service error: {str(e)}")
        
def get_detail_komik(komik_id):
    komik = supabase.table("zerokomik").select("*").eq("komik_id", komik_id).execute() 
    chapters = supabase.table("zerochapters").select("chapter_id, komik_id, chapter_number, chapter_readers, chapter_update_at").eq("komik_id", komik_id).execute()
    return {**komik.data[0], "chapters": chapters.data}
    
def get_chapter_komik(chapter_id):
    supa_chapter = supabase.table("zerochapters").select("*").eq("chapter_id", chapter_id).execute()
    this_chapter = supa_chapter.data[0]
    this_number = int(this_chapter["chapter_number"])
    
    supa = supabase.table("zerochapters").select("*").eq("komik_id", this_chapter["komik_id"]).order("chapter_update_at", desc=True).execute()
    pagination = {}
    for item in supa.data:
        if int(item["chapter_number"]) == this_number + 1:
            pagination.update({
                "next": {
                    "chapter_id": item["chapter_id"],
                    "chapter_number": item["chapter_number"],
                }
            })
        elif int(item["chapter_number"]) == this_number - 1:
            pagination.update({
                "prev": {
                    "chapter_id": item["chapter_id"],
                    "chapter_number": item["chapter_number"],
                }
            })
    
    return {**this_chapter, "pagination": pagination}

async def get_from_providers(page: int = 1):
    providers = [shinigami ]
    
    komik = []
    inserted, updated, error = 0, 0, 0
    for provider in providers:
        resp = await provider(page=page)
        if not resp:
            print(f" provider {provider} not return list")
            continue
            
        supa_list = supabase.table("zerokomik").select("*").execute()
        data_supabase = supa_list.data
        
        for item in resp:
            status = merge_komik(item, data_supabase)
            if status == "inserted":
                inserted += 1
            elif status == "updated":
                updated += 1
            else:
                error += 1
    return {"inserted": inserted, "updated": updated, "error": error}
        
        
def merge_komik(komik, supa):
    for item in supa:
        if fuzz.token_set_ratio(normalize(komik["title"]), normalize(item["title"])) > 80:
            print(f" komik already exists : {komik['title']}")
            save_chapters(item["komik_id"], komik["chapters"])
            return "updated"
            
    print(f" add komik : {komik['title']}")
    copy_komik = komik.copy()
    copy_komik.pop("chapters", None)
    
    if komik["created_at"] == "":
        copy_komik.pop("created_at", None)
        
    supabase.table("zerokomik").insert(copy_komik).execute()
    save_chapters(komik["komik_id"], komik["chapters"])
    return "inserted"
            
def save_chapters(komik_id, chapters):
    inserted = 0
    try:
        check_id = supabase.table("zerokomik").select("komik_id").eq("komik_id", komik_id).execute()
        if not check_id.data:
            print(f" skip {komik_id}: komik_id not found in zerokomik table")
            return 0

        existing_chapters = supabase.table("zerochapters").select("chapter_number").eq("komik_id", komik_id).execute()
        existing_number = {str(c["chapter_number"]).strip() for c in existing_chapters.data}
        
        new_chapters = []
        for chapter in chapters:
            chapter_num = str(chapter.get("chapter_number", "")).strip()
            if chapter_num not in existing_number:
                copy_chapter = chapter.copy()
                copy_chapter["komik_id"] = komik_id
                copy_chapter["chapter_number"] = chapter_num
                new_chapters.append(copy_chapter)

        if new_chapters:
            update = supabase.table("zerochapters").insert(new_chapters).execute()
            if hasattr(update, "error") and update.error:
                print(f" failed to insert chapter {komik_id}: {res.error}")
            else:
                inserted = len(new_chapters)
                print(f" {komik_id}: {inserted} new chapter saved")
        else:
            print(f" {komik_id}: all chapters are available")

    except Exception as e:
        print(f" failed to save chapter {komik_id}: {e}")

    return inserted
        
    