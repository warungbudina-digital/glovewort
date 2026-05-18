#!/usr/bin/env sh
set -eu

required_envs="TELEGRAM_BOT_TOKEN OPENCLAW_GATEWAY_TOKEN OPENCLAW_CONFIG_PATH BRIDGE_BASE_URL BRIDGE_API_KEY"
for name in $required_envs; do
  value=$(printenv "$name" || true)
  if [ -z "$value" ]; then
    echo "missing required env: $name" >&2
    exit 1
  fi
done

if [ ! -f "$OPENCLAW_CONFIG_PATH" ]; then
  echo "config file not found: $OPENCLAW_CONFIG_PATH" >&2
  exit 1
fi

/app/openclaw/scripts/wait-for-bridge.sh

exec node /app/openclaw.mjs gateway --bind "${OPENCLAW_GATEWAY_BIND:-lan}" --port "${OPENCLAW_GATEWAY_PORT:-18789}"
