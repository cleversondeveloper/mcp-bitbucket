from __future__ import annotations

import pytest

from mcp_bitbucket import has_next_page, next_page_url, page_values


def test_page_values_returns_values() -> None:
    assert page_values({"values": [{"name": "repo"}]}) == [{"name": "repo"}]


def test_page_values_defaults_to_empty_list() -> None:
    assert page_values({}) == []


def test_page_values_rejects_invalid_shape() -> None:
    with pytest.raises(ValueError, match="values"):
        page_values({"values": {"name": "repo"}})


def test_next_page_helpers() -> None:
    page = {"next": "https://api.example.test/page/2"}

    assert next_page_url(page) == "https://api.example.test/page/2"
    assert has_next_page(page) is True
    assert has_next_page({}) is False
