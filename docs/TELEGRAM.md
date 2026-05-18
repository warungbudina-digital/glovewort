# Telegram

## Role
Telegram is the operational ingress for the hand layer.

## Flow
User -> Telegram Bot/API -> `openclaw-gateway` -> bridge -> Ollama -> response

## Phase 1 scope
- command input
- response output
- no multi-channel expansion yet

## Constraints
- keep parsing simple
- keep actions explicit
- keep logs attributable to each request
