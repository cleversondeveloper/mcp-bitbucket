# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - Unreleased

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
