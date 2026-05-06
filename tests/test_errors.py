from __future__ import annotations

from mcp_bitbucket.infra.errors import BitbucketAPIError


def test_bitbucket_api_error_sanitizes_body() -> None:
    message = str(BitbucketAPIError(500, "line 1\nline 2"))
    assert message == "Bitbucket API 500: line 1 line 2"


def test_bitbucket_api_error_json_parsing() -> None:
    body = '{"error": {"message": "Invalid credentials", "detail": "secret info"}}'
    err = BitbucketAPIError(401, body)
    assert "Invalid credentials" in str(err)
    assert "secret info" not in str(err)


def test_bitbucket_api_error_truncation() -> None:
    long_body = "x" * 1000
    err = BitbucketAPIError(500, long_body)
    assert len(str(err)) < 300
    assert str(err).endswith("...")


def test_bitbucket_api_error_from_response() -> None:
    from mcp_bitbucket.infra.errors import (
        BitbucketAuthError,
        BitbucketNotFoundError,
        BitbucketRateLimitError,
    )

    assert isinstance(BitbucketAPIError.from_response(401, ""), BitbucketAuthError)
    assert isinstance(BitbucketAPIError.from_response(403, ""), BitbucketAuthError)
    assert isinstance(BitbucketAPIError.from_response(404, ""), BitbucketNotFoundError)
    assert isinstance(BitbucketAPIError.from_response(429, ""), BitbucketRateLimitError)
    assert type(BitbucketAPIError.from_response(500, "")) is BitbucketAPIError
