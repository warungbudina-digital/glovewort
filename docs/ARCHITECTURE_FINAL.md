# Final Architecture

## Scope
This project defines a lightweight single-host deployment where:

- **Ollama** is the primary reasoning engine (**brain**)
- **OpenClaw 2026.4.2** is the operational executor (**hand**)
- **Telegram** is the operator ingress
- **FastAPI bridge** is the protocol adapter between OpenClaw and Ollama

The design is intentionally constrained to a stable phase-1 baseline.

## Version Pinning
- OpenClaw source baseline: **2026.4.2**
- Reference source tree: `/home/node/.openclaw/workspace/partner-lama/openclaw-main`
- Reference deployment pattern: `deploy/ollama-fastapi`

## Core Services

### 1. openclaw-gateway
Responsibilities:
- receive Telegram input
- run the OpenClaw gateway/runtime
- call the LLM bridge over internal HTTP
- execute approved local actions
- hold Docker socket access

Constraints:
- no browser runtime in phase 1
- no direct Ollama coupling at config level if bridge is present
- no heavy media or multi-agent extensions

### 2. llm-bridge-api
Responsibilities:
- expose an OpenAI-compatible `/v1/chat/completions` surface
- enforce API-key based protection
- normalize request/response payloads
- isolate OpenClaw from Ollama-specific protocol details

Constraints:
- internal-only in phase 1
- one upstream model backend at a time

### 3. ollama-brain
Responsibilities:
- host the primary instruct model
- answer prompts forwarded by the bridge
- remain internal to the Docker network

Constraints:
- one primary loaded model
- tuned for low-memory, low-concurrency operation
- no Docker socket access

## Core Network Topology
All core services live on one Docker network.

```text
Telegram User
  -> Telegram Bot/API
  -> openclaw-gateway
  -> llm-bridge-api
  -> ollama-brain
  -> llm-bridge-api
  -> openclaw-gateway
  -> Telegram response
```

## Socket and Trust Placement
### Docker socket
Mounted only into `openclaw-gateway`.

Reasoning:
- execution authority belongs to the hand layer
- inference authority belongs to the brain layer
- the model runtime should not control the host runtime

### Trust model
- Telegram input is untrusted
- model output is advisory
- tool execution is privileged
- Docker socket actions require explicit guardrails

## Phase-1 OpenClaw Extension Set
Required:
- `ollama`
- `telegram`
- `webhooks`
- `shared`

Excluded in phase 1:
- `browser`
- voice/call extensions
- media generation extensions
- vector DB integrations
- secondary channels
- multi-host orchestration features

## Why the bridge is part of the core
The FastAPI bridge is not optional plumbing in this design. It is part of the architecture because it:
- stabilizes the protocol surface for OpenClaw
- keeps auth and timeout policy in one place
- makes model replacement easier
- creates a future insertion point for specialist model routing

## Why cloudflared is not part of the phase-1 core
Cloudflared is useful for external exposure or cross-host access, but it is not part of the minimal stable core because:
- it adds an extra external dependency
- it is not needed for intra-host communication
- it complicates debugging before the core is proven stable

## Operational Boundaries
### Included in phase 1
- single host
- Telegram ingress
- one OpenClaw gateway
- one bridge API
- one Ollama runtime
- one Docker network
- Docker socket on OpenClaw only

### Deferred to later phases
- cloudflared
- remote specialist model containers
- browser automation
- vector memory
- media pipelines
- render/analyzer workloads
- multi-host orchestration

## Failure Domains
1. Telegram ingress failure
2. OpenClaw runtime/configuration failure
3. bridge API failure
4. Ollama runtime/model failure
5. Docker socket action failure

The design intentionally keeps these domains separable.

## Final Architecture Decision
The project should be built as:

- **brain**: `ollama-brain`
- **adapter**: `llm-bridge-api`
- **hand**: `openclaw-gateway`
- **ingress**: Telegram
- **execution privilege**: Docker socket only on the hand layer

This is the baseline to carry forward into file-level specs and code planning.
