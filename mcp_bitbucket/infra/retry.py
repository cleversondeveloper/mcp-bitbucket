"""Estrategias de retry para chamadas HTTP ao Bitbucket."""

from __future__ import annotations

from dataclasses import dataclass
from random import uniform

import httpx


@dataclass(frozen=True)
class ExponentialBackoffRetryStrategy:
    """Implementa politica de retry com backoff exponencial."""
    max_retries: int
    retry_backoff: float
    retry_status_codes: tuple[int, ...]
    jitter_ratio: float = 0.1

    def should_retry(
        self,
        attempt: int,
        *,
        response: httpx.Response | None = None,
        error: httpx.RequestError | None = None,
    ) -> bool:
        """Indica se a requisicao deve ser tentada novamente."""
        if attempt >= self.max_retries:
            return False
        if error is not None:
            return True
        if response is None:
            return False
        return response.status_code in self.retry_status_codes

    def retry_delay(self, attempt: int, response: httpx.Response | None) -> float:
        """Calcula atraso ate a proxima tentativa respeitando Retry-After."""
        retry_after = response.headers.get("retry-after") if response else None
        if retry_after:
            try:
                return max(float(retry_after), 0.0)
            except ValueError:
                pass
        base = self.retry_backoff * (2**attempt)
        jitter = base * self.jitter_ratio
        return max(0.0, base + uniform(-jitter, jitter))
