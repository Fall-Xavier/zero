import asyncio,uuid, json, random

from app.providers.myanimelist import search_mal
from app.helpers.http_client import safe_get
from app.helpers.date_utils import time_now, convert_time, detect_update_day
    
async def bacakomik(page: int = 1):
    try:
        resp = await safe_get(f"https://omikbkversialter.click/?page=latest&paged={page}")
        if not resp:
            return []
            
        data = json.loads(resp.text)
        results = []
        for item in data:
            print(item["title"])
            readers = int(float(item["views"].split()[0]) * (1000 if "rb" in item["views"] else 1_000_000 if "jt" in item["views"] else 1) + random.randint(100, 999))
            detail = await detail_komik(item["url"], readers)
            
            chapters_time = [ch["chapter_update_at"] for ch in detail["chapters"]]
            most_day = detect_update_day(chapters_time)
            
            results.append({
                "komik_id": detail["komik_id"],
                "title": item["title"],
                "alternative_title": detail["alternative_title"],
                "release_year": detail["created_at"].split("-")[0],
                "release_year": most_day,
                "status": item["status"].lower(),
                "cover": detail["cover"],
                "type": item["type"].lower(),
                "country": "KR" if item["type"].lower() == "manhwa" else ("CN" if item["type"].lower() == "manhua" else "JP"),
                "rating": float(item["score"][:3] if len(item["score"]) > 2 else item["score"] + ".0"),
                "readers": readers,
                "bookmark": int(random.randint(1, readers)),
                "genres": detail["genres"],
                "author": detail["author"],
                "description": detail["description"],
                "chapters": detail["chapters"],
                "created_at": detail["created_at"],
                "updated_at": convert_time(item["data"]["time"]),
            })
        return results
    except Exception as e:
        return results 
        
async def detail_komik(url, readers):
    try:
        resp = await safe_get(url)
        data = json.loads(resp.text)[0]
        detail_mal = search_mal(data["title"])
        genres = []
        for c in ["genre", "demographic", "theme", "content"]:
            genres += [g["name"].lower() for g in data.get(c, []) if g.get("name", "").lower() != "n/a"]
        komik_id = str(uuid.uuid4())
        chapters = await detail_chapter(data["data"], readers, komik_id)
        return {
            "komik_id": komik_id,
            "alternative_title": detail_mal.get("alternative_title", ""),
            "cover": data.get("cover", ""),
            "genres": genres,
            "author": detail_mal.get("author", ""),
            "description": data.get("synopsis", ""),
            "chapters": chapters,
            "created_at": detail_mal.get("created_at", "")
        }
    except Exception as e:
        return {}
        
async def detail_chapter(data, readers, komik_id):
    try:
        chapter_readers = random.randint(100, 999) if readers < 10_000 else random.randint(1_000, 9_999) if readers < 100_000 else random.randint(10_000, 99_999) if readers < 1_000_000 else random.randint(100_000, 999_999)
        tasks = [extract_chapter_images(i["url"]) for i in data]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        chapters = []
        for item, extract in zip(data,results):
            if isinstance(extract, Exception) or not extract:
                continue
            chapters.append({
                "komik_id": komik_id,
                "chapter_id": str(uuid.uuid4()),
                "chapter_number": item.get("chapter",""),
                "chapter_readers": chapter_readers,
                "chapter_images": extract,
                "chapter_update_at": time_now(),
            })
        return chapters
    except Exception as e:
        return chapters
    
async def extract_chapter_images(url):
    try:
        resp = await safe_get(url)
        data = json.loads(resp.text)
        images = [img.replace("\\","") for img in data["image"]]
        return images
    except Exception as e:
        return images
