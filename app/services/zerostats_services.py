import uuid
from app.config.supabase import supabase

def create_stats(user_id: str):
    data = {
        "stats_id": str(uuid.uuid4()),
        "user_id": user_id,
        "title": [],
        "use_title": "",
        "level": 0,
        "exp": 0,
        "total_read": 0
    }
    supa = supabase.table("zerostats").insert(data).execute()
    print(supa.data)