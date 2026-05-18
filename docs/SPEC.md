# Specification

## Objectives
- Keep OpenClaw lightweight and stable.
- Use Ollama as the primary reasoning engine.
- Use Telegram for operational input.
- Preserve compatibility with OpenClaw 2026.4.2 deployment logic.

## Required OpenClaw Extensions
- `ollama`
- `telegram`
- `webhooks`
- `shared`

## Explicitly Excluded in Phase 1
- browser
- cloudflared
- vector DB
- media tools
- multi-host orchestration
- multi-model swarm behavior

## Service Responsibilities
### openclaw-gateway
- Receive Telegram commands.
- Route prompts to the bridge.
- Execute approved local actions.
- Return responses to Telegram.

### llm-bridge-api
- Expose `/healthz`.
- Expose `/v1/chat/completions`.
- Normalize chat payloads for Ollama.
- Enforce API auth.

### ollama-brain
- Serve the instruct model.
- Keep only one model loaded.
- Operate as an internal dependency only.

## Operational Constraints
- Small-host friendly.
- Single primary model.
- Low concurrency.
- No browser runtime in the gateway container.
