import asyncio, json, random 

from app.helpers.http_client import safe_get
from app.helpers.date_utils import time_now, convert_time, detect_update_day

async def shinigami(page: int = 1):
    try:
        resp = await safe_get(f"https://api.shngm.io/v1/manga/list?page={page}&page_size=30&is_update=true&sort=latest&sort_order=desc")
        if not resp:
            return []

        data = resp.json()["data"]
        results = []

        for item in data:
            if "Shinigami" in item["title"]:
                continue

            genres = [g["slug"] for g in item["taxonomy"].get("Genre", [])]
            author = ",".join(a["name"] for a in item["taxonomy"].get("Author", []))
            chapters = await detail_chapter(item["manga_id"])
            
            chapters_time = [ch["chapter_update_at"] for ch in chapters]
            most_day = detect_update_day(chapters_time)
            
            results.append({
                "komik_id": item["manga_id"],
                "title": item["title"],
                "alternative_title": item["alternative_title"],
                "release_year": item["release_year"],
                "release_day": most_day,
                "status": (
                    "ongoing" if item["status"] == 1
                    else "completed" if item["status"] == 2
                    else "hiatus"
                ),
                "cover": item["cover_image_url"].replace(
                    "low/unsafe/filters:format(webp):quality(70)/", ""
                ),
                "type": (
                    "manhwa" if item["country_id"] == "KR"
                    else "manhua" if item["country_id"] == "CN"
                    else "manga"
                ),
                "country": item["country_id"],
                "rating": item["user_rate"],
                "readers": item["view_count"],
                "bookmark": item["bookmark_count"],
                "genres": genres,
                "author": author,
                "description": item["description"],
                "chapters": chapters,
                "created_at": item["created_at"],
                "updated_at": item["updated_at"],
            })

        return results
    except Exception as e:
        print(e)
        
async def detail_chapter(komik_id):
    try:
        resp = await safe_get(f"https://api.shngm.io/v1/chapter/{komik_id}/list?page=1&page_size=9999&sort_by=chapter_number&sort_order=desc")
        data = resp.json()["data"]

        tasks = [extract_chapter_images(i["chapter_id"]) for i in data]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        chapters = []
        for item, extract in zip(data, results):
            if isinstance(extract, Exception) or not extract:
                continue
            chapters.append({
                "komik_id": komik_id,
                "chapter_id": item["chapter_id"],
                "chapter_number": item["chapter_number"],
                "chapter_readers": item["view_count"],
                "chapter_images": extract,
                "chapter_update_at": item["release_date"],
            })
        return chapters
    except Exception as e:
        return chapters
        
async def extract_chapter_images(chapter_id):
    try:
        resp = await safe_get(f"https://api.shngm.io/v1/chapter/detail/{chapter_id}")
        data = resp.json()["data"]
        base_url = data["base_url"] + data["chapter"]["path"]
        images = [base_url + img for img in data["chapter"]["data"]]
        return images
    except Exception as e:
        return images

