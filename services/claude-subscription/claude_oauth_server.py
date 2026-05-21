"""
Claude Subscription OAuth Server
把 claude CLI（走訂閱 OAuth）包成 OpenAI 相容的本地 API
讓 Hermes / LiteLLM 能直接路由進來，零 API 費用

啟動：python3 claude_oauth_server.py
端點：http://localhost:3456/v1/chat/completions
"""

import json
import subprocess
import shutil
import time
import uuid
import asyncio
from typing import AsyncGenerator

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn

# ── 設定 ─────────────────────────────────────────────────────

CLAUDE_BIN = shutil.which("claude") or "/Users/gask/.local/bin/claude"
DEFAULT_MODEL = "sonnet"   # sonnet / opus / haiku
PORT = 3456

# ── FastAPI 應用 ──────────────────────────────────────────────

app = FastAPI(title="Claude Subscription OAuth Server", version="1.0")

# ── 模型名稱轉換 ──────────────────────────────────────────────

MODEL_ALIASES = {
    # LiteLLM / OpenAI 常用名稱 → claude CLI 接受的別名
    "claude-oauth":           "sonnet",
    "claude-oauth-sonnet":    "sonnet",
    "claude-oauth-opus":      "opus",
    "claude-oauth-haiku":     "haiku",
    "claude-sonnet-4-5":      "sonnet",
    "claude-opus-4":          "opus",
    "claude-haiku-3-5":       "haiku",
    "sonnet":                 "sonnet",
    "opus":                   "opus",
    "haiku":                  "haiku",
}

def resolve_model(model_name: str) -> str:
    return MODEL_ALIASES.get(model_name, DEFAULT_MODEL)

# ── 訊息轉換：OpenAI 格式 → claude CLI prompt ────────────────

def messages_to_prompt(messages: list[dict]) -> tuple[str, str | None]:
    """
    把 OpenAI messages 陣列轉成：
    - system_prompt（str 或 None）
    - user_prompt（合併所有非 system 訊息）
    """
    system_parts = []
    conversation_parts = []

    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if isinstance(content, list):
            # 處理多模態內容，只取 text
            content = " ".join(
                c.get("text", "") for c in content
                if isinstance(c, dict) and c.get("type") == "text"
            )

        if role == "system":
            system_parts.append(content)
        elif role == "user":
            conversation_parts.append(f"User: {content}")
        elif role == "assistant":
            conversation_parts.append(f"Assistant: {content}")

    system_prompt = "\n\n".join(system_parts) if system_parts else None

    # 若有多輪對話，把歷史加在 system prompt 裡，最後一則 user 訊息作為主 prompt
    user_messages = [p for p in conversation_parts if p.startswith("User:")]

    if len(conversation_parts) > 1:
        # 多輪對話：把歷史放進 system，最後一則 user 作為 prompt
        history = "\n".join(conversation_parts[:-1])
        if system_prompt:
            system_prompt = f"{system_prompt}\n\n---\n對話歷史：\n{history}"
        else:
            system_prompt = f"以下是對話歷史，請根據此繼續回覆：\n{history}"

        # 最後一則 user 訊息
        last_user = conversation_parts[-1].replace("User: ", "", 1)
        return last_user, system_prompt

    # 單輪對話
    user_prompt = user_messages[-1].replace("User: ", "", 1) if user_messages else ""
    return user_prompt, system_prompt

# ── 呼叫 claude CLI ───────────────────────────────────────────

def call_claude(
    prompt: str,
    model: str = "sonnet",
    system_prompt: str | None = None,
    max_tokens: int = 4096,
) -> dict:
    """呼叫 claude -p，返回 JSON 結果"""

    cmd = [
        CLAUDE_BIN,
        "--print",
        "--output-format", "json",
        "--model", model,
        prompt,
    ]

    if system_prompt:
        cmd.extend(["--system-prompt", system_prompt])

    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
        )
        elapsed = time.time() - start

        if result.returncode != 0:
            raise RuntimeError(f"claude CLI 錯誤：{result.stderr[:500]}")

        data = json.loads(result.stdout)

        if data.get("is_error"):
            raise RuntimeError(f"claude 回傳錯誤：{data}")

        return {
            "text": data.get("result", ""),
            "elapsed": elapsed,
            "usage": data.get("usage", {}),
            "cost_usd": data.get("total_cost_usd", 0),
            "model": model,
        }

    except subprocess.TimeoutExpired:
        raise RuntimeError("claude CLI 超時（120 秒）")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 解析失敗：{result.stdout[:200]}")

# ── OpenAI 相容 API ───────────────────────────────────────────

@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    body = await request.json()

    messages   = body.get("messages", [])
    model_name = body.get("model", "claude-oauth")
    stream     = body.get("stream", False)
    max_tokens = body.get("max_tokens", 4096)

    if not messages:
        raise HTTPException(status_code=400, detail="messages 不能為空")

    model = resolve_model(model_name)
    prompt, system_prompt = messages_to_prompt(messages)

    if not prompt.strip():
        raise HTTPException(status_code=400, detail="無法從 messages 提取 user prompt")

    try:
        result = call_claude(
            prompt=prompt,
            model=model,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 返回 OpenAI 格式
    response_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
    created = int(time.time())

    usage = result.get("usage", {})

    response = {
        "id": response_id,
        "object": "chat.completion",
        "created": created,
        "model": f"claude-oauth-{model}",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": result["text"],
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {
            "prompt_tokens":     usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens":      usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
        },
        # 額外資訊（非標準，但有用）
        "x_subscription_cost_usd": result["cost_usd"],
        "x_elapsed_seconds":       round(result["elapsed"], 2),
        "x_note": "走 Claude 訂閱 OAuth，不消耗 API 額度",
    }

    return JSONResponse(response)


@app.get("/v1/models")
async def list_models():
    """列出可用模型"""
    return {
        "object": "list",
        "data": [
            {"id": "claude-oauth-sonnet", "object": "model", "owned_by": "claude-subscription"},
            {"id": "claude-oauth-opus",   "object": "model", "owned_by": "claude-subscription"},
            {"id": "claude-oauth-haiku",  "object": "model", "owned_by": "claude-subscription"},
        ]
    }


@app.get("/health")
async def health():
    """健康檢查 + 確認 claude CLI 可用"""
    claude_ok = bool(shutil.which("claude"))
    return {
        "status": "ok" if claude_ok else "degraded",
        "claude_bin": CLAUDE_BIN,
        "claude_available": claude_ok,
        "port": PORT,
        "note": "使用 Claude 訂閱 OAuth，不消耗 API 額度",
    }


# ── 啟動 ─────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════╗
║    Claude Subscription OAuth Server          ║
║    http://localhost:{PORT}                      ║
╠══════════════════════════════════════════════╣
║  claude CLI : {CLAUDE_BIN}
║  端點       : POST /v1/chat/completions      ║
║  模型       : claude-oauth-sonnet/opus/haiku ║
║  費用       : 走訂閱 OAuth，不消耗 API 額度  ║
╚══════════════════════════════════════════════╝
""")
    uvicorn.run(app, host="127.0.0.1", port=PORT, log_level="warning")
