# Base Image Build Plan

This document defines how the required base image for `glovewort` should be produced.

## Objective
Produce a local image named:
- `openclaw-2026.4.2-base:local`

This image is the pinned OpenClaw 2026.4.2 runtime base used by the `openclaw-gateway` overlay in this repo.

## Source of Truth
The base image must be built from:
- `/home/node/.openclaw/workspace/partner-lama/openclaw-main`

Version must match:
- `2026.4.2`

This is non-negotiable for phase 1.

## Why a Separate Base Image Exists
`glovewort` is not intended to vendor the entire OpenClaw source tree.

Instead:
- the upstream OpenClaw 2026.4.2 source remains the build origin
- `glovewort` adds a thin deployment-specific overlay
- the overlay injects config and startup behavior for the brain/hand architecture

This separation keeps the project:
- smaller
- easier to reason about
- easier to update at the deployment layer without rewriting upstream internals

## Base Image Responsibilities
The base image must contain:
- OpenClaw 2026.4.2 runtime
- `openclaw.mjs`
- built runtime assets
- required bundled extensions for phase 1
- required system packages for gateway runtime

The base image must not assume:
- browser runtime
- cloudflared
- media pipelines
- project-specific configs from `glovewort`

## Required Extension Set
For the base image used by `glovewort`, the intended extension set is:
- `ollama`
- `telegram`
- `webhooks`
- `shared`

Reasoning:
- `telegram` for ingress
- `ollama` for provider path support
- `webhooks` for light integration surface
- `shared` for common runtime support

## Explicit Build-Time Exclusions
Do not include these in the base image for phase 1:
- `browser`
- Docker CLI unless a later review requires it
- cloudflared
- extra model providers not required by the architecture

## Build Strategy
The base image should be built using the upstream OpenClaw Dockerfile from 2026.4.2, not a rewritten Dockerfile in `glovewort`.

Reason:
- reduces drift from the validated upstream build logic
- keeps risk localized to deployment overlay files
- preserves compatibility with upstream runtime expectations

## Canonical Build Inputs
Build context root:
- `/home/node/.openclaw/workspace/partner-lama/openclaw-main`

Canonical image tag output:
- `openclaw-2026.4.2-base:local`

Canonical build arguments:
- `OPENCLAW_EXTENSIONS="ollama telegram webhooks shared"`
- `OPENCLAW_VARIANT=default`
- `OPENCLAW_BUNDLED_PLUGIN_DIR=extensions`
- `OPENCLAW_DOCKER_APT_UPGRADE=0`
- `OPENCLAW_INSTALL_BROWSER=`
- `OPENCLAW_INSTALL_DOCKER_CLI=`

## Why `OPENCLAW_DOCKER_APT_UPGRADE=0`
For this deployment baseline:
- build determinism matters more than repeated package upgrades
- build time and image size should stay controlled
- the overlay layer is already deployment-specific

This keeps the base image leaner and closer to the already-tested pattern used earlier for Cloud Shell helper builds.

## Why no Docker CLI in the base image
Current phase-1 design mounts:
- `/var/run/docker.sock`

into `openclaw-gateway`.

That does not automatically require the Docker CLI inside the container unless the intended actions specifically depend on invoking `docker` commands.

Current design assumption:
- OpenClaw will operate without Docker CLI until proven otherwise
- if Docker CLI is required later, it should be added intentionally after review

## Output Contract
After build, the following must be true:
- the local image exists as `openclaw-2026.4.2-base:local`
- `glovewort` root `.env.example` points to that tag
- `openclaw/Dockerfile` in `glovewort` can layer on top of it without changing the upstream runtime internals

## Pre-Build Checklist
Before building the base image, verify:
- source path exists
- source version is `2026.4.2`
- phase-1 extension set is accepted
- no browser dependency is required
- no Cloudflare tunnel dependency is required

## Post-Build Checklist
After building the base image, verify:
- the image tag is correct
- the image contains `openclaw.mjs`
- the image is suitable as a parent for `openclaw/Dockerfile` in `glovewort`
- the image does not include phase-1 excluded features unintentionally

## Non-Goals of This Plan
This document does not yet:
- run the build
- validate the image contents live
- start any container
- patch the upstream OpenClaw source tree

It only freezes the base-image plan so the next step can be executed cleanly.

## Next Step After This Plan
Once this plan is accepted, the next correct step is:
1. create a build-readiness checklist
2. verify repo/runtime files against the plan
3. perform the first base-image build
