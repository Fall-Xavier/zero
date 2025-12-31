from fastapi import APIRouter, Query
from app.helpers.response import format_response

zerostats = APIRouter()

@zerostats.post("/up-level")
def up_level(
    user_id: str = Query(None),
    chapter: int = Query(None),
    comment: int = Query(None),
):
    exp_gain = 0
    if chapters:
        exp_gain += 20
    if comment:
        exp_gain += 10
        
    supa = supabase.table("zerostats").select("*").eq("user_id", user_id).execute()
    if not supa.data:
        return format_response("failed", "user not found", None)
    exp_now = supa.data[0]["exp"]
    level_now = supa.data[0]["level"]
    
    event = supabase.table("zeroevent").select("*").eq("type", "exp").execute()
    if event.data[0]["status"] == "active":
        exp_gain = exp_gain * 2
        
    exp_total = exp_now + exp_gain
    while True:
        required_exp = level_now * 200

        if exp_total >= required_exp:
            exp_total -= required_exp
            level_now += 1
        else:
            break
        
    supa_up = supabase.table("zerostats").update({"exp": total_exp, "level": level_now}).eq("user_id", user_id).execute()
    new_data = supabase.table("zerostats").select("*").eq("user_id", user_id).execute()
    return format_response("success", "exp update and level calculated", new_data.data)
    
@zerostats.post("/add-title")
def add_title(
    user_id: str = Query(None),
    title: str = Query(None),
):
    supa = supabase.table("zerostats").update({"title": title}).eq("user_id", user_id).execute()
    if not supa.data:
        return format_response("failed", "user not found", None)
    return format_response("success", f"success add title {title}", supa.data)

@zerostats.delete("/remove-title")
def remove_title(
    user_id: str = Query(None),
    title: str = Query(None)
):
    supa = supabase.table("zerostats").select("title").eq("user_id", user_id).execute()
    if not supa.data:
        return format_response("failed", "user not found", None)
    list_title = supa.data[0].get("title", [])
    new_titles = [t for t in list_title if t != title]
    
    update = supabase.table("zerostats").update({"title": new_titles}).eq("user_id", user_id).execute()
    return format_response("success", f"success removed title {remove_title}", update.data)
    
@zerostats.post("/add-read")
def add_read(
    user_id: str = Query(None),
):
    supa = supabase.table("zerostats").select("total_read").eq("user_id", user_id).execute()
    if not supa.data:
        return format_response("failed", "user not found", None)
    total_read = supa.data[0] + 1
    update = supabase.table("zerostats").update({"total_read": total_read}).eq("user_id", user_id).execute()
    return format_response("success", f"success add 1 total read", update.data)
    
"""
create table zerostats (
  stats_id text primary key,
  user_id text references zeroauth(user_id) on delete cascade,
  title text[],
  user_title text,
  level int8,
  exp int8,
  total_read int8,
);"""