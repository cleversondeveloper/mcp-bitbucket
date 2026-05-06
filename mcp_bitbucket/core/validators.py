"""Utilitarios de validacao e normalizacao para entradas da API Bitbucket."""

from __future__ import annotations

import re
import uuid
from typing import Any
from urllib.parse import quote, urlencode

MAX_PAGE_LEN = 100
VALID_SLUG_RE = re.compile(r"^[A-Za-z0-9._-]+$")
VALID_BRANCH_RE = re.compile(r"^[A-Za-z0-9._/\-]+$")
VALID_REF_RE = re.compile(r"^[A-Za-z0-9._/\-]+(\.\.[A-Za-z0-9._/\-]+)?$")
MAX_TITLE_LEN = 255
MAX_COMMENT_LEN = 32000
MAX_DESCRIPTION_LEN = 32000


def query(params: dict[str, Any]) -> str:
    """Monta query string a partir de parametros nao vazios."""
    filtered = {key: value for key, value in params.items() if value not in (None, "")}
    return f"?{urlencode(filtered)}" if filtered else ""


def safe_segment(value: str, label: str, pattern: re.Pattern[str]) -> str:
    """Valida e codifica um segmento de URL com base em regex permitida."""
    if not value or not pattern.fullmatch(value):
        raise ValueError(f"Invalid {label}.")
    return quote(value, safe="")


def safe_repo_slug(repo_slug: str) -> str:
    """Valida e codifica o slug de repositorio."""
    return safe_segment(repo_slug, "repo_slug", VALID_SLUG_RE)


def safe_branch(branch: str) -> str:
    """Valida e codifica nome de branch."""
    return safe_segment(branch, "branch", VALID_BRANCH_RE)


def safe_ref(ref: str) -> str:
    """Valida e codifica referencia de commit/intervalo."""
    return safe_segment(ref, "ref", VALID_REF_RE)


def validate_branch_name(branch: str) -> str:
    """Valida formato de nome de branch sem alterar o valor."""
    if not branch or not VALID_BRANCH_RE.fullmatch(branch):
        raise ValueError("Invalid branch.")
    return branch


def normalize_positive_int(value: int, label: str) -> int:
    """Garante inteiro positivo para parametros numericos."""
    if value < 1:
        raise ValueError(f"{label} must be greater than zero.")
    return value


def normalize_pagelen(pagelen: int | None) -> int | None:
    """Normaliza pagelen para o limite maximo permitido pela API."""
    if pagelen is None:
        return None
    if pagelen < 1:
        raise ValueError("pagelen must be greater than zero.")
    return min(pagelen, MAX_PAGE_LEN)


def normalize_page(page: int | None) -> int | None:
    """Valida o numero da pagina quando informado."""
    if page is None:
        return None
    if page < 1:
        raise ValueError("page must be greater than zero.")
    return page


def validate_length(value: str, max_len: int, label: str) -> str:
    """Valida tamanho maximo de campo textual."""
    if len(value) > max_len:
        raise ValueError(f"{label} exceeds maximum length of {max_len} characters.")
    return value


def validate_comment(comment: str) -> str:
    """Valida tamanho de comentario."""
    return validate_length(comment, MAX_COMMENT_LEN, "comment")


def validate_title(title: str) -> str:
    """Valida titulo obrigatorio e com tamanho permitido."""
    if not title.strip():
        raise ValueError("Title cannot be empty.")
    return validate_length(title, MAX_TITLE_LEN, "title")


def validate_description(description: str) -> str:
    """Valida tamanho da descricao."""
    return validate_length(description, MAX_DESCRIPTION_LEN, "description")


def validate_uuid(value: str) -> str:
    """Valida UUID e retorna no formato com chaves usado pelo Bitbucket."""
    try:
        val = str(uuid.UUID(value))
        return f"{{{val}}}"
    except ValueError:
        # Bitbucket UUIDs often include curly braces.
        try:
            clean = value.strip("{}")
            val = str(uuid.UUID(clean))
            return f"{{{val}}}"
        except ValueError as exc:
            raise ValueError(f"Invalid UUID: {value}") from exc


def parse_author(raw: str | None) -> dict[str, str | None]:
    """Extrai nome e e-mail do campo author.raw de um commit."""
    if not raw:
        return {"name": None, "email": None}
    match = re.match(r"^(.*)\s<([^>]+)>$", raw)
    if not match:
        return {"name": raw, "email": None}
    return {"name": match.group(1), "email": match.group(2)}


def repo_path(workspace: str, repo_slug: str) -> str:
    """Constroi path canonical de repositorio."""
    return f"/repositories/{workspace_slug(workspace)}/{safe_repo_slug(repo_slug)}"


def workspace_path(workspace: str) -> str:
    """Constroi path canonical de workspace."""
    return f"/workspaces/{workspace_slug(workspace)}"


def workspace_slug(workspace: str) -> str:
    """Codifica slug de workspace para uso seguro em URL."""
    return quote(workspace, safe="")
