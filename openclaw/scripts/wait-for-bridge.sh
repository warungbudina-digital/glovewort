#!/usr/bin/env sh
set -eu

base_url=${BRIDGE_BASE_URL:-http://llm-bridge-api:8000/v1}
health_url=$(printf '%s' "$base_url" | sed 's#/v1$##')/healthz
attempts=${WAIT_FOR_BRIDGE_ATTEMPTS:-30}
sleep_seconds=${WAIT_FOR_BRIDGE_INTERVAL_SECONDS:-2}

count=1
while [ "$count" -le "$attempts" ]; do
  if curl -fsS "$health_url" >/dev/null 2>&1; then
    exit 0
  fi
  sleep "$sleep_seconds"
  count=$((count + 1))
done

echo "bridge not ready after ${attempts} attempts: $health_url" >&2
exit 1
