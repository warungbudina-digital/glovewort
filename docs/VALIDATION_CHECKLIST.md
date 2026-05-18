# Validation Checklist

This checklist defines what must be proven before the phase-1 system is considered correct.

## Validation Scope
The following must be validated:
- service health
- dependency wiring
- Telegram ingress
- OpenClaw-to-bridge-to-Ollama flow
- Docker socket placement
- basic restart resilience

## Pre-Run Validation
Before any runtime validation:
- OpenClaw version is confirmed as **2026.4.2**
- chosen model identifier is consistent across all configs
- bridge auth key is configured
- Telegram credentials are configured
- Docker socket mount exists only on `openclaw-gateway`

## Service Health Validation

### V1 — Ollama health
Pass criteria:
- `ollama-brain` is running
- Ollama endpoint responds
- model runtime is available

### V2 — Bridge health
Pass criteria:
- `llm-bridge-api` is running
- `/healthz` returns success
- upstream Ollama dependency is healthy

### V3 — Gateway health
Pass criteria:
- `openclaw-gateway` is running
- configuration loads cleanly
- provider wiring resolves to the bridge endpoint

## Connectivity Validation

### V4 — Gateway to bridge
Pass criteria:
- OpenClaw can reach `llm-bridge-api`
- provider call path does not require any public tunnel

### V5 — Bridge to Ollama
Pass criteria:
- bridge can reach `ollama-brain`
- chat payloads are translated correctly

## Functional Validation

### V6 — Direct bridge inference
Pass criteria:
- a minimal `/v1/chat/completions` request succeeds
- response shape is compatible with OpenClaw expectations

### V7 — Telegram ingress
Pass criteria:
- Telegram message reaches OpenClaw
- gateway does not reject valid ingress configuration

### V8 — End-to-end roundtrip
Pass criteria:
- Telegram input -> OpenClaw -> bridge -> Ollama -> OpenClaw -> Telegram response succeeds

## Privilege Validation

### V9 — Docker socket scope
Pass criteria:
- `openclaw-gateway` sees Docker socket
- `llm-bridge-api` does not
- `ollama-brain` does not

## Resilience Validation

### V10 — Startup ordering
Pass criteria:
- `openclaw-gateway` does not try to operate before the bridge is healthy
- bridge does not operate before Ollama is healthy

### V11 — Restart resilience
Pass criteria:
- restarting `llm-bridge-api` does not permanently break `openclaw-gateway`
- restarting `ollama-brain` can recover cleanly through the dependency chain

## Negative Validation

### V12 — Unsupported phase-1 features remain absent
Pass criteria:
- no browser runtime dependency exists
- no cloudflared dependency exists in the phase-1 core
- no vector DB dependency exists in the phase-1 core

## Acceptance Rule
Phase 1 is only considered ready for implementation review when all validation items have a defined test method and a clear pass/fail interpretation.
