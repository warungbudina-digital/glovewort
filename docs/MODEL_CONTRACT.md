# Model Contract

This document freezes the phase-1 model assumptions before implementation.

## Purpose
The model layer must be predictable. Phase 1 is not a multi-model design.

## Phase-1 Model Rule
Exactly one primary instruct model is used for the core system.

Current target identifier:
- `qwen2.5-coder:1.5b`

This identifier must be used consistently in:
- `.env.example`
- `docker-compose.yml`
- bridge configuration
- OpenClaw provider config
- tests and validation payloads

## Why a Single Model in Phase 1
Reasoning:
- host resources are constrained
- startup and validation stay simpler
- debugging the bridge path is easier
- OpenClaw hand behavior is easier to reason about

## Model Role
### Ollama model responsibilities
- follow instructions
- provide compact reasoning
- return actionable assistant output
- remain lightweight enough for small-host operation

### The model does not own
- Docker actions
- Telegram ingress
- container orchestration
- direct host privileges

## Model-to-Bridge Contract
The bridge must send:
- chat-style request payloads
- one selected model identifier
- timeout-bounded requests

The bridge must receive:
- assistant text output
- predictable response shape

## OpenClaw-to-Model Contract
OpenClaw must treat the model as:
- reasoning source
- action advisor
- not a privileged executor

Any action suggested by the model still passes through OpenClaw policy.

## Phase-1 Non-Goals
Not included yet:
- multiple specialist models
- routing between coding/writing/classifier models
- remote model federation
- fallback chains
- tool-selected model switching

## Upgrade Rule
If a future phase changes the primary model, the following must be updated together:
- `.env.example`
- bridge env
- OpenClaw config
- validation checklist
- troubleshooting examples

## Exit Condition
The model contract is frozen when:
- one model identifier is accepted as canonical
- no phase-1 file references a second primary model
- the bridge and OpenClaw both point to the same model string
