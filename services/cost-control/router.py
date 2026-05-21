"""
智慧路由器：自動判斷任務複雜度，呼叫對應模型
整合 LiteLLM Proxy，讓 Hermes / OpenClaw 自動省錢

使用方式：
    from router import smart_call
    response = smart_call("幫我分類這封 Email", task_hint="classify")
"""

import os
import time
import json
from openai import OpenAI

# LiteLLM Proxy endpoint（本地啟動後）
PROXY_BASE = os.getenv("LITELLM_PROXY_URL", "http://localhost:4000")

client = OpenAI(
    base_url=PROXY_BASE,
    api_key=os.getenv("LITELLM_API_KEY", "anything")  # proxy 不需要真實 key
)

# ── 任務類型對應模型 ──────────────────────────────────────────

TASK_MODEL_MAP = {
    # 雜事 → 快速便宜模型
    "classify":    "fast",          # 分類
    "format":      "fast",          # 格式化
    "summarize":   "fast",          # 摘要
    "extract":     "fast",          # 資訊擷取
    "confirm":     "fast",          # 確認/回應
    "translate":   "fast",          # 翻譯

    # 日常工作 → 標準模型
    "draft":       "standard",      # 草稿撰寫
    "analyze":     "standard",      # 分析
    "plan":        "standard",      # 規劃
    "review":      "standard",      # 審查
    "research":    "standard",      # 研究

    # 複雜任務 → 強力模型
    "reason":      "powerful",      # 深度推理
    "strategy":    "powerful",      # 策略規劃
    "architect":   "powerful",      # 系統設計
    "debug":       "powerful",      # 複雜除錯

    # 隱私 / 本地 → Ollama
    "private":     "local-general", # 隱私敏感
    "code":        "local-coder",   # 程式碼（可選用本地）
}

# ── 關鍵字自動偵測（不需要手動指定 task_hint）────────────────

KEYWORD_RULES = [
    (["分類", "classify", "哪一類", "是否", "判斷是不是"], "classify"),
    (["摘要", "summary", "summarize", "重點", "總結"], "summarize"),
    (["翻譯", "translate", "英文", "中文轉"], "translate"),
    (["幫我寫", "草稿", "draft", "回覆這封", "回信"], "draft"),
    (["分析", "analyze", "深入了解", "為什麼", "原因"], "analyze"),
    (["架構", "設計", "architect", "系統", "如何規劃"], "architect"),
    (["程式", "code", "function", "class", "bug", "錯誤"], "code"),
    (["密碼", "token", "secret", "私人", "機密", "客戶資料"], "private"),
]


def detect_task_type(prompt: str) -> str:
    """根據關鍵字自動偵測任務類型"""
    prompt_lower = prompt.lower()
    for keywords, task_type in KEYWORD_RULES:
        if any(kw in prompt_lower for kw in keywords):
            return task_type
    return "analyze"  # 預設標準模型


def smart_call(
    prompt: str,
    task_hint: str = None,
    system: str = None,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    verbose: bool = False,
) -> str:
    """
    智慧呼叫：自動選擇最合適（最省錢）的模型

    Args:
        prompt: 用戶的 prompt
        task_hint: 任務類型提示（可選，不填自動偵測）
        system: system prompt
        temperature: 溫度
        max_tokens: 最大 token 數
        verbose: 是否印出路由決策

    Returns:
        模型回覆的文字
    """
    # 決定任務類型
    task_type = task_hint or detect_task_type(prompt)
    model = TASK_MODEL_MAP.get(task_type, "standard")

    if verbose:
        print(f"🔀 路由決策：task={task_type} → model={model}")

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    start = time.time()
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        elapsed = time.time() - start
        result = response.choices[0].message.content

        if verbose:
            usage = response.usage
            print(f"✅ 完成：{elapsed:.1f}s | tokens: {usage.total_tokens}")

        return result

    except Exception as e:
        print(f"❌ 路由失敗（{model}）：{e}，嘗試 fallback...")
        # Fallback 到標準模型
        response = client.chat.completions.create(
            model="standard",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content


def batch_classify(items: list[str], label_options: list[str]) -> list[str]:
    """
    批次分類（用最便宜模型，效率最高）

    Args:
        items: 要分類的項目列表
        label_options: 可選的標籤列表

    Returns:
        對應的標籤列表
    """
    prompt = f"""
請將以下每個項目分類為：{', '.join(label_options)}
只輸出 JSON 陣列，格式：["標籤1", "標籤2", ...]

項目：
{json.dumps(items, ensure_ascii=False)}
"""
    result = smart_call(prompt, task_hint="classify")
    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return ["未知"] * len(items)


# ── 使用範例 ─────────────────────────────────────────────────

if __name__ == "__main__":
    # 測試不同任務的路由
    tests = [
        ("分類這封 Email：你好，請問你們有優惠嗎？", None),
        ("幫我寫一封拒絕合作的禮貌回覆", "draft"),
        ("分析我們公司 Q1 業績下滑的可能原因", "analyze"),
        ("客戶的合約內容：[機密資料...]", "private"),
        ("設計一個支援百萬用戶的 API 架構", "architect"),
    ]

    for prompt, hint in tests:
        print(f"\n📝 任務：{prompt[:40]}...")
        result = smart_call(prompt, task_hint=hint, verbose=True)
        print(f"💬 回覆：{result[:100]}...")
