from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlsplit, parse_qs, urlunsplit, urlencode
import requests
import re

from jkanime import JkAnime


def _call_any(obj: Any, names: List[str], *args, **kwargs):
    for n in names:
        if hasattr(obj, n):
            fn = getattr(obj, n)
            try:
                return fn(*args, **kwargs)
            except Exception:
                continue
    return None


def _normalize_title(t: str) -> str:
    t = t.lower()
    t = re.sub(r"\([^)]*\)", "", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _fuzzy_match(a: str, b: str, threshold: int = 90) -> bool:
    try:
        from rapidfuzz.fuzz import ratio
        return ratio(_normalize_title(a), _normalize_title(b)) >= threshold
    except Exception:
        return _normalize_title(a) == _normalize_title(b)


def _canonical_url(u: str) -> str:
    parts = urlsplit(u)
    qs = parse_qs(parts.query, keep_blank_values=True)
    # Ordena parámetros para una comparación estable
    new_qs = urlencode(sorted([(k, v if isinstance(v, list) else [v]) for k, v in qs.items()]), doseq=True)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, new_qs, parts.fragment))


def _jk_servers_struct(urls: List[str]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for u in urls or []:
        parts = urlsplit(u)
        qs = parse_qs(parts.query)
        server = (qs.get("s", ["unknown"]) or ["unknown"])[0]
        remote = (qs.get("u", [None]) or [None])[0]
        out.append({
            "provider": "jkanime",
            "server": server,
            "url": u,
            "remote": remote,
        })
    return out


def _aflv_servers_struct(raw: Any) -> List[Dict[str, Any]]:
    servers: List[Dict[str, Any]] = []
    if isinstance(raw, list):
        for item in raw:
            if isinstance(item, dict):
                url = item.get("url") or item.get("embed") or item.get("link") or item.get("src")
                servers.append({
                    "provider": "animeflv",
                    "server": item.get("server") or item.get("name") or "unknown",
                    "url": url,
                    "quality": item.get("quality"),
                    "lang": item.get("lang"),
                })
    elif isinstance(raw, dict):
        for k, v in raw.items():
            if isinstance(v, str):
                servers.append({"provider": "animeflv", "server": k, "url": v})
            elif isinstance(v, dict):
                url = v.get("url") or v.get("embed")
                servers.append({"provider": "animeflv", "server": k, "url": url})
    return [s for s in servers if s.get("url")]


def _dedupe_servers(servers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for s in servers:
        key = (s.get("server") or "unknown", _canonical_url(s.get("url") or ""))
        if key not in seen:
            seen[key] = s
    return list(seen.values())


def _is_url_alive(url: str, timeout: int = 6) -> bool:
    if not url or url.startswith("data:"):
        return False
    try:
        r = requests.head(url, timeout=timeout, allow_redirects=True)
        if 200 <= r.status_code < 300:
            return True
    except Exception:
        pass
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True, stream=True)
        if 200 <= r.status_code < 300:
            return True
    except Exception:
        pass
    return False


class UnifiedAnimeAPI:
    def __init__(self, provider: str = "jkanime"):
        self.provider = provider.lower()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def _jk(self) -> JkAnime:
        return JkAnime()

    def _aflv(self):
        try:
            from animeflv import AnimeFLV
        except Exception:
            return None
        return AnimeFLV()

    def latest(self) -> Optional[List[Dict[str, Any]]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.latest()
        af = self._aflv()
        if not af:
            return None
        with af as api:
            return _call_any(api, ["new_releases", "get_new_releases", "latest"]) or []

    def search(self, q: str) -> Optional[Dict[str, Any]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.search(q)
        af = self._aflv()
        if not af:
            return None
        with af as api:
            return _call_any(api, ["search"], q)

    def extra(self, slug: str) -> Optional[Dict[str, Any]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.extra(slug)
        af = self._aflv()
        if not af:
            return None
        with af as api:
            return _call_any(api, ["anime_info", "get_anime_info", "info"], slug)

    def servers(self, slug: str, chapter: int) -> Optional[List[str]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.servers(slug, chapter)
        af = self._aflv()
        if not af:
            return None
        with af as api:
            return _call_any(api, ["get_video_servers", "get_servers", "video_servers"], slug, chapter)

    def top(self, season: str, year: str) -> Optional[List[Dict[str, Any]]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.top(season, year)
        return None

    def schedule(self) -> Optional[List[Dict[str, Any]]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.schedule()
        return None

    def directory(self, page: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.directory(page)
        return None

    def filter(self, query: Optional[Dict[str, str]] = None) -> Optional[List[Dict[str, Any]]]:
        if self.provider == "jkanime":
            with self._jk() as api:
                return api.filter(query)
        return None

    def unified_servers(self, title: str, episode: int, threshold: int = 92, validate: bool = False, timeout: int = 6) -> List[Dict[str, Any]]:
        # Busca en ambos proveedores y unifica si coinciden con alta confianza
        jk_servers: List[Dict[str, Any]] = []
        af_servers: List[Dict[str, Any]] = []

        # JkAnime
        with self._jk() as jk:
            s = jk.search(title) or {}
            animes = s.get("animes") or []
            jk_best = None
            for a in animes:
                if _fuzzy_match(a.get("title", ""), title, threshold):
                    jk_best = a
                    break
            if jk_best:
                slug = jk_best.get("slug")
                urls = jk.servers(slug, episode) or []
                jk_servers = _jk_servers_struct(urls)

        # AnimeFLV
        af = self._aflv()
        if af:
            with af as api:
                res = _call_any(api, ["search"], title) or []
                af_best = None
                for a in res if isinstance(res, list) else []:
                    name = a.get("title") or a.get("name") or a.get("anime_title") or ""
                    if _fuzzy_match(name, title, threshold):
                        af_best = a
                        break
                if af_best:
                    af_slug = af_best.get("slug") or af_best.get("id") or af_best.get("anime_id")
                    raw_servers = (
                        _call_any(api, ["get_video_servers", "get_servers", "video_servers"], af_slug, episode)
                        or _call_any(api, ["get_video_servers", "get_servers", "video_servers"], af_best, episode)
                    )
                    af_servers = _aflv_servers_struct(raw_servers)

        merged = _dedupe_servers(jk_servers + af_servers)
        if validate:
            filtered = []
            for s in merged:
                u = s.get("url") or ""
                if _is_url_alive(u, timeout):
                    filtered.append(s)
            return filtered
        return merged
