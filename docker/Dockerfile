FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" --home /home/app app

COPY pyproject.toml poetry.lock README.md ./
COPY mcp_bitbucket ./mcp_bitbucket

RUN pip install --upgrade pip && pip install .

USER app

ENTRYPOINT ["python", "-m", "mcp_bitbucket.app.main"]
CMD ["--transport", "stdio"]

