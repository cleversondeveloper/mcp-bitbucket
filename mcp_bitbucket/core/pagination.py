from __future__ import annotations

from typing import Any


def page_values(page: dict[str, Any]) -> list[Any]:
    values = page.get("values")
    if values is None:
        return []
    if not isinstance(values, list):
        raise ValueError("Bitbucket page values must be a list.")
    return values


def next_page_url(page: dict[str, Any]) -> str | None:
    next_url = page.get("next")
    return next_url if isinstance(next_url, str) else None


def has_next_page(page: dict[str, Any]) -> bool:
    return next_page_url(page) is not None
