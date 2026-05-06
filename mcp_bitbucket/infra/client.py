"""Cliente HTTP assíncrono para integração com a API do Bitbucket."""

from __future__ import annotations

import asyncio
import json
import logging
import re
import time
import uuid
from collections import deque
from typing import Any

import httpx

from ..core.settings import BitbucketConfig
from .errors import BitbucketAPIError
from .retry import ExponentialBackoffRetryStrategy

logger = logging.getLogger(__name__)
REPO_PATH_RE = re.compile(r"/repositories/[^/]+/([^/?]+)")


class TokenRedactingFilter(logging.Filter):
    """Filtro de log que mascara tokens sensiveis em mensagens e campos extras."""

    def __init__(self, get_token_func: Any) -> None:
        """Inicializa filtro com callback para recuperar token atual."""
        super().__init__()
        self.get_token_func = get_token_func

    def filter(self, record: logging.LogRecord) -> bool:
        """Redige token no registro de log antes da escrita."""
        token = self.get_token_func()
        if not token:
            return True

        # Redact token from the main message
        if isinstance(record.msg, str):
            record.msg = record.msg.replace(token, "***REDACTED***")

        # Redact token from string arguments
        if isinstance(record.args, tuple):
            record.args = tuple(
                arg.replace(token, "***REDACTED***") if isinstance(arg, str) else arg
                for arg in record.args
            )
        elif isinstance(record.args, dict):
            record.args = {
                k: (v.replace(token, "***REDACTED***") if isinstance(v, str) else v)
                for k, v in record.args.items()
            }

        # We don't redact exc_info directly here because it's a tuple of (type, value, traceback),
        # but we can redact any custom extra fields if they are strings.
        for attr, value in record.__dict__.items():
            if isinstance(value, str) and token in value:
                setattr(record, attr, value.replace(token, "***REDACTED***"))

        return True


class BitbucketClient:
    """Cliente de infraestrutura com retries, cache e sanitizacao de respostas."""

    def __init__(self, config: BitbucketConfig) -> None:
        """Inicializa cliente com configuracoes de auth, timeout e resiliencia."""
        self.config = config
        self.workspace = config.workspace
        self.api_base = config.api_base.rstrip("/")
        self.connect_timeout = config.connect_timeout
        self.read_timeout = config.read_timeout
        self.write_timeout = config.write_timeout
        self.user_agent = config.user_agent
        self.max_retries = config.max_retries
        self.retry_backoff = config.retry_backoff
        self.retry_status_codes = config.retry_status_codes
        self.cache_ttl = config.cache_ttl
        self.retry_strategy = ExponentialBackoffRetryStrategy(
            max_retries=config.max_retries,
            retry_backoff=config.retry_backoff,
            retry_status_codes=config.retry_status_codes,
        )

        self._http_client: httpx.AsyncClient | None = None
        self._cache: dict[str, tuple[float, Any]] = {}
        self._request_timestamps: deque[float] = deque()

        # Apply the redacting filter to the logger
        # Pass a callable that always fetches the latest token
        logger.addFilter(TokenRedactingFilter(lambda: self.config.get_token))

    @property
    def http_client(self) -> httpx.AsyncClient:
        """Retorna cliente HTTP compartilhado, criando sob demanda."""
        if self._http_client is None:
            timeout = httpx.Timeout(
                self.read_timeout,
                connect=self.connect_timeout,
                read=self.read_timeout,
                write=self.write_timeout,
                pool=self.connect_timeout,
            )
            limits = httpx.Limits(
                max_connections=self.config.max_connections,
                max_keepalive_connections=self.config.max_keepalive_connections,
                keepalive_expiry=self.config.keepalive_expiry,
            )
            self._http_client = httpx.AsyncClient(
                timeout=timeout,
                limits=limits,
                trust_env=self.config.trust_env_proxy,
            )
        return self._http_client

    async def aclose(self) -> None:
        """Fecha recursos de rede e limpa cache em memoria."""
        if self._http_client is not None:
            await self._http_client.aclose()
            self._http_client = None
        self._cache.clear()

    def headers(self, json_body: bool = False) -> dict[str, str]:
        """Monta headers padrao, incluindo autenticacao Bearer."""
        token = self.config.get_token
        result = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": self.user_agent,
        }
        if json_body:
            result["Content-Type"] = "application/json"
        return result

    def _truncate_text(self, text: str) -> str:
        """Trunca texto bruto conforme limite configurado."""
        max_chars = self.config.max_response_chars
        if len(text) > max_chars:
            return (
                text[:max_chars]
                + f"\n\n...[TRUNCATED: Exceeded {max_chars} characters]"
            )
        return text

    def _truncate_json(self, data: Any) -> Any:
        """Trunca recursivamente campos textuais em estruturas JSON."""
        max_chars = self.config.max_response_chars
        if isinstance(data, str):
            if len(data) > max_chars:
                return (
                    data[:max_chars]
                    + f"...[TRUNCATED: Exceeded {max_chars} characters]"
                )
            return data
        if isinstance(data, list):
            return [self._truncate_json(item) for item in data]
        if isinstance(data, dict):
            return {k: self._truncate_json(v) for k, v in data.items()}
        return data

    async def request(
        self, path: str, method: str = "GET", body: dict[str, Any] | None = None
    ) -> Any:
        """Executa requisicao HTTP com retry, tratamento de erro e cache GET."""
        self._check_rate_limit()
        client = self.http_client
        response: httpx.Response | None = None
        last_error: httpx.RequestError | None = None
        request_id = str(uuid.uuid4())

        # Check if path is already a full URL (e.g. from next_page_url)
        url = path if path.startswith("http") else f"{self.api_base}{path}"
        self._enforce_repo_allowlist(path)

        # Cache check for idempotent GET requests
        if method == "GET" and self.cache_ttl > 0:
            cached_data = self._cache.get(url)
            if cached_data:
                timestamp, data = cached_data
                if time.monotonic() - timestamp < self.cache_ttl:
                    return data

        for attempt in range(self.max_retries + 1):
            try:
                response = await client.request(
                    method,
                    url,
                    content=json.dumps(body).encode("utf-8")
                    if body is not None
                    else None,
                    headers=self.headers(json_body=body is not None),
                )
            except httpx.RequestError as exc:
                last_error = exc
                if not self.retry_strategy.should_retry(attempt, error=exc):
                    raise RuntimeError(f"Bitbucket API request failed: {exc}") from exc
                await self._sleep_before_retry(attempt, None)
                continue

            if not self.retry_strategy.should_retry(attempt, response=response):
                break

            await self._sleep_before_retry(attempt, response)

        if response is None:
            raise RuntimeError(f"Bitbucket API request failed: {last_error}")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            err = BitbucketAPIError.from_response(
                exc.response.status_code, exc.response.text
            )
            err.log_safe_error()
            self._audit_log(
                request_id=request_id,
                method=method,
                path=path,
                status=exc.response.status_code,
                outcome="error",
            )
            raise err from exc

        if response.status_code == httpx.codes.NO_CONTENT:
            return {}

        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            result = {"content": self._truncate_text(response.text)}
        else:
            result = self._truncate_json(response.json())

        # Update cache
        if method == "GET" and self.cache_ttl > 0:
            self._cache[url] = (time.monotonic(), result)

        self._audit_log(
            request_id=request_id,
            method=method,
            path=path,
            status=response.status_code,
            outcome="success",
        )
        return result

    async def iter_pages(self, path: str, max_pages: int = 10, **kwargs: Any) -> Any:
        """Itera paginas de resposta respeitando limite maximo configurado."""
        from ..core.pagination import next_page_url

        current_path = path
        pages_fetched = 0

        while current_path and pages_fetched < max_pages:
            page_data = await self.request(current_path, **kwargs)
            yield page_data

            pages_fetched += 1
            current_path = next_page_url(page_data)

    async def request_page(self, path: str, **kwargs: Any) -> dict[str, Any]:
        """Busca uma unica pagina e retorna o payload normalizado."""
        return await self.request(path, **kwargs)

    async def _sleep_before_retry(
        self, attempt: int, response: httpx.Response | None
    ) -> None:
        """Aguarda tempo de backoff antes da proxima tentativa."""
        delay = self.retry_strategy.retry_delay(attempt, response)
        logger.info(
            "bitbucket_request_retry",
            extra={
                "attempt": attempt + 1,
                "delay": delay,
                "status_code": response.status_code if response else None,
            },
        )
        await asyncio.sleep(delay)

    def _enforce_repo_allowlist(self, path: str) -> None:
        allowed = set(self.config.allowed_repos)
        if not allowed:
            return
        match = REPO_PATH_RE.search(path)
        if not match:
            return
        repo_slug = match.group(1)
        if repo_slug not in allowed:
            raise PermissionError(
                f"Repository '{repo_slug}' is not in BITBUCKET_ALLOWED_REPOS."
            )

    def _check_rate_limit(self) -> None:
        now = time.monotonic()
        window = self.config.rate_limit_window_seconds
        while self._request_timestamps and now - self._request_timestamps[0] > window:
            self._request_timestamps.popleft()
        if len(self._request_timestamps) >= self.config.rate_limit_requests:
            raise RuntimeError("Internal rate limit exceeded for Bitbucket MCP client.")
        self._request_timestamps.append(now)

    def _audit_log(
        self, request_id: str, method: str, path: str, status: int | None, outcome: str
    ) -> None:
        logger.info(
            "bitbucket_request_audit",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "workspace": self.workspace,
                "status": status,
                "outcome": outcome,
            },
        )

    async def fetch_oauth_scopes(self) -> set[str]:
        """Obtém escopos do token via header HTTP, quando disponível."""
        base_root = self.api_base
        if base_root.endswith("/2.0"):
            base_root = base_root[:-4]
        response = await self.http_client.request(
            "GET",
            f"{base_root}/user",
            headers=self.headers(),
        )
        scopes_raw = response.headers.get("x-oauth-scopes", "")
        return {scope.strip() for scope in scopes_raw.split(",") if scope.strip()}
