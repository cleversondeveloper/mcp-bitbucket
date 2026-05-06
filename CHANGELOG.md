# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - Unreleased
### Added
- Matriz de comportamento do preflight de segurança no `README.md`.
- Resumo rápido das variáveis `BITBUCKET_SCOPE_CHECK_ON_STARTUP` e `BITBUCKET_STRICT_SCOPE_CHECK`.

### Changed
- O preflight de segurança passou a ficar desabilitado por padrão no startup.
- A documentação foi atualizada para explicar o impacto do preflight e suas combinações.

## [0.1.0] - RELEASED ![RELEASED](https://img.shields.io/badge/status-RELEASED-brightgreen) (2026-05-06)
### Added
- Initial MCP integration with basic tools.
- Granular timeouts and optional caching for performance.
- Tools for PRs, commits, branches, and workspaces.
- Best practices error handling (`BitbucketRateLimitError`, `BitbucketAuthError`).
- Segregation between `register_read_tools` and `register_write_tools`.
- Explicit `confirm` flag on sensitive/destructive tools.
- Size limit on JSON strings and payloads to prevent token overflow.
- Token redaction from application logs.
- Validation for input payloads (max comment length, branch format, UUIDs).
