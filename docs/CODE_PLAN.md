# Code Plan

This document describes the implementation order without writing code yet.

## Implementation Rule
Use **OpenClaw 2026.4.2** only. Do not re-base the project onto another OpenClaw version.

## Phase Order

### Phase 0 — preserve reference
Goal:
- keep `/home/node/.openclaw/workspace/partner-lama/openclaw-main` as read-only reference baseline
- treat `deploy/ollama-fastapi` as the inference-pattern source

Deliverable:
- documented mapping from reference files to target repo files

### Phase 1 — finalize docs and boundaries
Goal:
- freeze architecture, file tree, file specs, security boundaries, and service responsibilities

Deliverable:
- authoritative docs in `docs/`

### Phase 2 — root runtime skeleton
Goal:
- add non-executable scaffolding for:
  - `.env.example`
  - `docker-compose.yml`
  - `openclaw/`
  - `ollama/`
  - `deploy/ollama-fastapi/`

Deliverable:
- file skeletons only
- no build/run yet

### Phase 3 — bridge alignment plan
Goal:
- define how the existing `deploy/ollama-fastapi` pattern is normalized into this repo

Key questions:
- which files remain identical to reference
- which files are adapted for single-host phase 1
- whether root compose wraps or supersedes deploy compose

Deliverable:
- explicit adaptation notes in docs

### Phase 4 — OpenClaw-hand image plan
Goal:
- define the smallest valid OpenClaw 2026.4.2 build shape for the gateway container

Required decisions:
- extension set
- environment variable contract
- config file location
- startup/wait strategy

Deliverable:
- Dockerfile plan and config contract

### Phase 5 — composition plan
Goal:
- define exact service relationships in `docker-compose.yml`

Required decisions:
- service names
- ports
- health checks
- `depends_on` logic
- network naming
- volume mounts
- Docker socket mount placement

Deliverable:
- compose specification, still design-only

### Phase 6 — validation plan
Goal:
- define tests before implementation is considered complete

Required validations:
1. Ollama service health
2. bridge service health
3. OpenClaw to bridge connectivity
4. Telegram ingress health
5. end-to-end Telegram roundtrip
6. Docker socket visibility only on gateway

Deliverable:
- test checklist document

## Non-Goals for Current Planning Cycle
Do not plan code for these yet:
- browser runtime
- cloudflared
- remote model federation
- vector DB
- media generation
- render/analyzer tools
- multi-host orchestration

## Dependency Logic
Implementation must respect this dependency order:
1. architecture
2. file spec
3. security boundary
4. runtime skeleton
5. bridge mapping
6. compose structure
7. validation plan
8. implementation

## Exit Criteria Before Coding Starts
Do not start implementation until:
- the architecture is frozen
- file responsibilities are documented
- service boundaries are clear
- Docker socket placement is accepted
- phase-1 exclusions are accepted
