# Security

## Trust boundaries
- Telegram input is untrusted.
- Model output is advisory.
- Docker socket is privileged.

## Core controls
- Mount `docker.sock` only into `openclaw-gateway`.
- Keep Ollama internal-only.
- Require bridge API authentication.
- Restrict OpenClaw extensions to the minimum viable set.

## Phase 1 extension set
- `ollama`
- `telegram`
- `webhooks`
- `shared`
