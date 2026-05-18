# Deployment

## Phase 1 baseline
Single host deployment with three services:
- `openclaw-gateway`
- `llm-bridge-api`
- `ollama-brain`

## Phase 1 decisions
- OpenClaw is pinned to version **2026.4.2**.
- Telegram is the only ingress.
- `docker.sock` is mounted only into `openclaw-gateway`.
- Ollama is reachable only through the internal bridge.
- Cloudflared is not part of the phase-1 core.

## Startup order
1. `ollama-brain`
2. `llm-bridge-api`
3. `openclaw-gateway`

## Validation targets
- internal HTTP reachability
- bridge health
- Telegram roundtrip
- no direct public Ollama exposure
