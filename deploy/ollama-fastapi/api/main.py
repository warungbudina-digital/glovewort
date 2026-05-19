from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any

import httpx
from fastapi import FastAPI, Header, HTTPException, Response
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama-brain:11434")
DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "qwen2.5-coder:1.5b")
TIMEOUT_SECONDS = float(os.getenv("OLLAMA_TIMEOUT", "180"))
BRIDGE_API_KEY = os.getenv("BRIDGE_API_KEY", "")

app = FastAPI(title="glovewort-ollama-bridge", version="1.0.0")


class ChatMessage(BaseModel):
    role: str
    content: str | list[Any] | None = ""


class ChatRequest(BaseModel):
    model: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False


def _check_auth(authorization: str | None) -> None:
    if not BRIDGE_API_KEY:
        return

    expected = f"Bearer {BRIDGE_API_KEY}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/healthz")
async def healthz() -> JSONResponse:
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
        response.raise_for_status()
        return JSONResponse({"ok": True, "ollama": "up"})
    except Exception as exc:  # pragma: no cover
        return JSONResponse({"ok": False, "ollama": str(exc)}, status_code=503)


def _to_ollama_messages(messages: list[ChatMessage]) -> list[dict[str, str]]:
    converted: list[dict[str, str]] = []
    for msg in messages:
        if isinstance(msg.content, str):
            content = msg.content
        elif msg.content is None:
            content = ""
        else:
            content = json.dumps(msg.content)
        converted.append({"role": msg.role, "content": content})
    return converted


def _openai_chunk(content: str, model: str, request_id: str) -> dict[str, Any]:
    return {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [{"index": 0, "delta": {"content": content}, "finish_reason": None}],
    }


@app.post("/v1/chat/completions", response_model=None)
async def chat_completions(
    payload: ChatRequest,
    authorization: str | None = Header(default=None),
) -> Response:
    _check_auth(authorization)

    model = payload.model or DEFAULT_MODEL
    request_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    ollama_body = {
        "model": model,
        "messages": _to_ollama_messages(payload.messages),
        "stream": payload.stream,
        "options": {
            **({"temperature": payload.temperature} if payload.temperature is not None else {}),
            **({"num_predict": payload.max_tokens} if payload.max_tokens is not None else {}),
        },
    }

    if not payload.stream:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.post(f"{OLLAMA_URL}/api/chat", json=ollama_body)
        if response.status_code >= 400:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        data = response.json()
        text = (data.get("message") or {}).get("content", "")
        return JSONResponse(
            {
                "id": request_id,
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": text},
                        "finish_reason": "stop",
                    }
                ],
            }
        )

    async def stream_events() -> Any:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            async with client.stream("POST", f"{OLLAMA_URL}/api/chat", json=ollama_body) as resp:
                if resp.status_code >= 400:
                    detail = await resp.aread()
                    raise HTTPException(status_code=resp.status_code, detail=detail.decode("utf-8", errors="ignore"))

                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    payload_line = json.loads(line)
                    text = (payload_line.get("message") or {}).get("content", "")
                    done = bool(payload_line.get("done"))

                    if text:
                        yield f"data: {json.dumps(_openai_chunk(text, model, request_id))}\n\n"
                    if done:
                        final_chunk = {
                            "id": request_id,
                            "object": "chat.completion.chunk",
                            "created": int(time.time()),
                            "model": model,
                            "choices": [{"index": 0, "delta": {}, "finish_reason": "stop"}],
                        }
                        yield f"data: {json.dumps(final_chunk)}\n\n"
                        yield "data: [DONE]\n\n"
                        return

    return StreamingResponse(stream_events(), media_type="text/event-stream")
