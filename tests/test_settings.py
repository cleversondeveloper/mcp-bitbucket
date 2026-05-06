from __future__ import annotations

import pytest

from mcp_bitbucket import BitbucketConfig


def test_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BITBUCKET_WORKSPACE", "workspace")
    monkeypatch.setenv("BITBUCKET_TOKEN", "token")
    monkeypatch.setenv("BITBUCKET_API_BASE", "https://example.test/2.0/")
    monkeypatch.setenv("BITBUCKET_ALLOWED_API_HOSTS", "example.test")
    monkeypatch.setenv("BITBUCKET_CONNECT_TIMEOUT", "10")
    monkeypatch.setenv("BITBUCKET_READ_TIMEOUT", "10")
    monkeypatch.setenv("BITBUCKET_WRITE_TIMEOUT", "10")
    monkeypatch.setenv("BITBUCKET_MAX_RETRIES", "5")
    monkeypatch.setenv("BITBUCKET_RETRY_BACKOFF", "0.25")
    monkeypatch.setenv("BITBUCKET_READ_ONLY", "false")

    config = BitbucketConfig.from_env()

    assert config.workspace == "workspace"
    assert config.get_token == "token"
    assert config.api_base == "https://example.test/2.0/"
    assert config.connect_timeout == 10
    assert config.read_timeout == 10
    assert config.write_timeout == 10
    assert config.max_retries == 5
    assert config.retry_backoff == 0.25
    assert config.read_only is False


def test_config_from_env_read_only(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BITBUCKET_WORKSPACE", "workspace")
    monkeypatch.setenv("BITBUCKET_TOKEN", "token")
    monkeypatch.setenv("BITBUCKET_READ_ONLY", "true")

    config = BitbucketConfig.from_env()

    assert config.read_only is True


def test_config_from_env_token_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    token_file = tmp_path / "token.txt"
    token_file.write_text("file-token", encoding="utf-8")
    monkeypatch.setenv("BITBUCKET_WORKSPACE", "workspace")
    monkeypatch.setenv("BITBUCKET_TOKEN_FILE", str(token_file))

    config = BitbucketConfig.from_env()

    assert config.get_token == "file-token"


def test_config_from_env_requires_workspace_and_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("BITBUCKET_WORKSPACE", raising=False)
    monkeypatch.delenv("BITBUCKET_TOKEN", raising=False)

    with pytest.raises(RuntimeError, match="BITBUCKET_WORKSPACE"):
        BitbucketConfig.from_env()


def test_config_validates_invalid_values() -> None:
    with pytest.raises(ValueError, match="workspace"):
        BitbucketConfig(workspace=" ", _token="token")

    with pytest.raises(ValueError, match="connect_timeout"):
        BitbucketConfig(workspace="workspace", _token="token", connect_timeout=0)
