# Compose Specification

This document defines the phase-1 `docker-compose.yml` design without writing the final runtime file yet.

## Compose Objective
Provide a single-host composition for:
- `openclaw-gateway`
- `llm-bridge-api`
- `ollama-brain`

using:
- one Docker network
- explicit health checks
- ordered startup
- Docker socket mount only for the gateway

## Services

### 1. `ollama-brain`
Purpose:
- host the primary instruct model
- serve internal inference requests

Expected characteristics:
- persistent volume for model data
- low parallelism settings
- internal-only service exposure
- health check based on local Ollama readiness

Expected mounts:
- Ollama data volume only

Explicitly forbidden mounts:
- Docker socket

### 2. `llm-bridge-api`
Purpose:
- expose an OpenAI-compatible API to OpenClaw
- translate payloads to Ollama upstream

Expected characteristics:
- depends on healthy `ollama-brain`
- internal HTTP access only in phase 1
- API-key protected
- explicit timeout environment variables

Expected mounts:
- none, unless logs are later externalized

Explicitly forbidden mounts:
- Docker socket

### 3. `openclaw-gateway`
Purpose:
- host OpenClaw 2026.4.2 runtime
- receive Telegram ingress
- call bridge API
- execute local actions

Expected characteristics:
- depends on healthy `llm-bridge-api`
- minimal extension set
- explicit config mount or baked config path
- Docker socket access

Expected mounts:
- Docker socket
- optional config mount
- optional persistent runtime state mount

## Network Specification

### Network name
Preferred logical name:
- `brain_hand_net`

### Network behavior
- all three core services join the same network
- service-to-service calls use Docker DNS names
- no public dependency for internal model access

## Port Policy

### `ollama-brain`
- no required public bind in phase 1
- internal service port only

### `llm-bridge-api`
- internal service access only in phase 1
- optional localhost bind only for debugging if explicitly needed

### `openclaw-gateway`
- Telegram operation may not require a public port depending on provider mode
- any debug or admin ports should remain non-public by default

## Health Check Policy

### `ollama-brain`
Health should confirm:
- process responds
- model runtime endpoint is alive

### `llm-bridge-api`
Health should confirm:
- `/healthz` responds successfully
- upstream dependency is reachable

### `openclaw-gateway`
Health should confirm:
- process is alive
- config loads successfully
- bridge dependency is reachable or startup gate has already validated this

## Dependency Ordering
Required startup order:
1. `ollama-brain`
2. `llm-bridge-api`
3. `openclaw-gateway`

Desired compose semantics:
- `llm-bridge-api` waits on healthy `ollama-brain`
- `openclaw-gateway` waits on healthy `llm-bridge-api`

## Volume Policy

### Required volumes
- persistent Ollama model storage

### Optional volumes
- OpenClaw config bind or dedicated config file mount
- lightweight runtime state/log bind

### Forbidden volume placements
- no Docker socket on bridge
- no Docker socket on Ollama

## Environment Variable Policy

### `ollama-brain`
Expected categories:
- model concurrency control
- keep-alive tuning
- model storage/runtime settings

### `llm-bridge-api`
Expected categories:
- upstream Ollama URL
- default model identifier
- bridge timeout
- bridge API key

### `openclaw-gateway`
Expected categories:
- gateway token/config
- Telegram auth/config
- provider base URL
- bridge API key for model provider auth

## Compose Exit Criteria
The compose design is acceptable only if it satisfies all of the following:
- OpenClaw 2026.4.2 is the runtime basis
- bridge remains in the path between OpenClaw and Ollama
- Docker socket exists only on the gateway
- no browser is required
- no cloudflared is required
- internal networking is sufficient for all phase-1 communication
