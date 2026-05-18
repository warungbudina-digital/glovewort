# File-by-File Specification

This document defines the intended purpose of each phase-1 file before implementation starts.

## Root Files

### `README.md`
Purpose:
- explain project goal
- state the brain/hand split
- state the OpenClaw 2026.4.2 pin
- point readers to architecture and deployment docs

### `.env.example`
Purpose:
- define all runtime environment variables required for phase 1

Expected sections:
- Telegram settings
- bridge auth settings
- OpenClaw gateway token/settings
- Ollama model selection
- port/network defaults

### `docker-compose.yml`
Purpose:
- declare the three phase-1 services
- bind them to one shared network
- mount Docker socket only into `openclaw-gateway`
- declare health checks and startup dependencies

## `docs/`

### `docs/ARCHITECTURE.md`
Purpose:
- earlier architecture summary

### `docs/ARCHITECTURE_FINAL.md`
Purpose:
- final authoritative architecture decision
- source of truth for implementation scope

### `docs/SPEC.md`
Purpose:
- concise system specification and scope boundaries

### `docs/FILE_TREE.md`
Purpose:
- intended project layout reference

### `docs/FILE_SPEC.md`
Purpose:
- define every planned file and its role before coding

### `docs/CODE_PLAN.md`
Purpose:
- describe implementation order and responsibilities without code

### `docs/DEPLOYMENT.md`
Purpose:
- explain deployment sequence and runtime assumptions

### `docs/TELEGRAM.md`
Purpose:
- explain Telegram ingress behavior, constraints, and testing scope

### `docs/SECURITY.md`
Purpose:
- explain trust boundaries and privilege placement

### `docs/TROUBLESHOOTING.md`
Purpose:
- initial failure-domain guide

## `deploy/ollama-fastapi/`
This subtree is derived from the validated reference pattern and should remain close to the reference unless a change is justified.

### `deploy/ollama-fastapi/.env.example`
Purpose:
- bridge-level env template
- bridge auth and tunnel-related vars if later extended

### `deploy/ollama-fastapi/README.md`
Purpose:
- explain bridge deployment behavior and usage assumptions

### `deploy/ollama-fastapi/docker-compose.yml`
Purpose:
- reference compose for bridge + Ollama pattern
- may be adapted or absorbed into root compose later

### `deploy/ollama-fastapi/openclaw.config.example.yaml`
Purpose:
- reference provider wiring from OpenClaw to the bridge API

### `deploy/ollama-fastapi/api/Dockerfile`
Purpose:
- build the FastAPI bridge container

### `deploy/ollama-fastapi/api/main.py`
Purpose:
- expose `/healthz`
- expose `/v1/chat/completions`
- translate OpenAI-style chat payloads to Ollama

### `deploy/ollama-fastapi/api/requirements.txt`
Purpose:
- pin minimal Python deps for the bridge

## `openclaw/`

### `openclaw/Dockerfile`
Purpose:
- build a lightweight OpenClaw 2026.4.2 image
- keep only required extensions
- avoid browser/runtime bloat

### `openclaw/config/openclaw.config.yaml`
Purpose:
- primary runtime config for OpenClaw
- define provider base URL, model default, and Telegram ingress

### `openclaw/config/model-routing.yaml`
Purpose:
- document or define model/provider routing behavior
- phase 1 should still route to one primary bridge-backed model

### `openclaw/config/permissions.yaml`
Purpose:
- document execution boundaries and allowed action classes
- especially Docker-action restrictions

### `openclaw/scripts/entrypoint.sh`
Purpose:
- container startup wrapper
- environment validation before process launch

### `openclaw/scripts/wait-for-bridge.sh`
Purpose:
- block gateway start until the bridge is reachable

### `openclaw/scripts/healthcheck.sh`
Purpose:
- gateway health verification

## `ollama/`

### `ollama/Modelfile`
Purpose:
- define or document the chosen instruct model baseline if required

### `ollama/scripts/pull-model.sh`
Purpose:
- pull the required model explicitly
- avoid pulling unneeded models

### `ollama/scripts/healthcheck.sh`
Purpose:
- runtime health check for Ollama service availability

### `ollama/data/`
Purpose:
- persistent model storage

## `logs/`
Purpose:
- structured place for runtime log mounts if needed

## `state/`
Purpose:
- lightweight persistent runtime state if needed later
