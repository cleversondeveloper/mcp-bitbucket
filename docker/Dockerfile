FROM python:3.14-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

WORKDIR /app

RUN pip install --upgrade pip poetry

COPY pyproject.toml poetry.lock README.md ./
COPY mcp_bitbucket ./mcp_bitbucket

RUN poetry install --only main --no-ansi

FROM python:3.14-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" --home /home/app app

COPY --from=builder /usr/local /usr/local

USER app

ENTRYPOINT ["python", "-m", "mcp_bitbucket.app.main"]
CMD ["--transport", "stdio"]
