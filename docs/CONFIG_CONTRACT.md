# Configuration Contract

This document freezes the configuration contract for phase 1 before executable runtime files are finalized.

## Contract Goal
All runtime files must agree on:
- service names
- model identifier
- bridge base URL
- environment variable names
- trust and privilege boundaries

If a value is changed in one place, all dependent files must be updated together.

## Canonical Service Names
These names are fixed for phase 1:
- `openclaw-gateway`
- `llm-bridge-api`
- `ollama-brain`

These names are used in:
- `docker-compose.yml`
- OpenClaw provider configuration
- bridge upstream configuration
- validation and troubleshooting docs

## Canonical Network Name
Phase-1 logical network name:
- `brain_hand_net`

## Canonical Provider Contract
OpenClaw must call the bridge, not Ollama directly.

### Required provider path
- provider type: OpenAI-compatible completions/chat layer
- provider base URL: `http://llm-bridge-api:8000/v1`
- model name: phase-1 primary model only

## Canonical Socket Contract
Docker socket is mounted only into:
- `openclaw-gateway`

Docker socket must not be mounted into:
- `llm-bridge-api`
- `ollama-brain`

## Canonical Telegram Contract
Telegram is the only ingress channel in phase 1.

Required runtime assumption:
- valid bot token exists
- ingress mode is fixed explicitly, not implied

## Canonical Bridge Contract
The bridge must expose:
- `GET /healthz`
- `POST /v1/chat/completions`

The bridge must require:
- API key auth when configured

The bridge must forward to:
- `http://ollama-brain:11434`

## Canonical OpenClaw Contract
OpenClaw must be pinned to:
- version `2026.4.2`

OpenClaw phase-1 extension set:
- `ollama`
- `telegram`
- `webhooks`
- `shared`

OpenClaw phase-1 exclusions:
- `browser`
- voice/call
- media generation
- extra channels

## Canonical File Ownership
### Root contract files
- `.env.example`
- `docker-compose.yml`

### Gateway contract files
- `openclaw/Dockerfile`
- `openclaw/config/openclaw.config.yaml`
- `openclaw/config/model-routing.yaml`
- `openclaw/config/permissions.yaml`

### Bridge contract files
- `deploy/ollama-fastapi/api/main.py`
- `deploy/ollama-fastapi/api/Dockerfile`
- `deploy/ollama-fastapi/api/requirements.txt`
- `deploy/ollama-fastapi/openclaw.config.example.yaml`

### Brain contract files
- `ollama/Modelfile`
- `ollama/scripts/pull-model.sh`
- `ollama/scripts/healthcheck.sh`

## Change Control Rule
Any change to the following values requires synchronized updates across docs and runtime files:
- service names
- network name
- model identifier
- provider base URL
- bridge API auth variable name
- Telegram ingress variable names
- Docker socket placement

## Exit Condition
The configuration contract is considered frozen when:
- all phase-1 documents reference the same service names
- all phase-1 documents reference the same primary model
- the bridge path is fixed as the only inference path
