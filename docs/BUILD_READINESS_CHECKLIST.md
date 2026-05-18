# Build Readiness Checklist

This checklist must pass before the first base-image build is treated as valid.

## Scope
The target build in this phase is only:
- `openclaw-2026.4.2-base:local`

The target source is only:
- `/home/node/.openclaw/workspace/partner-lama/openclaw-main`

## A. Source Integrity
- [ ] Source directory exists
- [ ] `package.json` version is `2026.4.2`
- [ ] upstream `Dockerfile` exists
- [ ] `extensions/` exists
- [ ] reference `deploy/ollama-fastapi` exists

## B. Build Contract Consistency
- [ ] canonical image tag is `openclaw-2026.4.2-base:local`
- [ ] canonical extension set is `ollama telegram webhooks shared`
- [ ] `OPENCLAW_VARIANT=default`
- [ ] `OPENCLAW_BUNDLED_PLUGIN_DIR=extensions`
- [ ] `OPENCLAW_DOCKER_APT_UPGRADE=0`
- [ ] `OPENCLAW_INSTALL_BROWSER` is empty
- [ ] `OPENCLAW_INSTALL_DOCKER_CLI` is empty

## C. Phase-1 Architecture Consistency
- [ ] no browser requirement in phase 1
- [ ] no cloudflared dependency in phase 1 core
- [ ] one primary model only
- [ ] Docker socket belongs only to `openclaw-gateway`
- [ ] OpenClaw talks to bridge, not directly to Ollama

## D. Runtime File Consistency
- [ ] `.env.example` points to `OPENCLAW_BASE_IMAGE=openclaw-2026.4.2-base:local`
- [ ] root `docker-compose.yml` uses `llm-bridge-api`
- [ ] root `docker-compose.yml` uses `ollama-brain`
- [ ] root `docker-compose.yml` mounts Docker socket only on `openclaw-gateway`
- [ ] `openclaw/config/openclaw.config.yaml` points to `${BRIDGE_BASE_URL}`
- [ ] runtime config uses `qwen2.5-coder:1.5b` consistently

## E. Host Tooling Readiness
- [ ] Docker daemon is reachable
- [ ] Docker build is permitted in this environment
- [ ] disk space is sufficient for a full upstream OpenClaw image build
- [ ] network access is available for dependency/image fetches

## F. Build Success Criteria
The first build is considered successful only if:
- [ ] build exits successfully
- [ ] image tag `openclaw-2026.4.2-base:local` exists locally
- [ ] image can be inspected via Docker metadata

## G. Post-Build Immediate Verification
- [ ] image tag is correct
- [ ] image was built from the intended source path
- [ ] image is usable as parent of `glovewort/openclaw/Dockerfile`
- [ ] no unexpected browser/runtime additions were intentionally requested
