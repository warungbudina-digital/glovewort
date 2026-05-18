# deploy/ollama-fastapi

This subtree is the phase-1 inference core for `glovewort`.

It is adapted from the validated OpenClaw 2026.4.2 reference pattern at:
- `/home/node/.openclaw/workspace/partner-lama/openclaw-main/deploy/ollama-fastapi`

## Role in the architecture
This layer provides:
- `ollama-brain` as the local reasoning engine
- `llm-bridge-api` as the OpenAI-compatible adapter

OpenClaw does **not** talk to Ollama directly in phase 1. It talks to the bridge.

## Phase-1 decisions
- primary model is fixed to `qwen2.5-coder:1.5b`
- bridge exposes `/healthz` and `/v1/chat/completions`
- Cloudflared is not part of this phase-1 core
- Docker socket is not mounted into this subtree
- all traffic is internal Docker-network traffic

## Service intent
### `ollama-brain`
- hosts the primary instruct model
- internal-only service
- no Docker socket access

### `llm-bridge-api`
- exposes an OpenAI-compatible chat endpoint
- uses API key auth when configured
- forwards requests to `ollama-brain`

## Integration target
The expected OpenClaw provider base URL is:
- `http://llm-bridge-api:8000/v1`

## Out of scope here
- Telegram ingress
- Docker socket actions
- cloudflared tunneling
- browser runtime

Those belong to the `openclaw-gateway` layer, not the inference subtree.
