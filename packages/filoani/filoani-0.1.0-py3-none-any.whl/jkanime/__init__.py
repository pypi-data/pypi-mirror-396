from typing import Optional, Dict, Any, List

from python.jkanime_v2 import (
    latest_anime_added as _latest_anime_added,
    by_alphabet as _by_alphabet,
    iter_by_alphabet as _iter_by_alphabet,
    search as _search,
    schedule as _schedule,
    top as _top,
    get_extra_info as _get_extra_info,
    get_anime_servers as _get_anime_servers,
    get_anime_directory as _get_anime_directory,
    filter as _filter,
    iter_filter as _iter_filter,
)


class JkAnime:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def latest(self) -> Optional[List[Dict[str, Any]]]:
        return _latest_anime_added()

    def by_alphabet(self, letter: str) -> Optional[List[Dict[str, Any]]]:
        return _by_alphabet(letter)

    def iter_by_alphabet(self, letter: str):
        return _iter_by_alphabet(letter)

    def search(self, q: str) -> Optional[Dict[str, Any]]:
        return _search(q)

    def schedule(self) -> List[Dict[str, Any]]:
        return _schedule()

    def top(self, season: str, year: str) -> Optional[List[Dict[str, Any]]]:
        return _top(season, year)

    def extra(self, slug: str) -> Optional[Dict[str, Any]]:
        return _get_extra_info(slug)

    def servers(self, slug: str, chapter: int) -> Optional[List[str]]:
        return _get_anime_servers(slug, chapter)

    def directory(self, page: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
        return _get_anime_directory(page)

    def filter(self, query: Optional[Dict[str, str]] = None) -> Optional[List[Dict[str, Any]]]:
        return _filter(query)


__all__ = [
    "JkAnime",
]

