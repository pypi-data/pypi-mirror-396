from typing import Optional, Dict, Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from enum import Enum
from fastapi.responses import JSONResponse

from .jkanime_v2 import (
    latest_anime_added,
    by_alphabet,
    search,
    schedule,
    top,
    get_extra_info,
    get_anime_servers,
    get_anime_directory,
    filter as filter_catalog,
)
from filoani import UnifiedAnimeAPI

class SeasonEnum(str, Enum):
    Primavera = "Primavera"
    Verano = "Verano"
    Otoño = "Otoño"
    Invierno = "Invierno"
    TemporadaActual = "Temporada Actual"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/latest")
def latest(provider: str = "jkanime") -> JSONResponse:
    if provider == "jkanime":
        return JSONResponse(latest_anime_added() or [])
    with UnifiedAnimeAPI(provider) as api:
        return JSONResponse(api.latest() or [])


@app.get("/alphabet/{letter}")
def alphabet(letter: str, provider: str = "jkanime") -> JSONResponse:
    if provider != "jkanime":
        return JSONResponse({"error": "alphabet no soportado", "provider": provider}, status_code=501)
    return JSONResponse(by_alphabet(letter) or [])


@app.get("/search")
def search_endpoint(q: str = Query(...), provider: str = "jkanime") -> JSONResponse:
    if provider == "jkanime":
        return JSONResponse(search(q) or {})
    with UnifiedAnimeAPI(provider) as api:
        return JSONResponse(api.search(q) or {})


@app.get("/filter")
def filter_endpoint(
    genre: Optional[str] = None,
    demography: Optional[str] = None,
    category: Optional[str] = None,
    type: Optional[str] = None,
    state: Optional[str] = None,
    year: Optional[str] = None,
    season: Optional[str] = None,
    orderBy: Optional[str] = None,
    provider: str = "jkanime",
) -> JSONResponse:
    query: Dict[str, Any] = {
        "genre": genre,
        "demography": demography,
        "category": category,
        "type": type,
        "state": state,
        "year": year,
        "season": season,
        "orderBy": orderBy,
    }
    if provider != "jkanime":
        return JSONResponse({"error": "filter no soportado", "provider": provider}, status_code=501)
    return JSONResponse(filter_catalog(query) or [])


@app.get("/extra/{slug}")
def extra(slug: str, provider: str = "jkanime") -> JSONResponse:
    if provider == "jkanime":
        return JSONResponse(get_extra_info(slug) or {"extra": None})
    with UnifiedAnimeAPI(provider) as api:
        return JSONResponse(api.extra(slug) or {})


@app.get("/top")
def top_endpoint(season: SeasonEnum, year: str, provider: str = "jkanime") -> JSONResponse:
    if provider != "jkanime":
        return JSONResponse({"error": "top no soportado", "provider": provider}, status_code=501)
    return JSONResponse(top(season.value.replace("TemporadaActual", "Temporada Actual"), year) or [])


@app.get("/schedule")
def schedule_endpoint(provider: str = "jkanime") -> JSONResponse:
    if provider != "jkanime":
        return JSONResponse({"error": "schedule no soportado", "provider": provider}, status_code=501)
    return JSONResponse(schedule())


@app.get("/servers/{slug}/{chapter}")
def servers(slug: str, chapter: int, provider: str = "jkanime") -> JSONResponse:
    if provider == "jkanime":
        return JSONResponse(get_anime_servers(slug, chapter) or [])
    with UnifiedAnimeAPI(provider) as api:
        return JSONResponse(api.servers(slug, chapter) or [])


@app.get("/directory/{page}")
def directory(page: Optional[int] = None, provider: str = "jkanime") -> JSONResponse:
    if provider != "jkanime":
        return JSONResponse({"error": "directory no soportado", "provider": provider}, status_code=501)
    return JSONResponse(get_anime_directory(page) or [])
@app.get("/unified/servers")
def unified_servers(title: str, episode: int, threshold: int = 92, validate: bool = False, timeout: int = 6) -> JSONResponse:
    with UnifiedAnimeAPI("jkanime") as api:
        merged = api.unified_servers(title, episode, threshold, validate, timeout)
        return JSONResponse(merged)
