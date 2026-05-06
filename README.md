# MCP Bitbucket

Servidor MCP para operações no Bitbucket, com execução local (Poetry) ou em Docker.

![Develop Tests](https://img.shields.io/github/actions/workflow/status/<org-ou-usuario>/mcp-bitbucket/develop-tests.yml?branch=develop&label=develop%20tests)
![Main Build](https://img.shields.io/github/actions/workflow/status/<org-ou-usuario>/mcp-bitbucket/main-build.yml?branch=main&label=main%20build)
![Tag Publish](https://img.shields.io/github/actions/workflow/status/<org-ou-usuario>/mcp-bitbucket/tag-publish.yml?branch=main&label=tag%20publish)

## ✨ Visão rápida

- ✅ Suporte a modo somente leitura (`read-only`)
- ✅ Tools de consulta e escrita (PR, branch, comentários)
- ✅ Integração com clientes MCP (Codex, Gemini, Zed, Antigravity)
- ✅ Execução por `stdio` (padrão MCP)

## 🚀 Instalação e execução

### 1) 🧪 Modo local (Poetry)

```bash
poetry install
```

Configure variáveis obrigatórias:

```bash
export BITBUCKET_WORKSPACE="seu-workspace"
export BITBUCKET_TOKEN="seu-token"
```

Inicie o servidor:

```bash
# leitura + escrita
poetry run mcp-bitbucket

# somente leitura
poetry run mcp-bitbucket --read-only
```

### 2) 🐳 Modo Docker

Build:

```bash
docker build -f docker/Dockerfile -t mcp-bitbucket:local .
```

Run:

```bash
docker run -i --rm \
  -e BITBUCKET_WORKSPACE="$BITBUCKET_WORKSPACE" \
  -e BITBUCKET_TOKEN="$BITBUCKET_TOKEN" \
  -e BITBUCKET_READ_ONLY="true" \
  mcp-bitbucket:local
```

Compose:

```bash
docker compose -f docker/docker-compose.yml run --rm mcp-bitbucket
```

## 🔌 Configuração por cliente MCP

### 🤖 Codex

Local:

```json
{
  "command": "poetry",
  "args": ["run", "mcp-bitbucket", "--read-only"],
  "cwd": "/caminho/para/mcp-bitbucket",
  "env": {
    "BITBUCKET_WORKSPACE": "seu-workspace",
    "BITBUCKET_TOKEN": "seu-token"
  }
}
```

Docker:

```json
{
  "command": "docker",
  "args": [
    "run", "-i", "--rm",
    "-e", "BITBUCKET_WORKSPACE",
    "-e", "BITBUCKET_TOKEN",
    "-e", "BITBUCKET_READ_ONLY=true",
    "mcp-bitbucket:local"
  ]
}
```

### ✨ Gemini CLI (`~/.gemini/settings.json`)

Local:

```json
{
  "mcpServers": {
    "bitbucket-local": {
      "command": "poetry",
      "args": ["run", "mcp-bitbucket", "--read-only"],
      "cwd": "/caminho/para/mcp-bitbucket",
      "env": {
        "BITBUCKET_WORKSPACE": "seu-workspace",
        "BITBUCKET_TOKEN": "seu-token"
      }
    }
  }
}
```

Docker:

```json
{
  "mcpServers": {
    "bitbucket-docker": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "BITBUCKET_WORKSPACE",
        "-e", "BITBUCKET_TOKEN",
        "-e", "BITBUCKET_READ_ONLY=true",
        "mcp-bitbucket:local"
      ]
    }
  }
}
```

### 🧭 Zed (`~/.config/zed/settings.json`)

Local:

```json
{
  "context_servers": {
    "bitbucket-local": {
      "command": "poetry",
      "args": ["run", "mcp-bitbucket", "--read-only"],
      "cwd": "/caminho/para/mcp-bitbucket",
      "env": {
        "BITBUCKET_WORKSPACE": "seu-workspace",
        "BITBUCKET_TOKEN": "seu-token"
      }
    }
  }
}
```

Docker:

```json
{
  "context_servers": {
    "bitbucket-docker": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "BITBUCKET_WORKSPACE",
        "-e", "BITBUCKET_TOKEN",
        "-e", "BITBUCKET_READ_ONLY=true",
        "mcp-bitbucket:local"
      ]
    }
  }
}
```

### 🪐 Antigravity (`.vscode/mcp.json`)

Local:

```json
{
  "servers": {
    "bitbucket-local": {
      "command": "poetry",
      "args": ["run", "mcp-bitbucket", "--read-only"],
      "cwd": "/caminho/para/mcp-bitbucket",
      "env": {
        "BITBUCKET_WORKSPACE": "seu-workspace",
        "BITBUCKET_TOKEN": "seu-token"
      }
    }
  }
}
```

Docker:

```json
{
  "servers": {
    "bitbucket-docker": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "BITBUCKET_WORKSPACE",
        "-e", "BITBUCKET_TOKEN",
        "-e", "BITBUCKET_READ_ONLY=true",
        "mcp-bitbucket:local"
      ]
    }
  }
}
```

## ⚙️ Variáveis de ambiente

Resumo rápido:

- `BITBUCKET_SCOPE_CHECK_ON_STARTUP=false` mantém o startup simples e sem bloqueio por validação de escopos.
- `BITBUCKET_SCOPE_CHECK_ON_STARTUP=true` ativa o preflight de segurança.
- `BITBUCKET_STRICT_SCOPE_CHECK=true` faz a falha de validação interromper o boot quando o preflight estiver ativo.

| Variável | Obrigatória | Padrão | Descrição |
|---|---|---|---|
| `BITBUCKET_WORKSPACE` | Sim | - | Workspace slug |
| `BITBUCKET_TOKEN` | Sim | - | App Password ou OAuth token |
| `BITBUCKET_TOKEN_FILE` | Não | - | Caminho de arquivo com token (**preferível BITBUCKET_TOKEN**) |
| `BITBUCKET_READ_ONLY` | Não | `true` | Executa em modo somente leitura |
| `BITBUCKET_ENABLE_WRITE` | Não | `false` | Habilita registro de tools de escrita |
| `BITBUCKET_ALLOW_MERGE` | Não | `false` | Permite execução da tool de merge |
| `BITBUCKET_REQUIRE_CONFIRM_PHRASE` | Não | `true` | Exige frase para operações destrutivas |
| `BITBUCKET_CONFIRM_PHRASE` | Não | `I_UNDERSTAND` | Frase exigida em operações destrutivas |
| `BITBUCKET_ALLOWED_REPOS` | Não | vazio | Lista de `repo_slug` permitidos (CSV) |
| `BITBUCKET_API_BASE` | Não | `https://api.bitbucket.org/2.0` | Base da API Bitbucket |
| `BITBUCKET_ALLOWED_API_HOSTS` | Não | `api.bitbucket.org` | Hosts permitidos para `BITBUCKET_API_BASE` (CSV) |
| `BITBUCKET_TRUST_ENV_PROXY` | Não | `false` | Permite uso de `HTTP_PROXY` e `HTTPS_PROXY` do ambiente |
| `BITBUCKET_SCOPE_CHECK_ON_STARTUP` | Não | `false` | Executa preflight de segurança no startup quando habilitado |
| `BITBUCKET_STRICT_SCOPE_CHECK` | Não | `false` | Falha startup se escopos mínimos não forem comprovados |
| `BITBUCKET_CONNECT_TIMEOUT` | Não | `10.0` | Timeout de conexão (em segundos) |
| `BITBUCKET_READ_TIMEOUT` | Não | `30.0` | Timeout de leitura (em segundos) |
| `BITBUCKET_WRITE_TIMEOUT` | Não | `30.0` | Timeout de escrita (em segundos) |
| `BITBUCKET_MAX_CONNECTIONS` | Não | `100` | Limite total de conexões HTTP |
| `BITBUCKET_MAX_KEEPALIVE_CONNECTIONS` | Não | `20` | Limite de conexões keep-alive |
| `BITBUCKET_KEEPALIVE_EXPIRY` | Não | `5.0` | Expiração de keep-alive (em segundos) |
| `BITBUCKET_MAX_RETRIES` | Não | `3` | Máximo de tentativas |
| `BITBUCKET_RETRY_BACKOFF` | Não | `0.5` | Fator base do backoff exponencial (em segundos) |
| `BITBUCKET_RATE_LIMIT_REQUESTS` | Não | `120` | Máximo de requests por janela |
| `BITBUCKET_RATE_LIMIT_WINDOW_SECONDS` | Não | `60` | Janela de rate limit interno (em segundos) |
| `BITBUCKET_SENSITIVE_RATE_LIMIT_REQUESTS` | Não | `20` | Máximo de operações sensíveis por janela |
| `BITBUCKET_SENSITIVE_RATE_LIMIT_WINDOW_SECONDS` | Não | `3600` | Janela das operações sensíveis (em segundos) |
| `BITBUCKET_MAX_RESPONSE_CHARS` | Não | `100000` | Limite de caracteres na resposta |

### 🔑 Exemplo de `BITBUCKET_TOKEN_FILE`

Arquivo de token (exemplo: `/run/secrets/bitbucket_token`):

```text
bbp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Configuração:

```bash
export BITBUCKET_TOKEN_FILE="/run/secrets/bitbucket_token"
```

Boas práticas:

- O arquivo deve conter somente o token, sem aspas e sem prefixo `BITBUCKET_TOKEN=`.
- Permissão recomendada: `chmod 600 /run/secrets/bitbucket_token`.
- `BITBUCKET_TOKEN_FILE` não aplica criptografia por si só; a proteção depende do armazenamento (ex.: Docker Secrets, Kubernetes Secrets com encryption at rest).

## 🔐 Escopos mínimos

Use tokens separados para leitura e escrita quando possível.

| Perfil | Escopos recomendados | Uso |
|---|---|---|
| Leitura | `account`, `pullrequest`, `repository`, `workspace` | Consultas e diagnóstico |
| Escrita | `pullrequest:write`, `repository:write` | PR, branch, comentários, merge |

## 🛡️ Verificações de segurança

- O preflight de segurança no startup fica desabilitado por padrão para não bloquear a inicialização do servidor MCP.
- Escrita só é habilitada com configuração explícita:
  - `BITBUCKET_READ_ONLY=false`
  - `BITBUCKET_ENABLE_WRITE=true`
- Merge só é permitido com `BITBUCKET_ALLOW_MERGE=true`.
- Operações destrutivas exigem confirmação explícita e, por padrão, frase de confirmação.
- Operações sensíveis (`merge`, `decline`, `request_changes`) possuem quota própria por janela.
- Rotação de token já é suportada por leitura dinâmica de `BITBUCKET_TOKEN_FILE` sem reinício do processo.

### 📊 Matriz de comportamento do preflight

O preflight valida o acesso ao workspace e tenta confirmar escopos do token no startup.
Quando `BITBUCKET_SCOPE_CHECK_ON_STARTUP=true`, ele é executado antes do servidor expor as tools.
O impacto real depende da combinação com `BITBUCKET_STRICT_SCOPE_CHECK`.

| `BITBUCKET_SCOPE_CHECK_ON_STARTUP` | `BITBUCKET_STRICT_SCOPE_CHECK` | Resultado no startup |
|---|---|---|
| `false` | `false` | O servidor inicia normalmente. Nenhuma validação de escopo é executada no boot. |
| `false` | `true` | O servidor inicia normalmente. O `strict` fica sem efeito porque o preflight não foi acionado. |
| `true` | `false` | O servidor executa o preflight. Se a validação falhar, registra warning e continua subindo. |
| `true` | `true` | O servidor executa o preflight. Se a validação falhar ou os escopos mínimos não forem comprovados, o startup falha. |

Recomendação prática:

- Para uso padrão em clientes MCP via Docker, mantenha `BITBUCKET_SCOPE_CHECK_ON_STARTUP=false`.
- Ative `BITBUCKET_SCOPE_CHECK_ON_STARTUP=true` apenas em ambientes de validação ou quando quiser bloquear o boot por política.
- Use `BITBUCKET_STRICT_SCOPE_CHECK=true` somente se a indisponibilidade no startup for aceitável em troca de enforcement mais rígido.

## 🔎 Scans recomendados

```bash
poetry run task sast
poetry run task audit
```

## 📡 Auditoria externa (SIEM)

- O MCP já publica eventos de auditoria (`bitbucket_request_audit`) em logs.
- Para trilha imutável, encaminhe stdout do container/processo para seu stack de observabilidade com retenção imutável (ex.: WORM, retention lock).

Exemplo de configuração (Docker `json-file` com rotação + coleta externa):

```yaml
services:
  mcp-bitbucket:
    image: mcp-bitbucket:local
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "5"
```

Exemplo de configuração (envio para Fluentd/SIEM):

```yaml
services:
  mcp-bitbucket:
    image: mcp-bitbucket:local
    logging:
      driver: fluentd
      options:
        fluentd-address: "127.0.0.1:24224"
        tag: "mcp.bitbucket.audit"
```

## 🏗️ CI/CD

- `develop`:
  - executa testes automatizados
  - valida o Dockerfile com Hadolint
- `main`:
  - builda a imagem local
- `tag v*`:
  - builda e publica a imagem multiarch no Docker Hub `<dockerhub-username>/mcp-bitbucket`

## 🔐 Variáveis e Secrets Necessários

### 🧾 Secrets (GitHub Actions)

| Nome | Obrigatório | Uso |
|---|---|---|
| `DOCKERHUB_USERNAME` | Sim | Namespace do Docker Hub (usado em login e tags) |
| `DOCKERHUB_TOKEN` | Sim | Token para autenticação no Docker Hub |

### ⚙️ Variáveis de Ambiente da Aplicação

| Categoria | Variáveis |
|---|---|
| Obrigatórias | `BITBUCKET_WORKSPACE`, `BITBUCKET_TOKEN` ou `BITBUCKET_TOKEN_FILE` |
| Segurança/Policy | `BITBUCKET_READ_ONLY`, `BITBUCKET_ENABLE_WRITE`, `BITBUCKET_ALLOW_MERGE`, `BITBUCKET_ALLOWED_REPOS`, `BITBUCKET_ALLOWED_API_HOSTS`, `BITBUCKET_STRICT_SCOPE_CHECK` |
| Rede/Resiliência | `BITBUCKET_CONNECT_TIMEOUT`, `BITBUCKET_READ_TIMEOUT`, `BITBUCKET_WRITE_TIMEOUT`, `BITBUCKET_MAX_RETRIES`, `BITBUCKET_RETRY_BACKOFF` |

### 💡 Observações

- Configure os secrets em `Settings > Secrets and variables > Actions`.
- Para ambientes produtivos, prefira `BITBUCKET_TOKEN_FILE` com secret montado em arquivo.

## 🧰 Tools disponíveis

| Tool | Perfil | Método | Endpoint |
|---|---|---|---|
| `get_latest_commit` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/commits/{branch}` |
| `list_commits` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/commits` |
| `get_commit` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/commit/{commit}` |
| `get_commit_diff` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/diff/{spec}` |
| `create_commit_comment` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/commit/{commit}/comments` |
| `list_repositories` | Leitura | GET | `/repositories/{workspace}` |
| `get_repository` | Leitura | GET | `/repositories/{workspace}/{repo_slug}` |
| `list_projects` | Leitura | GET | `/workspaces/{workspace}/projects` |
| `list_workspaces` | Leitura | GET | `/workspaces` |
| `list_branches` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/refs/branches` |
| `get_branch` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/refs/branches/{branch}` |
| `create_branch` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/refs/branches` |
| `list_open_pull_requests` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/pullrequests` |
| `get_pull_request` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}` |
| `list_pull_request_comments` | Leitura | GET | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}/comments` |
| `create_pull_request_comment` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}/comments` |
| `create_pull_request` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/pullrequests` |
| `add_pull_request_reviewer` | Escrita | PUT | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}` |
| `merge_pull_request` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}/merge` |
| `decline_pull_request` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}/decline` |
| `approve_pull_request` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}/approve` |
| `request_changes` | Escrita | POST | `/repositories/{workspace}/{repo_slug}/pullrequests/{id}/request-changes` |
| `list_repository_permissions` | Leitura | GET | `/user/permissions/repositories` |
