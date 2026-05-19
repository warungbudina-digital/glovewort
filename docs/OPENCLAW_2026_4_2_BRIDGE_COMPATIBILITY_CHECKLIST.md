# OpenClaw 2026.4.2 ↔ llm-bridge-api Compatibility Checklist

This checklist defines the minimum compatibility contract required for `glovewort` phase-1:

- **OpenClaw 2026.4.2** as the gateway/runtime
- **llm-bridge-api** as the OpenAI-compatible adapter
- **Ollama** as the actual inference backend

The goal is precise compatibility, not feature completeness.

---

## 1. Scope

This checklist covers only the path below:

```text
Telegram -> OpenClaw gateway -> llm-bridge-api -> Ollama
```

It does **not** cover:

- browser tools
- image generation
- embeddings
- function calling/tool calling over provider API
- multi-model routing
- remote tunnel topologies

---

## 2. Compatibility target

`llm-bridge-api` must behave like a sufficiently compatible **OpenAI Chat Completions** provider for OpenClaw 2026.4.2.

That means the bridge must accept OpenClaw request shapes and return response/stream shapes that OpenClaw can consume without fallback errors, generic replies, or terminated runs.

---

## 3. Request contract

### 3.1 Endpoint

Required:

- `POST /v1/chat/completions`
- `GET /healthz`

Status:

- required in phase-1
- already implemented

### 3.2 Authorization

Required behavior:

- accept `Authorization: Bearer <token>`
- if `BRIDGE_API_KEY` is empty, auth may be bypassed
- if `BRIDGE_API_KEY` is set, non-matching bearer token must return `401`

Why:

- OpenClaw provider config is using `apiKey`
- auth failures must be explicit, not silently downgraded

### 3.3 Content-Type

Required behavior:

- accept `application/json`
- reject malformed JSON with a clear 4xx response

### 3.4 Request body fields

Minimum required fields to support:

- `model`
- `messages`
- `stream`
- `temperature` (optional)
- `max_tokens` (optional)

Bridge should tolerate extra unknown fields without crashing.

Why:

- OpenClaw may send fields not used by Ollama
- bridge should ignore non-critical extras unless they change semantics

---

## 4. Message normalization contract

### 4.1 Roles

The bridge must normalize OpenClaw roles into Ollama-compatible roles.

Required mapping:

- `user` -> `user`
- `assistant` -> `assistant`
- `system` -> `system`
- `developer` -> `system`

Why:

- OpenClaw 2026.4.2 may emit `developer`
- many local chat backends do not treat `developer` as a first-class role

### 4.2 Content handling

The bridge must handle these content forms:

- plain string
- `null`
- array-of-parts

Required behavior:

- string -> pass through
- null -> empty string
- list parts -> extract text-bearing parts and join them
- only fallback to JSON serialization when no text can be extracted

Text-bearing part types to support at minimum:

- `text`
- `input_text`
- `output_text`

Why:

- OpenClaw may send structured message content
- blindly `json.dumps(...)`-ing all arrays leads to generic or irrelevant model replies

### 4.3 Non-text parts

Phase-1 behavior:

- ignore unsupported non-text parts unless they contain text payloads
- do not crash if image/tool-related parts appear
- if no text can be extracted, fallback to serialized JSON string

Why:

- phase-1 is text-first
- graceful degradation is better than crash

---

## 5. Non-stream response contract

For `stream=false`, the bridge response must look like OpenAI Chat Completions output.

Minimum required shape:

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "qwen2.5-coder:1.5b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "..."
      },
      "finish_reason": "stop"
    }
  ]
}
```

Required behavior:

- always return one `choices[0]`
- `message.role` must be `assistant`
- `message.content` must be a string
- `finish_reason` should be `stop` on normal completion

Why:

- this is the simplest stable compatibility surface for OpenClaw

---

## 6. Stream response contract

For `stream=true`, the bridge must return SSE-compatible Chat Completions chunks.

Minimum required chunk semantics:

- media type: `text/event-stream`
- one or more `data: {...}` chunks
- final stop chunk
- terminal `data: [DONE]`

Required chunk shape:

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "qwen2.5-coder:1.5b",
  "choices": [
    {
      "index": 0,
      "delta": { "content": "partial text" },
      "finish_reason": null
    }
  ]
}
```

Final chunk:

```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion.chunk",
  "created": 1234567890,
  "model": "qwen2.5-coder:1.5b",
  "choices": [
    {
      "index": 0,
      "delta": {},
      "finish_reason": "stop"
    }
  ]
}
```

And then:

```text
data: [DONE]
```

### 6.1 Lifecycle rule

Critical requirement:

- the HTTP client used to stream from Ollama must remain alive for the entire SSE generator lifecycle

Why:

- otherwise OpenClaw sees `terminated`
- this already occurred in phase-1 before patching

---

## 7. Error contract

### 7.1 Auth errors

Return:

- `401` with a simple JSON error body

### 7.2 Ollama upstream errors

Return:

- propagated 4xx/5xx when possible
- error body should be readable text or JSON
- do not swallow upstream failure into generic success

### 7.3 Unexpected bridge exceptions

Required behavior:

- fail visibly in logs
- return a non-2xx response
- do not return fake success payloads

Why:

- silent corruption is worse than explicit failure

---

## 8. Health contract

### 8.1 `/healthz`

Required behavior:

- verify bridge process is alive
- verify Ollama upstream is reachable
- return `200` only when the bridge can successfully contact Ollama

Current phase-1 approach:

- `GET {OLLAMA_URL}/api/tags`

That is acceptable for phase-1.

### 8.2 Container healthcheck command

Required behavior:

- must use a command that actually exists in the image
- should not depend on `curl`/`wget` unless installed

Current phase-1 preferred check:

- Python stdlib `urllib.request`

---

## 9. Model identity contract

Required consistency across files:

- `.env` -> `OLLAMA_MODEL=qwen2.5-coder:1.5b`
- OpenClaw config -> `ollama-bridge/qwen2.5-coder:1.5b`
- bridge default model -> `qwen2.5-coder:1.5b`
- Ollama must actually have the model pulled

Verification command:

```bash
docker compose exec -T ollama-brain ollama list
```

Why:

- identity drift causes hard-to-debug false negatives

---

## 10. OpenClaw config compatibility contract

For OpenClaw 2026.4.2, config must follow the runtime schema exactly.

Required phase-1 constraints:

- config file must be JSON5-compatible
- `gateway.mode` must be set to `local`
- model default must be under `agents.defaults.model.primary`
- provider catalog entries under `models.providers.*.models` must be arrays, not objects

Why:

- several startup failures already came from schema mismatch, not runtime logic failure

---

## 11. Logging contract

For phase-1, logs must be sufficient to isolate which layer failed.

Required visibility:

- OpenClaw gateway logs should show provider/model and embedded-run errors
- bridge logs should show startup, health hits, and traceback on failure
- Ollama logs should remain available for model-level failures

Minimum debugging commands:

```bash
docker compose logs --tail 200 openclaw-gateway
docker compose logs --tail 120 llm-bridge-api
docker compose logs --tail 120 ollama-brain
```

---

## 12. Validation checklist

A phase-1 bridge is acceptable only if all checks below pass.

### A. Container health

- [ ] `ollama-brain` is `healthy`
- [ ] `llm-bridge-api` is `healthy`
- [ ] `openclaw-gateway` is `Up`

### B. Direct bridge health

- [ ] `GET /healthz` returns `200`
- [ ] bridge health proves Ollama reachability, not just process liveness

### C. Direct completion test

- [ ] non-stream completion returns a valid Chat Completions JSON body
- [ ] content reflects the actual prompt, not a generic greeting

### D. Streaming compatibility

- [ ] OpenClaw no longer reports `terminated`
- [ ] bridge logs show no `client has been closed` errors
- [ ] Telegram responses vary with prompt content

### E. Config correctness

- [ ] no JSON5 parse errors
- [ ] no schema errors for `agents` / `models` blocks
- [ ] no gateway-mode block on startup

---

## 13. Known phase-1 pitfalls

These are already observed failure classes in this project.

### Pitfall 1: wrong Docker build context

Symptom:

- `main.py` / `requirements.txt` not found during build

Fix:

- set bridge build context to `./deploy/ollama-fastapi/api`

### Pitfall 2: healthcheck binary missing

Symptom:

- bridge is up but marked unhealthy

Fix:

- use Python stdlib healthcheck instead of `curl`/`wget`

### Pitfall 3: YAML config used where JSON5 is required

Symptom:

- `JSON5 invalid character` on startup

Fix:

- use JSON5-style object config

### Pitfall 4: OpenClaw schema mismatch

Symptom:

- `models.defaults` rejected
- `models.providers.*.models` object rejected

Fix:

- use `agents.defaults.model.primary`
- use provider `models` arrays

### Pitfall 5: stream client lifecycle bug

Symptom:

- Telegram replies `terminated`
- bridge logs: `Cannot send a request, as the client has been closed`

Fix:

- keep `AsyncClient` alive inside the streaming generator

### Pitfall 6: structured content passed through naively

Symptom:

- model answers with the same generic greeting for unrelated prompts

Fix:

- normalize array-of-parts content into plain text before forwarding to Ollama

---

## 14. Next hardening steps

Once the bridge passes phase-1 compatibility, the next improvements should be:

1. add structured request/response logging at debug level only
2. add content normalization tests
3. add stream compatibility tests
4. add explicit timeout/error mapping for Ollama upstream failures
5. decide whether to support tool-call-compatible responses later

---

## 15. Bottom line

The bridge is considered compatible with OpenClaw 2026.4.2 only when:

- config schema is valid
- direct completion works
- streaming works
- Telegram replies reflect the real prompt
- OpenClaw no longer reports `terminated`

Until then, failures should be treated as **bridge contract bugs**, not as evidence that OpenClaw core logic is broken.
