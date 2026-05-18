# Architecture

## Baseline
- OpenClaw version is pinned to **2026.4.2**.
- The deployment pattern is based on `deploy/ollama-fastapi` from `/home/node/.openclaw/workspace/partner-lama/openclaw-main`.
- The deployment target is a single host with a single Docker network.

## Core Components
1. **openclaw-gateway**
   - Telegram ingress
   - Agent runtime
   - Tool executor
   - Docker socket access
   - Client of the LLM bridge
2. **llm-bridge-api**
   - OpenAI-compatible API adapter
   - Auth layer for model access
   - Timeout and payload normalization layer
3. **ollama-brain**
   - Hosts the primary instruct model
   - Internal-only inference backend

## Data Flow
Telegram User -> Telegram Bot/API -> openclaw-gateway -> llm-bridge-api -> ollama-brain -> llm-bridge-api -> openclaw-gateway -> Telegram response

## Network Model
- One Docker network for all core services.
- Internal traffic uses service-to-service HTTP.
- No cloudflared in the phase-1 core.

## Security Model
- `docker.sock` is mounted only into `openclaw-gateway`.
- Ollama is not exposed publicly.
- The bridge enforces API key auth.
- Telegram input is treated as untrusted.
- Model output is advisory and must not be executed blindly.
