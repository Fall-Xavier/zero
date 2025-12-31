import re, requests, json
from rapidfuzz import fuzz

ses = requests.Session()

def normalize(text: str): 
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

def detail(manga_id: int):
    response = ses.get(f"https://api.jikan.moe/v4/manga/{manga_id}")
    data = response.json()["data"]
    detail = {}
    
    all_title = []
    for title in data["titles"]:
        if title["type"] == "English":
            all_title.append(title["title"])
        elif title["type"] == "Japanese":
            all_title.append(title["title"])
    detail["alternative_title"] = ",".join(title for title in all_title)
    
    published = data["published"]["from"]
    detail["created_at"] = published.split("+")[0]+"Z"
    detail["author"] = ",".join(a["name"] for a in data["authors"])
    return detail


def search_mal(keyword: str):
    res = ses.get(f"https://myanimelist.net/search/prefix.json?type=manga&keyword={keyword}&v=1")
    data = res.json()

    for item in data.get("categories", []):
        if item["type"] == "manga":
            for manga in item["items"]:
                if fuzz.token_set_ratio(normalize(keyword), normalize(manga["name"])) > 80:
                    #print(" cocok : "+manga["name"])
                    return detail(manga["id"])
                else:
                    print(" tidak cocok : "+manga["name"])

    print(" tidak ada yang cocok")
    return {"alternative_title": "", "author": "", "created_at": ""}
    
#search("Solo Leveling Ragnarok")