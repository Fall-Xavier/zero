from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.zerokomik_routers import zerokomik
from app.routers.zerouser_routers import zerouser
from app.routers.zerohistory_routers import zerohistory
from app.routers.zerobookmark_routers import zerobookmark
from app.routers.zeronews_routers import zeronews
from app.routers.zeroinfo_routers import zeroinfo
from app.routers.zerostats_routers import zerostats

tags_metadata = [
    {
        "name": "Zero API",
        "description": "API for get and save komik to your database. Built with simple code FastAPI."
    }
]

app = FastAPI(
    title="Zero API",
    description="API for get and save komik to your database. Built with simple code FastAPI..",
    summary="A Python-based scraping/proxy API for komik.",
    version="1.0.0",
    openapi_tags=tags_metadata,
    redoc_url=None,
    docs_url=None,
)

origins = [
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(zerokomik)
app.include_router(zerouser)
app.include_router(zerohistory)
app.include_router(zerobookmark)
app.include_router(zeronews)
app.include_router(zeroinfo)
app.include_router(zerostats)