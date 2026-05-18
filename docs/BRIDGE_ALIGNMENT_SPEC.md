# Bridge Alignment Specification

This document defines how the validated `deploy/ollama-fastapi` reference pattern from OpenClaw 2026.4.2 is carried into `glovewort`.

## Reference Source
- Reference tree: `/home/node/.openclaw/workspace/partner-lama/openclaw-main`
- Reference deployment subtree: `deploy/ollama-fastapi`

## Design Intent
The bridge layer remains a core architectural component, not a temporary helper. It exists to:
- give OpenClaw a stable OpenAI-compatible inference surface
- centralize auth, timeout, and payload normalization
- isolate Ollama protocol details from OpenClaw configuration
- create an insertion point for future specialist model routing

## Files Mapped from the Reference

### `deploy/ollama-fastapi/api/main.py`
Reference role:
- minimal OpenAI-compatible adapter over Ollama chat

Glovewort role:
- remain the core inference adapter
- continue exposing `/healthz` and `/v1/chat/completions`
- stay intentionally small and text-first in phase 1

### `deploy/ollama-fastapi/api/Dockerfile`
Reference role:
- small Python runtime image for the bridge

Glovewort role:
- remain close to the reference unless packaging constraints require a minimal change

### `deploy/ollama-fastapi/api/requirements.txt`
Reference role:
- minimal runtime dependencies for FastAPI/httpx/pydantic stack

Glovewort role:
- stay minimal
- no extra inference dependencies should be added here

### `deploy/ollama-fastapi/openclaw.config.example.yaml`
Reference role:
- show how OpenClaw points to the bridge provider

Glovewort role:
- define the provider wiring pattern for OpenClaw 2026.4.2
- serve as the basis for `openclaw/config/openclaw.config.yaml`

### `deploy/ollama-fastapi/.env.example`
Reference role:
- define bridge auth/tunnel variables

Glovewort role:
- keep bridge auth variables
- treat tunnel variables as optional or deferred unless phase 2 explicitly introduces cloudflared

### `deploy/ollama-fastapi/docker-compose.yml`
Reference role:
- deploy the bridge stack around Ollama

Glovewort role:
- remain the conceptual source for service relationships
- not necessarily the final top-level compose file for this repo

## Required Adaptations

### Adaptation 1 — Docker socket placement
Reference pattern currently mounts Docker socket into the Ollama side.

For glovewort this is not accepted.

Required target state:
- `docker.sock` mounted only into `openclaw-gateway`
- no Docker socket access in `ollama-brain`
- no Docker socket access in `llm-bridge-api`

Reason:
- execution privilege belongs to the hand, not the brain or adapter

### Adaptation 2 — Model identifier consistency
Reference examples show inconsistent default model values.

Required target state:
- choose one primary instruct model for phase 1
- use the same identifier consistently in:
  - bridge env
  - OpenClaw provider config
  - docs
  - test payloads

### Adaptation 3 — Cloudflared demotion
Reference pattern includes cloudflared.

Required target state for phase 1:
- cloudflared is not part of the core compose
- no dependency on public tunnel for intra-host communication
- all core traffic stays inside Docker network

### Adaptation 4 — Single-host service naming
Reference pattern is written as a deploy helper.

Required target state:
- service names must align with the phase-1 architecture:
  - `openclaw-gateway`
  - `llm-bridge-api`
  - `ollama-brain`

## Non-Adaptation Rules
To avoid unnecessary divergence from the validated pattern:
- do not rewrite the bridge API protocol shape without a reason
- do not add multimodal behavior in phase 1
- do not add model routing complexity in the bridge yet
- do not turn the bridge into a general orchestration service

## Alignment Decision
The bridge subtree should be treated as:
- **reference-derived core logic**
- adapted only where required by the brain/hand trust model
- kept minimal to preserve Cloud Shell and small-host stability
