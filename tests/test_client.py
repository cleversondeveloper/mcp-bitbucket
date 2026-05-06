from __future__ import annotations

import httpx

from mcp_bitbucket import BitbucketClient, BitbucketConfig
from mcp_bitbucket.infra.retry import ExponentialBackoffRetryStrategy


def test_retry_delay_uses_retry_after_header() -> None:
    client = BitbucketClient(BitbucketConfig(workspace="workspace", _token="token"))
    response = httpx.Response(429, headers={"retry-after": "2"})

    assert client.retry_strategy.retry_delay(0, response) == 2


def test_retry_delay_falls_back_to_exponential_backoff() -> None:
    client = BitbucketClient(
        BitbucketConfig(workspace="workspace", _token="token", retry_backoff=0.5)
    )

    delay = client.retry_strategy.retry_delay(2, None)
    assert 1.8 <= delay <= 2.2


def test_retry_strategy_should_retry() -> None:
    strategy = ExponentialBackoffRetryStrategy(
        max_retries=2,
        retry_backoff=0.5,
        retry_status_codes=(429, 500),
    )

    assert strategy.should_retry(0, error=httpx.ReadTimeout("timeout")) is True
    assert strategy.should_retry(0, response=httpx.Response(429)) is True
    assert strategy.should_retry(2, response=httpx.Response(429)) is False


def test_token_redacting_filter():
    import logging

    from mcp_bitbucket.infra.client import TokenRedactingFilter

    filter = TokenRedactingFilter(lambda: "my-secret-token")

    # Test string message
    record = logging.LogRecord(
        "name", logging.INFO, "path", 1, "Got token: my-secret-token here", (), None
    )
    filter.filter(record)
    assert record.msg == "Got token: ***REDACTED*** here"

    # Test string args
    record = logging.LogRecord(
        "name", logging.INFO, "path", 1, "Msg %s", ("my-secret-token-123",), None
    )
    filter.filter(record)
    assert record.args == ("***REDACTED***-123",)

    # Test extra attributes
    record = logging.LogRecord("name", logging.INFO, "path", 1, "Msg", (), None)
    record.custom_field = "header: my-secret-token"
    filter.filter(record)
    assert record.custom_field == "header: ***REDACTED***"


def test_client_applies_filter():
    config = BitbucketConfig(workspace="w", _token="test-token")
    BitbucketClient(config)
    # The filter should be added to the module logger
    from mcp_bitbucket.infra.client import logger

    assert any(
        getattr(f, "get_token_func", lambda: None)() == "test-token"
        for f in logger.filters
    )


def test_client_headers() -> None:
    config = BitbucketConfig(workspace="w", _token="t", user_agent="test-agent")
    client = BitbucketClient(config)

    assert client.headers() == {
        "Authorization": "Bearer t",
        "Accept": "application/json",
        "User-Agent": "test-agent",
    }

    assert client.headers(json_body=True) == {
        "Authorization": "Bearer t",
        "Accept": "application/json",
        "User-Agent": "test-agent",
        "Content-Type": "application/json",
    }


def test_client_request_contract() -> None:
    import asyncio
    from unittest.mock import AsyncMock, patch

    config = BitbucketConfig(workspace="w", _token="t")
    client = BitbucketClient(config)

    mock_response = httpx.Response(200, json={"success": True})
    mock_response.raise_for_status = lambda: mock_response

    with patch("httpx.AsyncClient.request", new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response

        result = asyncio.run(
            client.request("/test/path", method="POST", body={"key": "value"})
        )

        assert result == {"success": True}
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert args[1] == "https://api.bitbucket.org/2.0/test/path"
        assert kwargs["content"] == b'{"key": "value"}'
        assert kwargs["headers"]["Authorization"] == "Bearer t"
        assert kwargs["headers"]["Content-Type"] == "application/json"
