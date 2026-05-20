# Phase-2 Deterministic Command Router Architecture

## 1. Goal

Phase-2 changes `glovewort` from a **text assistant with simulated execution** into a **deterministic command executor** for a small, explicit command set.

The design goal is not general autonomy.
The design goal is:

- predictable execution
- low hallucination risk
- compatibility with Cloud Shell limits
- explicit separation between:
  - **LLM reasoning/text generation**
  - **actual command execution**

---

## 2. Problem Statement

Phase-1 proved:

- Telegram ingress works
- OpenClaw gateway works
- bridge to Ollama works
- Ollama can answer text prompts

Phase-1 also proved:

- OpenClaw is **not actually invoking tools** in this setup
- the model is instead **hallucinating execution results**
- local model size and current bridge contract are insufficient for reliable tool-use semantics

Therefore phase-2 must remove tool execution from implicit model behavior and replace it with explicit routing.

---

## 3. Core Design Principle

**The model must not be trusted to decide whether a tool was executed.**

Instead:

1. incoming Telegram message is classified
2. if it matches a deterministic command rule, execute directly
3. otherwise send to LLM as a text request
4. if execution occurs, the response sent back to the user is based on **real tool output**, not model imagination

This is the key architectural change.

---

## 4. High-Level Topology

```text
Telegram User
   -> OpenClaw gateway
   -> deterministic router layer
      -> command path (exec/read/etc)
      -> or chat path (llm-bridge-api -> Ollama)
   -> Telegram response
```

### Internal breakdown

```text
Telegram
  -> openclaw-gateway
     -> router service / router module
        -> deterministic command handlers
           -> exec/read/other safe tools
        -> fallback chat handler
           -> llm-bridge-api
              -> ollama-brain
```

---

## 5. Architecture Decision

## 5.1 Router-first, model-second

The router must run **before** LLM inference for commands that match explicit command patterns.

That means:

- `jalankan pwd` should not go to the LLM first
- `baca README.md` should not go to the LLM first
- `docker ps` should not go to the LLM first

Instead:

- the router parses the message
- identifies a supported deterministic command
- executes it directly
- optionally asks LLM only to summarize the real output

---

## 5.2 Bounded command surface

Phase-2 should support only a small explicit command set.

Initial safe command families:

### A. shell execution

Examples:

- `jalankan pwd`
- `jalankan ls`
- `jalankan whoami`
- `jalankan docker ps`

Constraint:

- only through explicit command prefix such as `jalankan ...`
- must enforce allowlist or safety filter

### B. file read

Examples:

- `baca README.md`
- `baca openclaw/config/openclaw.config.yaml`

Constraint:

- read-only path validation
- workspace/root restrictions

### C. file summarize

Examples:

- `baca README.md lalu ringkas`

Flow:

- router performs real read
- optional LLM summarization over real content

### D. docker inspection

Examples:

- `docker ps`
- `docker compose ps`

Constraint:

- inspect-only in phase-2A
- do not allow stop/rm/restart yet

---

## 5.3 No free-form tool execution in phase-2A

Phase-2A should not try to support arbitrary natural-language tool use.

Bad target for phase-2A:

- “please investigate the whole system and fix everything automatically”

Good target for phase-2A:

- “jalankan pwd”
- “baca README.md”
- “docker ps”
- “baca file X lalu ringkas”

This keeps the router deterministic and testable.

---

## 6. Routing Modes

Each incoming message should be assigned one of these modes.

### 6.1 `command_exec`

Message explicitly requests shell execution.

Trigger examples:

- starts with `jalankan `
- starts with `run `

Output source:

- real shell output

### 6.2 `file_read`

Message requests file contents.

Trigger examples:

- starts with `baca `
- starts with `read `

Output source:

- real file content or summarized real content

### 6.3 `docker_inspect`

Message requests Docker inspection.

Trigger examples:

- starts with `docker ps`
- starts with `docker compose ps`
- starts with `cek container`

Output source:

- real Docker output

### 6.4 `chat_fallback`

Message does not match any deterministic route.

Output source:

- Ollama via bridge

---

## 7. Trust Model

## 7.1 Command path

Trusted source of truth:

- actual tool output

LLM role:

- optional summarizer only

## 7.2 Chat path

Trusted source of truth:

- none; this is standard LLM response path

LLM role:

- direct answer generation

---

## 8. Safety Boundaries

Phase-2 must introduce explicit safety boundaries because deterministic routing enables real execution.

### 8.1 Allowlist for `exec`

Allowed in phase-2A:

- `pwd`
- `ls`
- `whoami`
- `cat <safe-path>`
- `docker ps`
- `docker compose ps`
- `docker images`
- `df -h`

Blocked in phase-2A:

- `rm`
- `mv`
- `shutdown`
- `reboot`
- `kill`
- `docker rm`
- `docker stop`
- `docker system prune`
- package installation
- network-changing commands

### 8.2 Read path restrictions

Allowed roots:

- project workspace
- explicit repo roots
- selected config paths

Blocked:

- arbitrary secrets outside approved roots
- `/etc/shadow`
- private key locations
- hidden auth stores unless explicitly approved later

### 8.3 Output truncation

Long command outputs must be truncated or summarized.

Why:

- Telegram message limits
- readability
- cost control

---

## 9. Phase-2A Execution Flow

## 9.1 `jalankan pwd`

```text
Telegram message
  -> router detects command_exec
  -> validates allowlist
  -> executes `pwd`
  -> captures stdout/stderr/exit code
  -> formats response
  -> sends real result to Telegram
```

## 9.2 `baca README.md lalu ringkas`

```text
Telegram message
  -> router detects file_read + summarize
  -> validates path
  -> reads README.md
  -> optionally sends real content to LLM for summary
  -> replies with summary grounded in actual file content
```

## 9.3 normal chat question

```text
Telegram message
  -> router no command match
  -> forward to llm-bridge-api
  -> Ollama response
  -> Telegram reply
```

---

## 10. Integration Strategy

There are two implementation approaches.

## 10.1 In-process router inside OpenClaw-adjacent layer

Pros:

- fewer moving parts
- simpler deployment

Cons:

- tighter coupling with OpenClaw container
- harder to debug if mixed with gateway runtime

## 10.2 Sidecar router service (recommended)

Pros:

- clear separation of responsibilities
- simpler logs
- deterministic routing logic isolated from LLM bridge
- easier to evolve safely

Cons:

- one more service/container

Recommendation:

- **use a sidecar router service** for phase-2

---

## 11. Recommended Phase-2 Topology

```text
Telegram
  -> openclaw-gateway
  -> deterministic-router
      -> exec/read/docker handlers
      -> or llm-bridge-api
           -> ollama-brain
```

### Service roles

- `openclaw-gateway`: ingress and reply transport
- `deterministic-router`: command classification and real execution
- `llm-bridge-api`: chat fallback adapter
- `ollama-brain`: inference backend

---

## 12. Message Handling Policy

The router should evaluate incoming messages in this order:

1. explicit deterministic command
2. deterministic read/summarize command
3. deterministic docker inspection command
4. fallback to chat

This ordering matters.

Why:

- otherwise the model may answer text before the command layer gets a chance to execute

---

## 13. Phase-2A Supported Syntax

Initial Indonesian-first syntax:

### Execution

- `jalankan <command>`

### File read

- `baca <path>`
- `baca <path> lalu ringkas`

### Docker inspect

- `docker ps`
- `docker compose ps`
- `cek container`

### Optional English aliases

- `run <command>`
- `read <path>`

---

## 14. Response Policy

### Command execution response

Must include:

- executed command
- exit code
- stdout/stderr summary

Example:

```text
Perintah: pwd
Exit code: 0
Hasil:
/home/warungbudina/glovewort
```

### File read response

Must clearly distinguish between:

- raw excerpt
- summary of actual content

### Chat fallback response

Can remain normal assistant style.

---

## 15. Observability

Router logs must explicitly record:

- incoming message
- chosen route
- matched pattern
- executed command/path
- exit code
- fallback reason if routed to chat

Without this, debugging phase-2 will regress into guessing again.

---

## 16. Phase-2A Success Criteria

Phase-2A is successful only if:

- `jalankan pwd` returns the real working directory
- `docker ps` returns real container IDs
- `baca README.md lalu ringkas` summarizes actual file content
- non-command questions still route to Ollama
- logs clearly show command-vs-chat routing decisions
- no command result is fabricated by the model

---

## 17. Phase-2B and later

After phase-2A is stable, future expansion may add:

- larger command allowlist
- write operations with confirmation
- structured argument parsing
- safer docker administrative actions
- task templates
- optional model-assisted summarization of long outputs

But these are not phase-2A requirements.

---

## 18. Bottom Line

Phase-2 should not try to make a small model “act more agentic.”

Instead it should:

- route explicit commands deterministically
- execute tools directly
- use the LLM only where it adds value
- remove hallucinated execution from the control path

That is the most realistic design for Cloud Shell constraints and the current `glovewort` architecture.
