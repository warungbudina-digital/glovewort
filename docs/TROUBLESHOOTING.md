# Troubleshooting

## Failure domains
1. Telegram ingress
2. OpenClaw gateway
3. LLM bridge
4. Ollama runtime
5. Docker socket actions

## First checks
- Is `ollama-brain` healthy?
- Is `llm-bridge-api` healthy?
- Can `openclaw-gateway` reach the bridge?
- Is Telegram ingress authenticated correctly?
- Is the model name consistent across all configs?

## Typical early faults
- wrong bridge base URL
- wrong model identifier
- OpenClaw starts before the bridge is ready
- Docker socket mounted to the wrong service
