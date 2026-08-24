from typing import Any
from openai import AsyncOpenAI
from ..core.config import settings

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {"name": "calculator", "description": "执行基本四则运算。", "parameters": {"type": "object", "properties": {"expression": {"type": "string"}}, "required": ["expression"]}},
    },
    {
        "type": "function",
        "function": {"name": "get_system_status", "description": "检查企业平台核心组件状态。", "parameters": {"type": "object", "properties": {}}},
    },
    {
        "type": "function",
        "function": {"name": "knowledge_search", "description": "搜索企业知识库。", "parameters": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    },
]

class ModelGateway:
    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url) if settings.llm_api_key else None

    async def chat(self, messages: list[dict[str, Any]], model: str | None = None) -> dict[str, Any]:
        if settings.llm_provider == "mock" or self.client is None:
            text = messages[-1].get("content", "")
            if any(keyword in text for keyword in ["计算", "算一下", "calculate"]):
                expression = text.replace("计算", "").strip() or "1+1"
                return {"content": "", "tool_calls": [{"name": "calculator", "arguments": {"expression": expression}}]}
            if any(keyword in text for keyword in ["状态", "健康", "status"]):
                return {"content": "", "tool_calls": [{"name": "get_system_status", "arguments": {}}]}
            if any(keyword in text for keyword in ["知识库", "报销", "制度", "政策", "文档"]):
                return {"content": "", "tool_calls": [{"name": "knowledge_search", "arguments": {"query": text}}]}
            return {"content": f"这是 Mock Agent 的演示回答：我已经收到任务「{text}」。将 LLM_PROVIDER 切换为 openai 即可接入真实模型。", "tool_calls": []}

        response = await self.client.chat.completions.create(
            model=model or settings.llm_model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )
        message = response.choices[0].message
        tool_calls = []
        raw_tool_calls = []
        for call in message.tool_calls or []:
            import json
            item = {"name": call.function.name, "arguments": json.loads(call.function.arguments or "{}"), "id": call.id}
            tool_calls.append(item)
            raw_tool_calls.append(call.model_dump())
        return {"content": message.content or "", "tool_calls": tool_calls, "assistant_tool_calls": raw_tool_calls}
