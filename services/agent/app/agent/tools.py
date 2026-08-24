from typing import Any
from ..services.rag import search_knowledge

TOOL_META = {
    "calculator": {"risk_level": "low", "requires_approval": False},
    "get_system_status": {"risk_level": "low", "requires_approval": False},
    "knowledge_search": {"risk_level": "low", "requires_approval": False},
}


def calculator(expression: str) -> str:
    allowed = set("0123456789+-*/().% ")
    if not expression or any(ch not in allowed for ch in expression):
        return "表达式包含不允许的字符。"
    try:
        # 仅允许受限字符的演示计算器；生产建议换成安全 AST evaluator。
        return str(eval(expression, {"__builtins__": {}}, {}))
    except Exception as exc:
        return f"计算失败：{exc}"


def get_system_status() -> str:
    return "API=healthy; PostgreSQL=healthy; Redis=healthy; Qdrant=healthy; MinIO=healthy"


async def knowledge_search(tenant_id: str, query: str) -> tuple[str, list[dict[str, Any]]]:
    results = await search_knowledge(tenant_id, query)
    if not results:
        return "知识库未找到相关内容。", []
    body = "\n\n".join([f"[{idx + 1}] {item['source']} ({item['score']})\n{item['text']}" for idx, item in enumerate(results)])
    return body, results
