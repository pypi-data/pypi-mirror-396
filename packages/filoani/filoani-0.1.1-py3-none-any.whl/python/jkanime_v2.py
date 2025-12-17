import os
import time
import random
import re
from typing import Any, Dict, List, Optional, Generator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util retry import Retry
from urllib.parse import urlencode
from bs4 import BeautifulSoup


BASE_URL = os.getenv("JKANIME_BASE_URL", "https://jkanime.net/")
REMOTE_SERVER_URL = os.getenv("JKANIME_REMOTE_SERVER_URL", "https://c4.jkdesu.com")

_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/119.0 Safari/537.36",
]

_REQUEST_MIN_INTERVAL = 0.2
_last_request_time: float = 0.0
_CACHE_TTL = int(os.getenv("JKANIME_CACHE_TTL", "60"))
_cache: Dict[str, Dict[str, Any]] = {}

_session = requests.Session()
_adapter = HTTPAdapter(max_retries=Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]))
_session.mount("https://", _adapter)
_session.mount("http://", _adapter)


def _make_request(url: str, response_type: str = "json", method: str = "get") -> Any:
    global _last_request_time
    method_up = method.upper()
    now = time.monotonic()
    if method_up == "GET":
        delta = now - _last_request_time
        if delta < _REQUEST_MIN_INTERVAL:
            time.sleep(_REQUEST_MIN_INTERVAL - delta)
        _last_request_time = time.monotonic()

        cache_key = f"{method_up}:{response_type}:{url}"
        entry = _cache.get(cache_key)
        if entry:
            if (time.monotonic() - entry["ts"]) <= _CACHE_TTL:
                return entry["data"]

    headers = {
        "User-Agent": random.choice(_USER_AGENTS),
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    try:
        r = _session.request(method_up, url, timeout=30, headers=headers)
        r.raise_for_status()
        data = r.json() if response_type == "json" else r.text
        if method_up == "GET":
            _cache[cache_key] = {"ts": time.monotonic(), "data": data}
        return data
    except Exception:
        return None


def _build_query(obj: Dict[str, Any]) -> str:
    return urlencode({k: v for k, v in obj.items() if v is not None and v != ""}, doseq=True)


def _extract_number_from_string(s: Any) -> Optional[int]:
    if s is None:
        return None
    m = re.search(r"\d+", str(s))
    return int(m.group(0)) if m else None


GENRE_MAP = [
    "accion",
    "aventura",
    "autos",
    "comedia",
    "dementia",
    "demonios",
    "misterio",
    "drama",
    "ecchi",
    "fantasia",
    "juegos",
    "hentai",
    "historico",
    "terror",
    "magia",
    "artes-marciales",
    "mecha",
    "musica",
    "parodia",
    "samurai",
    "romance",
    "colegial",
    "sci-fi",
    "shoujo-ai",
    "shounen-ai",
    "space",
    "deportes",
    "super-poderes",
    "vampiros",
    "yaoi",
    "yuri",
    "harem",
    "cosas-de-la-vida",
    "sobrenatural",
    "militar",
    "policial",
    "psicologico",
    "thriller",
    "espaol-latino",
    "isekai",
]

DEMOGRAPHY_MAP = ["nios", "shoujo", "shounen", "seinen", "josei"]

CATEGORY_MAP = ["donghua"]

TYPES_MAP = ["animes", "peliculas", "especiales", "ovas", "onas"]

STATE_MAP = ["emision", "finalizados", "estrenos"]

YEAR_MAP = [
    "2024",
    "2023",
    "2022",
    "2021",
    "2020",
    "2019",
    "2018",
    "2017",
    "2016",
    "2015",
    "2014",
    "2013",
    "2012",
    "2011",
    "2010",
    "2009",
    "2008",
    "2007",
    "2006",
    "2005",
    "2004",
    "2003",
    "2002",
    "2001",
    "2000",
    "1999",
    "1998",
    "1997",
    "1996",
    "1995",
    "1994",
    "1993",
    "1992",
    "1991",
    "1990",
    "1989",
    "1988",
    "1987",
    "1986",
    "1985",
    "1984",
    "1983",
    "1982",
    "1981",
]

SEASON_MAP = ["invierno", "primavera", "verano", "otoño"]

ORDERBY_MAP = ["desc"]


def latest_anime_added() -> Optional[List[Dict[str, Any]]]:
    html = _make_request(BASE_URL, "text", "get")
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    containers = soup.select("div.trending__anime div:nth-of-type(1)")
    results = []
    for idx, el in enumerate(containers):
        if idx % 2 == 0:
            continue
        inner = BeautifulSoup(str(el), "html.parser")
        title = inner.select_one(".anime__item .anime__item__text h5 a")
        slug_a = inner.select_one(".anime__item a:nth-of-type(1)")
        image = inner.select_one(".anime__item .anime__item__pic")
        type_el = inner.select_one(".anime__item__text ul li.anime")
        status_el = inner.select_one(".anime__item__text ul li")
        results.append(
            {
                "slug": (slug_a["href"].strip("/") if slug_a and slug_a.has_attr("href") else None),
                "title": (title.text.strip() if title else None),
                "synopsis": None,
                "episodes": None,
                "image": (image.get("data-setbg") if image else None),
                "type": (type_el.text.strip() if type_el else None),
                "status": (status_el.text.strip() if status_el else None),
            }
        )
    return [a for a in results if a.get("slug")]


def by_alphabet(letter: str) -> Optional[List[Dict[str, Any]]]:
    url = f"{BASE_URL}letra/{letter}"
    all_info: List[Dict[str, Any]] = []
    while url:
        html = _make_request(url, "text", "get")
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        items = soup.select(".row .anime__item")
        for el in items:
            a = el.select_one("a")
            title = el.select_one("a")
            pic = el.select_one(".anime__item__pic")
            type_el = el.select_one(".anime__item__text .anime")
            status_el = el.select_one(".anime__item__text ul li:nth-of-type(1)")
            style = pic.get("style") if pic else ""
            m = re.search(r"url\((['\"]?)(.*?)\1\)", style or "")
            thumb = m.group(2) if m else ""
            href = a.get("href") if a else None
            slug = href.split("/")[-1] if href else None
            all_info.append(
                {
                    "slug": slug,
                    "title": (title.text.strip() if title else None),
                    "thumbnail": thumb or None,
                    "type": (type_el.text.strip() if type_el else None),
                    "status": (status_el.text.strip() if status_el else None),
                }
            )
        next_link = soup.select_one(".text.nav-next")
        url = next_link.get("href") if next_link and next_link.has_attr("href") else None
    return all_info


def iter_by_alphabet(letter: str) -> Generator[List[Dict[str, Any]], None, None]:
    url = f"{BASE_URL}letra/{letter}"
    while url:
        html = _make_request(url, "text", "get")
        if not html:
            return
        soup = BeautifulSoup(html, "html.parser")
        page_info: List[Dict[str, Any]] = []
        items = soup.select(".row .anime__item")
        for el in items:
            a = el.select_one("a")
            title = el.select_one("a")
            pic = el.select_one(".anime__item__pic")
            type_el = el.select_one(".anime__item__text .anime")
            status_el = el.select_one(".anime__item__text ul li:nth-of-type(1)")
            style = pic.get("style") if pic else ""
            m = re.search(r"url\((['\"]?)(.*?)\1\)", style or "")
            thumb = m.group(2) if m else ""
            href = a.get("href") if a else None
            slug = href.split("/")[-1] if href else None
            page_info.append({
                "slug": slug,
                "title": (title.text.strip() if title else None),
                "thumbnail": thumb or None,
                "type": (type_el.text.strip() if type_el else None),
                "status": (status_el.text.strip() if status_el else None),
            })
        yield page_info
        next_link = soup.select_one(".text.nav-next")
        url = next_link.get("href") if next_link and next_link.has_attr("href") else None


def search(q: str) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}ajax/ajax_search/?{_build_query({'q': q})}"
    data = _make_request(url, "json", "get")
    return data or None


def schedule() -> List[Dict[str, Any]]:
    url = f"{BASE_URL}horario"
    html = _make_request(url, "text", "get")
    soup = BeautifulSoup(html, "html.parser")
    days = [
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    ]
    boxes = soup.select("div.app-layout div.box.semana")
    result: List[Dict[str, Any]] = []
    for i, day in enumerate(days):
        box = boxes[i] if i < len(boxes) else None
        if not box:
            result.append({"day": day, "animes": []})
            continue
        inner = BeautifulSoup(str(box), "html.parser")
        entries = inner.select("div.cajas div.box")
        animes: List[Dict[str, Any]] = []
        for el in entries:
            h3 = el.select_one("h3")
            parent_a = h3.parent if h3 else None
            href = parent_a.get("href") if parent_a and parent_a.has_attr("href") else None
            last_span = el.select_one(".last span")
            last_text = last_span.text.strip() if last_span else ""
            parts = [p.strip() for p in last_text.split(":")]
            last_episode = parts[1] if len(parts) > 1 else None
            animes.append(
                {
                    "id": (el.select_one("#guardar-anime").get("data-anime") if el.select_one("#guardar-anime") else None),
                    "slug": (href.replace("/", "") if href else None),
                    "title": (h3.text.strip() if h3 else None),
                    "image": (el.select_one("img").get("src") if el.select_one("img") else None),
                    "lastEpisode": last_episode,
                    "timestamp": (el.select_one(".last time").text.strip() if el.select_one(".last time") else None),
                    "type": (el.select_one("#guardar-anime").get("data-tipo") if el.select_one("#guardar-anime") else None),
                }
            )
        result.append({"day": day, "animes": animes})
    return result


def top(season: str, year: str) -> Optional[List[Dict[str, Any]]]:
    if season == "Temporada Actual":
        url = f"{BASE_URL}top"
    else:
        url = f"{BASE_URL}top?{_build_query({'temporada': season, 'fecha': year})}"
    html = _make_request(url, "text", "get")
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("div.list")
    data: List[Dict[str, Any]] = []
    for el in items:
        inner = BeautifulSoup(str(el), "html.parser")
        title_el = inner.select_one("h5 a")
        slug_el = inner.select_one("a")
        synopsis_el = inner.select_one("p")
        image_el = inner.select_one("img")
        type_el = inner.select_one(".anime")
        episodes_el = inner.select_one(".ep")
        episodes = _extract_number_from_string(episodes_el.text if episodes_el else None)
        href = slug_el.get("href") if slug_el else None
        slug = href.strip("/") if href else None
        data.append(
            {
                "id": None,
                "slug": slug,
                "title": (title_el.text.strip() if title_el else None),
                "synopsis": (synopsis_el.text.strip() if synopsis_el else None),
                "episodes": episodes,
                "image": (image_el.get("src") if image_el else None),
                "type": (type_el.text.strip() if type_el else None),
            }
        )
    return data


def get_extra_info(anime_slug: str) -> Optional[Dict[str, Any]]:
    url = f"{BASE_URL}{anime_slug}"
    html = _make_request(url, "text", "get")
    if not html:
        return {"extra": None}
    soup = BeautifulSoup(html, "html.parser")
    ul = soup.select_one(".aninfo ul")
    extra: Dict[str, Any] = {}
    if ul:
        for li in ul.select("li"):
            span = li.select_one("span")
            key = span.text.strip().replace(":", "").lower() if span else ""
            eng = {
                "tipo": "type",
                "genero": "genre",
                "studios": "studios",
                "demografia": "demography",
                "idiomas": "languages",
                "episodios": "episodes",
                "duracion": "duration",
                "emitido": "aired",
                "estado": "status",
                "calidad": "quality",
                "promo": "promo",
            }.get(key, key)
            if key in {"genero", "studios", "demografia"}:
                values = [a.text.strip() for a in li.select("a")]
                extra[eng] = values
            else:
                val_text = li.get_text(separator=" ", strip=True)
                base_text = val_text.replace(span.text, "").strip() if span else val_text
                if re.fullmatch(r"\d+", base_text or ""):
                    num = int(base_text)
                    extra[eng] = num
                    extra["episodeList"] = [{"key": anime_slug, "value": i + 1} for i in range(num)]
                else:
                    extra[eng] = base_text or None
            if key == "estado" and not extra.get(eng):
                next_text = span.find_next(string=True) if span else None
                extra[eng] = next_text.strip() if isinstance(next_text, str) else None
            if extra.get(eng) is None:
                extra[eng] = None
    promo_el = soup.select_one(".animeTrailer")
    promo_id = promo_el.get("data-yt") if promo_el and promo_el.has_attr("data-yt") else None
    extra["promo"] = f"https://youtube.com/watch?v={promo_id}" if promo_id else None
    return {"extra": extra}


def get_anime_servers(anime_id: str, chapter: int) -> Optional[List[str]]:
    url = f"{BASE_URL}{anime_id}/{chapter}"
    html = _make_request(url, "text", "get")
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    scripts = soup.find_all("script")
    text = "".join(s.get_text() for s in scripts)
    m = re.search(r"var\s+servers\s*=\s*(\[.*?\]);", text, re.S)
    if not m:
        return None
    servers_json = m.group(1)
    try:
        import json
        servers = json.loads(servers_json)
    except Exception:
        return None
    urls = []
    for s in servers:
        remote = s.get("remote")
        server = (s.get("server") or "").lower()
        q = _build_query({"u": remote, "s": server})
        urls.append(f"https://jkanime.net/c1.php?{q}")
    return urls


def get_anime_directory(pagination_number: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
    url = f"{BASE_URL}/directorio/{pagination_number}"
    html = _make_request(url, "text", "get")
    if not html:
        return None
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("div.row.row-cols-md-3.custom_flex.page_directorio .card.mb-3.custom_item2")
    data: List[Dict[str, Any]] = []
    for el in cards:
        inner = BeautifulSoup(str(el), "html.parser")
        title_el = inner.select_one(".card-title a")
        slug_el = inner.select_one(".card-title span a")
        amount_ep_el = inner.select_one(".card-text.ep")
        started_el = inner.select_one(".card-text.ep small")
        status_el = inner.select_one(".card-status")
        type_el = inner.select_one(".card-txt")
        synopsis_el = inner.select_one(".card-text.synopsis")
        image_el = inner.select_one(".custom_thumb2 img")
        amount_ep = None
        if amount_ep_el:
            t = amount_ep_el.text.strip().split(" ")
            amount_ep = t[0] if t else None
        data.append(
            {
                "title": (title_el.get("title") if title_el and title_el.has_attr("title") else None),
                "slug": (slug_el.get("href") if slug_el and slug_el.has_attr("href") else None),
                "amountEpisodes": amount_ep,
                "startedEmision": (started_el.text.strip() if started_el else None),
                "statusEmision": (status_el.text.strip() if status_el else None),
                "type": (type_el.text.strip() if type_el else None),
                "synopsis": (synopsis_el.text.strip() if synopsis_el else None),
                "image": (image_el.get("src") if image_el else None),
            }
        )
    return [a for a in data if a.get("slug")]


def _apply_filter_path(query: Optional[Dict[str, str]]) -> str:
    if not query:
        return ""
    path_parts: List[str] = []
    if (g := query.get("genre")) in GENRE_MAP:
        path_parts.append(g)
    if (d := query.get("demography")) in DEMOGRAPHY_MAP:
        path_parts.append(d)
    if (c := query.get("category")) in CATEGORY_MAP:
        path_parts.append(c)
    if (t := query.get("type")) in TYPES_MAP:
        path_parts.append(t)
    if (s := query.get("state")) in STATE_MAP:
        path_parts.append(s)
    if (y := query.get("year")) in YEAR_MAP:
        path_parts.append(y)
    if (sn := query.get("season")) in SEASON_MAP:
        path_parts.append(sn)
    if (ob := query.get("orderBy")) in ORDERBY_MAP:
        path_parts.append(ob)
    return "/".join([p for p in path_parts if p])


def filter(query: Optional[Dict[str, str]] = None) -> Optional[List[Dict[str, Any]]]:
    applied = _apply_filter_path(query)
    next_url: Optional[str] = f"{BASE_URL}directorio/{applied}"
    all_info: List[Dict[str, Any]] = []
    while next_url:
        html = _make_request(next_url, "text", "get")
        if not html:
            return None
        soup = BeautifulSoup(html, "html.parser")
        container = soup.select_one(".row .page_directorio")
        if container:
            for card in container.select(".card"):
                card_title_a = card.select_one(".card-title a")
                image_el = card.select_one(".img-fluid")
                synopsis_el = card.select_one(".synopsis")
                type_el = card.select_one("p.card-txt")
                p_text = card.select_one(".card-body p")
                episodes = None
                if p_text and p_text.text:
                    episodes = (p_text.text.split(",")[0]).strip()
                href = card_title_a.get("href") if card_title_a and card_title_a.has_attr("href") else None
                slug = href.split("/")[-1] if href else None
                all_info.append(
                    {
                        "title": (card_title_a.get("title") if card_title_a and card_title_a.has_attr("title") else None),
                        "slug": slug,
                        "image": (image_el.get("src") if image_el else None),
                        "synopsis": (synopsis_el.text.strip() if synopsis_el else None),
                        "type": (type_el.text.strip() if type_el else None),
                        "episodes": episodes,
                    }
                )
        next_link = soup.select_one(".text.nav-next")
        next_url = next_link.get("href") if next_link and next_link.has_attr("href") else None
    return all_info


def iter_filter(query: Optional[Dict[str, str]] = None) -> Generator[List[Dict[str, Any]], None, None]:
    applied = _apply_filter_path(query)
    next_url: Optional[str] = f"{BASE_URL}directorio/{applied}"
    while next_url:
        html = _make_request(next_url, "text", "get")
        if not html:
            return
        soup = BeautifulSoup(html, "html.parser")
        page_info: List[Dict[str, Any]] = []
        container = soup.select_one(".row .page_directorio")
        if container:
            for card in container.select(".card"):
                card_title_a = card.select_one(".card-title a")
                image_el = card.select_one(".img-fluid")
                synopsis_el = card.select_one(".synopsis")
                type_el = card.select_one("p.card-txt")
                p_text = card.select_one(".card-body p")
                episodes = None
                if p_text and p_text.text:
                    episodes = (p_text.text.split(",")[0]).strip()
                href = card_title_a.get("href") if card_title_a and card_title_a.has_attr("href") else None
                slug = href.split("/")[-1] if href else None
                page_info.append({
                    "title": (card_title_a.get("title") if card_title_a and card_title_a.has_attr("title") else None),
                    "slug": slug,
                    "image": (image_el.get("src") if image_el else None),
                    "synopsis": (synopsis_el.text.strip() if synopsis_el else None),
                    "type": (type_el.text.strip() if type_el else None),
                    "episodes": episodes,
                })
        yield page_info
        next_link = soup.select_one(".text.nav-next")
        next_url = next_link.get("href") if next_link and next_link.has_attr("href") else None


__all__ = [
    "latest_anime_added",
    "by_alphabet",
    "iter_by_alphabet",
    "search",
    "schedule",
    "top",
    "get_extra_info",
    "get_anime_servers",
    "get_anime_directory",
    "filter",
    "iter_filter",
]

