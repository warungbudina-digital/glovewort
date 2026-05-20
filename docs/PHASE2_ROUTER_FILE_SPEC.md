# Phase-2 Deterministic Router File-by-File Specification

This document defines the file-level plan for phase-2 deterministic routing.
No runtime coding is assumed yet.

---

## 1. Scope

Phase-2 adds a router layer that determines whether a message should:

- execute a deterministic command
- read and summarize a file
- inspect Docker state
- or fall back to normal LLM chat

---

## 2. New Files

## 2.1 `router/`

New directory:

```text
router/
  Dockerfile
  requirements.txt
  app/
    main.py
    models.py
    routing.py
    handlers.py
    safety.py
    formatters.py
    logging_utils.py
```

### Purpose

Contains the deterministic router service.

---

## 3. File-by-file spec

## 3.1 `router/Dockerfile`

### Purpose

Container image for the deterministic router service.

### Responsibilities

- install minimal Python runtime
- copy router app files
- expose HTTP port for internal calls from OpenClaw

### Must not do

- host Ollama
- contain Telegram provider logic
- embed unrelated heavy dependencies

---

## 3.2 `router/requirements.txt`

### Purpose

Minimal Python dependencies for the router.

### Expected dependencies

- `fastapi`
- `uvicorn`
- `pydantic`
- optional light helper libs only if justified

### Must avoid

- heavy ML dependencies
- unnecessary SDK sprawl

---

## 3.3 `router/app/main.py`

### Purpose

HTTP entrypoint for router service.

### Responsibilities

- define FastAPI app
- expose `/healthz`
- expose routing endpoint(s), e.g. `/route`
- wire request model -> routing logic -> response model

### Expected endpoints

- `GET /healthz`
- `POST /route`

### Output contract

Should indicate whether result came from:

- `command_exec`
- `file_read`
- `docker_inspect`
- `chat_fallback`

---

## 3.4 `router/app/models.py`

### Purpose

Request/response schemas.

### Responsibilities

Define:

- incoming router request model
- command execution result model
- file read result model
- chat fallback response envelope

### Expected key models

- `RouteRequest`
- `RouteDecision`
- `ExecResult`
- `ReadResult`
- `RouteResponse`

---

## 3.5 `router/app/routing.py`

### Purpose

Deterministic classification logic.

### Responsibilities

- inspect raw message text
- match it against explicit command patterns
- decide route mode

### Expected route modes

- `command_exec`
- `file_read`
- `docker_inspect`
- `chat_fallback`

### Must not do

- execute commands directly
- call Ollama directly

This module decides only.

---

## 3.6 `router/app/handlers.py`

### Purpose

Execution handlers per route type.

### Responsibilities

- perform safe shell execution
- perform safe file reads
- perform docker inspection commands
- delegate chat fallback to bridge

### Expected handlers

- `handle_exec(...)`
- `handle_file_read(...)`
- `handle_docker_inspect(...)`
- `handle_chat_fallback(...)`

---

## 3.7 `router/app/safety.py`

### Purpose

Central safety policy.

### Responsibilities

- allowlist commands
- validate file paths
- reject destructive commands
- reject unsafe docker operations

### Example rules

Allowed:

- `pwd`
- `ls`
- `whoami`
- `docker ps`
- `docker compose ps`
- `cat <approved path>`

Denied:

- `rm`
- `mv`
- `docker rm`
- `docker stop`
- `shutdown`
- `reboot`

### Must be authoritative

No execution path should bypass `safety.py`.

---

## 3.8 `router/app/formatters.py`

### Purpose

Human-readable formatting for Telegram replies.

### Responsibilities

- format command output
- truncate long stdout safely
- distinguish raw results vs summarized results

### Why separate

Formatting logic should not be mixed into execution logic.

---

## 3.9 `router/app/logging_utils.py`

### Purpose

Consistent structured logging.

### Responsibilities

- log route decisions
- log matched commands
- log command exit codes
- log fallback-to-chat reason

### Must log

- input message summary
- chosen route
- handler result status

---

## 4. Existing Files to Modify

## 4.1 `docker-compose.yml`

### Add

New service:

- `deterministic-router`

### Responsibilities after modification

- connect router to same Docker network
- give router access to only what it needs
- optionally mount Docker socket if router executes docker commands directly

### Design decision

Prefer giving the router command execution responsibility directly, rather than forcing all execution back through model text.

---

## 4.2 `.env.example`

### Add router variables

Examples:

- `ROUTER_PORT=8090`
- `ROUTER_EXEC_TIMEOUT=20`
- `ROUTER_MAX_OUTPUT_CHARS=4000`
- `ROUTER_ALLOW_DOCKER_INSPECT=1`

---

## 4.3 `openclaw/config/openclaw.config.yaml`

### Possible phase-2 role

Still controls gateway/channel/model defaults.

### Expected change

Either:

- OpenClaw messages are routed to router first for deterministic command handling

or

- OpenClaw remains chat-facing while deterministic commands are intercepted by an external integration layer

This needs a final wiring decision before coding.

---

## 4.4 `deploy/ollama-fastapi/api/main.py`

### Role in phase-2

Remains the LLM fallback adapter.

### No longer responsible for

- command routing
- pretending to be tool executor

### Responsibilities remain

- chat completions compatibility
- stream/non-stream support
- model message normalization

---

## 5. Routing API Contract

## 5.1 Request

Example shape:

```json
{
  "channel": "telegram",
  "chat_id": "843382635",
  "message_text": "jalankan pwd lalu balas hasilnya",
  "metadata": {
    "user": "OBC-crypto"
  }
}
```

## 5.2 Response

Example shape:

```json
{
  "route": "command_exec",
  "executed": true,
  "command": "pwd",
  "exit_code": 0,
  "stdout": "/home/warungbudina/glovewort",
  "stderr": "",
  "reply_text": "Perintah: pwd\nExit code: 0\nHasil:\n/home/warungbudina/glovewort"
}
```

Fallback example:

```json
{
  "route": "chat_fallback",
  "executed": false,
  "reply_text": "...",
  "model": "qwen2.5-coder:3b-instruct"
}
```

---

## 6. Command Parsing Rules

Phase-2A should use simple deterministic parsing, not ML parsing.

### Examples

- `jalankan pwd` -> `pwd`
- `jalankan docker ps` -> `docker ps`
- `baca README.md` -> read file
- `baca README.md lalu ringkas` -> read + summarize

### Parsing policy

- exact prefix match first
- low ambiguity
- reject unclear command shapes

---

## 7. Execution Policy

## 7.1 Shell execution

Implementation target:

- subprocess-based execution
- timeout enforced
- stdout/stderr captured
- no shell if avoidable; if shell is used, enforce strict filtering

## 7.2 File reading

Implementation target:

- read text files only in phase-2A
- path normalization + allowed-root checks

## 7.3 Docker inspection

Implementation target:

- read-only Docker commands only
- no mutable Docker operations in phase-2A

---

## 8. Optional summarization flow

For commands like:

- `baca README.md lalu ringkas`

Flow:

1. router performs actual file read
2. router truncates content if needed
3. router forwards real content to `llm-bridge-api`
4. LLM returns summary
5. router returns grounded summary to Telegram

Important:

- summary is always derived from real content, never invented from prompt alone

---

## 9. Logging Requirements

Each route request should log:

- raw incoming text
- matched route type
- matched command/path
- allow/deny decision
- execution time
- exit code
- output truncation flag

This is required for phase-2 debugging.

---

## 10. Non-goals for phase-2A

Do not implement yet:

- arbitrary natural-language command planning
- autonomous remediation
- destructive shell operations
- file writes
- Docker lifecycle mutation
- tool-call JSON schema negotiation with model

---

## 11. Validation Checklist

Before calling phase-2A complete:

- [ ] `jalankan pwd` returns real cwd
- [ ] `docker ps` returns real container IDs
- [ ] `baca README.md` returns actual file content or grounded summary
- [ ] normal chat still routes to Ollama
- [ ] logs show explicit route decisions
- [ ] hallucinated tool output is no longer possible on deterministic routes

---

## 12. Bottom Line

The router should be treated as a **control-plane component**, not a cosmetic helper.

Its job is to decide:

- **execute deterministically**
- or **chat normally**

That is the only defensible way to make `glovewort` useful as a real executor under Cloud Shell constraints.
