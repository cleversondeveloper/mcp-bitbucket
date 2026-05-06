"""Erros de dominio para respostas da API Bitbucket."""

import json
import logging
from dataclasses import dataclass
from textwrap import shorten

logger = logging.getLogger(__name__)

MAX_ERROR_BODY_LEN = 250
MAX_LOG_BODY_LEN = 1000


@dataclass(frozen=True)
class BitbucketAPIError(RuntimeError):
    """Erro base para falhas retornadas pela API Bitbucket."""
    status: int
    body: str

    def __str__(self) -> str:
        """Retorna mensagem textual segura para exibicao."""
        return f"Bitbucket API {self.status}: {self.sanitized_message}"

    @property
    def sanitized_message(self) -> str:
        """Extrai mensagem segura do corpo da resposta, evitando vazamento interno."""
        try:
            data = json.loads(self.body)
            # Bitbucket standard error format is often {"error": {"message": "..."}}
            if isinstance(data, dict):
                error_obj = data.get("error", {})
                if isinstance(error_obj, dict):
                    msg = error_obj.get("message")
                    if msg:
                        return shorten(
                            str(msg), width=MAX_ERROR_BODY_LEN, placeholder="..."
                        )
        except json.JSONDecodeError, TypeError:
            pass

        # Fallback to truncated raw body if not JSON or standard format
        return shorten(
            self.body.replace("\n", " ").strip(),
            width=MAX_ERROR_BODY_LEN,
            placeholder="...",
        )

    def log_safe_error(self) -> None:
        """Registra o erro com corpo truncado maior para depuração."""
        truncated_body = shorten(self.body, width=MAX_LOG_BODY_LEN, placeholder="...")
        logger.error(
            "bitbucket_api_error",
            extra={
                "status": self.status,
                "body_preview": truncated_body,
            },
        )

    @classmethod
    def from_response(cls, status: int, body: str) -> BitbucketAPIError:
        """Método fábrica para criar erros de domínio com base no status HTTP."""
        if status in (401, 403):
            return BitbucketAuthError(status, body)
        if status == 404:
            return BitbucketNotFoundError(status, body)
        if status == 429:
            return BitbucketRateLimitError(status, body)
        return cls(status, body)


@dataclass(frozen=True)
class BitbucketAuthError(BitbucketAPIError):
    """Erro de autenticacao/autorizacao (401/403)."""
    pass


@dataclass(frozen=True)
class BitbucketNotFoundError(BitbucketAPIError):
    """Erro para recurso nao encontrado (404)."""
    pass


@dataclass(frozen=True)
class BitbucketRateLimitError(BitbucketAPIError):
    """Erro de limite de taxa excedido (429)."""
    pass
