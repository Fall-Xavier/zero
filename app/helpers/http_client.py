import httpx
import asyncio
import random
from typing import Optional, Dict

semaphore = asyncio.Semaphore(5)
client = httpx.AsyncClient(timeout=30)

async def safe_get(url: str):
    for attempt in range(1, 4):
        async with semaphore:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    return resp
                print(f"[{resp.status_code}] failed (percobaan {attempt}) → {url}")
            except Exception as e:
                print(f"[ERR GET] percobaan {attempt} → {url} → {e}")

        if attempt < 3:
            delay = random.uniform(1.0, 2.0)
            print(f"↻ retry after {delay:.1f}s...")
            await asyncio.sleep(delay)
    return None