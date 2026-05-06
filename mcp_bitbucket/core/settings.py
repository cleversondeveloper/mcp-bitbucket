from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass
from typing import ClassVar
from urllib.parse import urlparse


@dataclass(frozen=True)
class BitbucketConfig:
    DEFAULT_RETRY_STATUS_CODES: ClassVar[tuple[int, ...]] = (429, 500, 502, 503, 504)

    workspace: str
    _token: str | Callable[[], str]
    api_base: str = "https://api.bitbucket.org/2.0"
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0
    cache_ttl: float = 60.0
    user_agent: str = "bitbucket-local-mcp/1.0"
    max_retries: int = 3
    retry_backoff: float = 0.5
    retry_status_codes: tuple[int, ...] = DEFAULT_RETRY_STATUS_CODES
    read_only: bool = False
    enable_write: bool = False
    allow_merge: bool = False
    require_confirm_phrase: bool = True
    confirm_phrase: str = "I_UNDERSTAND"
    allowed_repos: tuple[str, ...] = ()
    allowed_api_hosts: tuple[str, ...] = ("api.bitbucket.org",)
    trust_env_proxy: bool = False
    scope_check_on_startup: bool = False
    strict_scope_check: bool = False
    max_connections: int = 100
    max_keepalive_connections: int = 20
    keepalive_expiry: float = 5.0
    rate_limit_requests: int = 120
    rate_limit_window_seconds: int = 60
    sensitive_rate_limit_requests: int = 20
    sensitive_rate_limit_window_seconds: int = 3600
    max_response_chars: int = 100000

    def __post_init__(self) -> None:
        if not self.workspace.strip():
            raise ValueError("workspace cannot be empty.")
        if isinstance(self._token, str) and not self._token.strip():
            raise ValueError("token cannot be empty.")
        if self.connect_timeout <= 0:
            raise ValueError("connect_timeout must be greater than zero.")
        if self.read_timeout <= 0:
            raise ValueError("read_timeout must be greater than zero.")
        if self.write_timeout <= 0:
            raise ValueError("write_timeout must be greater than zero.")
        if self.cache_ttl < 0:
            raise ValueError("cache_ttl cannot be negative.")
        if self.max_retries < 0:
            raise ValueError("max_retries cannot be negative.")
        if self.retry_backoff < 0:
            raise ValueError("retry_backoff cannot be negative.")
        if not self.retry_status_codes:
            raise ValueError("retry_status_codes cannot be empty.")
        if self.max_response_chars <= 0:
            raise ValueError("max_response_chars must be greater than zero.")
        parsed_api_base = urlparse(self.api_base)
        if parsed_api_base.scheme not in {"http", "https"}:
            raise ValueError("api_base must be an http(s) URL.")
        api_host = parsed_api_base.hostname
        if not api_host:
            raise ValueError("api_base must include a valid host.")
        if self.allowed_api_hosts and api_host not in set(self.allowed_api_hosts):
            raise ValueError(
                f"api_base host '{api_host}' is not allowed by BITBUCKET_ALLOWED_API_HOSTS."
            )
        if self.max_connections <= 0:
            raise ValueError("max_connections must be greater than zero.")
        if self.max_keepalive_connections <= 0:
            raise ValueError("max_keepalive_connections must be greater than zero.")
        if self.keepalive_expiry < 0:
            raise ValueError("keepalive_expiry cannot be negative.")
        if self.rate_limit_requests <= 0:
            raise ValueError("rate_limit_requests must be greater than zero.")
        if self.rate_limit_window_seconds <= 0:
            raise ValueError("rate_limit_window_seconds must be greater than zero.")
        if self.sensitive_rate_limit_requests <= 0:
            raise ValueError("sensitive_rate_limit_requests must be greater than zero.")
        if self.sensitive_rate_limit_window_seconds <= 0:
            raise ValueError(
                "sensitive_rate_limit_window_seconds must be greater than zero."
            )
        if self.require_confirm_phrase and not self.confirm_phrase.strip():
            raise ValueError("confirm_phrase cannot be empty.")

    @property
    def get_token(self) -> str:
        """Resolve the token dynamically if a callable was provided."""
        token = self._token() if callable(self._token) else self._token
        token = token.strip()
        if not token:
            raise RuntimeError("BITBUCKET_TOKEN is empty.")
        weak_tokens = {"changeme", "change-me", "example", "password", "123456"}
        if token.lower() in weak_tokens:
            raise RuntimeError("Weak token detected. Configure a valid BITBUCKET_TOKEN.")
        return token

    @classmethod
    def from_env(cls) -> BitbucketConfig:
        def _parse_bool(name: str, default: bool) -> bool:
            raw = os.environ.get(name)
            if raw is None:
                return default
            return raw.strip().lower() in {"1", "true", "yes", "on"}

        workspace = os.environ.get("BITBUCKET_WORKSPACE")
        token_file = os.environ.get("BITBUCKET_TOKEN_FILE")

        def dynamic_token() -> str:
            if token_file:
                with open(token_file, encoding="utf-8") as fp:
                    return fp.read().strip()
            return os.environ.get("BITBUCKET_TOKEN", "").strip()

        token = dynamic_token()

        api_base = os.environ.get("BITBUCKET_API_BASE", cls.api_base)
        connect_timeout = float(
            os.environ.get("BITBUCKET_CONNECT_TIMEOUT", cls.connect_timeout)
        )
        read_timeout = float(os.environ.get("BITBUCKET_READ_TIMEOUT", cls.read_timeout))
        write_timeout = float(
            os.environ.get("BITBUCKET_WRITE_TIMEOUT", cls.write_timeout)
        )
        cache_ttl = float(os.environ.get("BITBUCKET_CACHE_TTL", cls.cache_ttl))
        max_retries = int(os.environ.get("BITBUCKET_MAX_RETRIES", cls.max_retries))
        retry_backoff = float(
            os.environ.get("BITBUCKET_RETRY_BACKOFF", cls.retry_backoff)
        )
        read_only = _parse_bool("BITBUCKET_READ_ONLY", True)
        enable_write = _parse_bool("BITBUCKET_ENABLE_WRITE", False)
        allow_merge = _parse_bool("BITBUCKET_ALLOW_MERGE", False)
        require_confirm_phrase = _parse_bool("BITBUCKET_REQUIRE_CONFIRM_PHRASE", True)
        trust_env_proxy = _parse_bool("BITBUCKET_TRUST_ENV_PROXY", False)
        scope_check_on_startup = _parse_bool("BITBUCKET_SCOPE_CHECK_ON_STARTUP", False)
        strict_scope_check = _parse_bool("BITBUCKET_STRICT_SCOPE_CHECK", False)
        confirm_phrase = os.environ.get("BITBUCKET_CONFIRM_PHRASE", cls.confirm_phrase)
        allowed_repos_raw = os.environ.get("BITBUCKET_ALLOWED_REPOS", "")
        allowed_repos = tuple(
            item.strip()
            for item in allowed_repos_raw.split(",")
            if item.strip()
        )
        allowed_api_hosts_raw = os.environ.get("BITBUCKET_ALLOWED_API_HOSTS", "")
        allowed_api_hosts = (
            tuple(item.strip() for item in allowed_api_hosts_raw.split(",") if item.strip())
            if allowed_api_hosts_raw
            else cls.allowed_api_hosts
        )
        max_connections = int(
            os.environ.get("BITBUCKET_MAX_CONNECTIONS", cls.max_connections)
        )
        max_keepalive_connections = int(
            os.environ.get(
                "BITBUCKET_MAX_KEEPALIVE_CONNECTIONS", cls.max_keepalive_connections
            )
        )
        keepalive_expiry = float(
            os.environ.get("BITBUCKET_KEEPALIVE_EXPIRY", cls.keepalive_expiry)
        )
        rate_limit_requests = int(
            os.environ.get("BITBUCKET_RATE_LIMIT_REQUESTS", cls.rate_limit_requests)
        )
        rate_limit_window_seconds = int(
            os.environ.get(
                "BITBUCKET_RATE_LIMIT_WINDOW_SECONDS", cls.rate_limit_window_seconds
            )
        )
        sensitive_rate_limit_requests = int(
            os.environ.get(
                "BITBUCKET_SENSITIVE_RATE_LIMIT_REQUESTS",
                cls.sensitive_rate_limit_requests,
            )
        )
        sensitive_rate_limit_window_seconds = int(
            os.environ.get(
                "BITBUCKET_SENSITIVE_RATE_LIMIT_WINDOW_SECONDS",
                cls.sensitive_rate_limit_window_seconds,
            )
        )
        max_response_chars = int(
            os.environ.get("BITBUCKET_MAX_RESPONSE_CHARS", cls.max_response_chars)
        )

        if not workspace or not token:
            raise RuntimeError("BITBUCKET_WORKSPACE and BITBUCKET_TOKEN are required.")

        return cls(
            workspace=workspace,
            _token=dynamic_token,
            api_base=api_base,
            connect_timeout=connect_timeout,
            read_timeout=read_timeout,
            write_timeout=write_timeout,
            cache_ttl=cache_ttl,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
            read_only=read_only,
            enable_write=enable_write,
            allow_merge=allow_merge,
            require_confirm_phrase=require_confirm_phrase,
            confirm_phrase=confirm_phrase,
            allowed_repos=allowed_repos,
            allowed_api_hosts=allowed_api_hosts,
            trust_env_proxy=trust_env_proxy,
            scope_check_on_startup=scope_check_on_startup,
            strict_scope_check=strict_scope_check,
            max_connections=max_connections,
            max_keepalive_connections=max_keepalive_connections,
            keepalive_expiry=keepalive_expiry,
            rate_limit_requests=rate_limit_requests,
            rate_limit_window_seconds=rate_limit_window_seconds,
            sensitive_rate_limit_requests=sensitive_rate_limit_requests,
            sensitive_rate_limit_window_seconds=sensitive_rate_limit_window_seconds,
            max_response_chars=max_response_chars,
        )
