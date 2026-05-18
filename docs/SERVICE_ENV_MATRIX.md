# Service Environment Matrix

This document defines which environment variables belong to which service in phase 1.

## Purpose
Prevent ambiguous variable placement and reduce config drift.

## Global Naming Rule
Variable names should indicate ownership clearly:
- `TELEGRAM_*` for Telegram ingress
- `OPENCLAW_*` for gateway runtime
- `BRIDGE_*` for bridge API behavior
- `OLLAMA_*` for Ollama runtime behavior

## Root `.env.example`
The root env file is the canonical source for operator-provided values.

## Service Matrix

### 1. `openclaw-gateway`
Required variables:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_MODE`
- `OPENCLAW_GATEWAY_TOKEN`
- `OPENCLAW_CONFIG_PATH`
- `OPENCLAW_MODEL_PROVIDER`
- `OPENCLAW_MODEL_NAME`
- `BRIDGE_API_KEY`

Consumes indirectly:
- `BRIDGE_BASE_URL`

Does not own:
- `OLLAMA_KEEP_ALIVE`
- `OLLAMA_NUM_PARALLEL`
- `OLLAMA_MAX_LOADED_MODELS`

### 2. `llm-bridge-api`
Required variables:
- `BRIDGE_API_KEY`
- `BRIDGE_TIMEOUT_SECONDS`
- `OLLAMA_MODEL`
- `OLLAMA_PORT`

Derived runtime values:
- `OLLAMA_URL=http://ollama-brain:${OLLAMA_PORT}`

Does not own:
- `TELEGRAM_BOT_TOKEN`
- `OPENCLAW_GATEWAY_TOKEN`

### 3. `ollama-brain`
Required variables:
- `OLLAMA_PORT`
- `OLLAMA_MODEL`
- `OLLAMA_KEEP_ALIVE`
- `OLLAMA_NUM_PARALLEL`
- `OLLAMA_MAX_LOADED_MODELS`

Does not own:
- `TELEGRAM_BOT_TOKEN`
- `BRIDGE_API_KEY`
- `OPENCLAW_GATEWAY_TOKEN`

## Variable Intent Matrix

### Telegram
- `TELEGRAM_BOT_TOKEN`: auth secret for ingress
- `TELEGRAM_BOT_MODE`: explicit ingress mode

### OpenClaw
- `OPENCLAW_GATEWAY_TOKEN`: gateway auth/identity token
- `OPENCLAW_CONFIG_PATH`: runtime config path
- `OPENCLAW_MODEL_PROVIDER`: canonical configured provider name
- `OPENCLAW_MODEL_NAME`: canonical configured model name used by gateway logic

### Bridge
- `BRIDGE_API_KEY`: auth boundary between OpenClaw and bridge
- `BRIDGE_PORT`: bind/default bridge port
- `BRIDGE_TIMEOUT_SECONDS`: upstream call timeout
- `BRIDGE_BASE_URL`: canonical OpenClaw-facing bridge URL

### Ollama
- `OLLAMA_PORT`: internal runtime port
- `OLLAMA_MODEL`: primary model identifier
- `OLLAMA_KEEP_ALIVE`: model residency policy
- `OLLAMA_NUM_PARALLEL`: concurrency bound
- `OLLAMA_MAX_LOADED_MODELS`: memory control bound

## Validation Rules
The env matrix is valid only if:
- no Telegram secrets are required by `ollama-brain`
- no Docker control values are required by `llm-bridge-api`
- no bridge auth is required by Ollama itself
- OpenClaw is the only service that combines ingress and execution concerns

## Exit Condition
The service env matrix is frozen when:
- each variable has one clear owner
- each service has a minimal required variable set
- no phase-1 runtime file contradicts this mapping
