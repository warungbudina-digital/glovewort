#!/usr/bin/env sh
set -eu

port=${OPENCLAW_GATEWAY_PORT:-18789}

curl -fsS "http://127.0.0.1:${port}/healthz" >/dev/null
