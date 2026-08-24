from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from ..services.model_gateway import ModelGateway
from .tools import calculator, get_system_status, knowledge_search


gateway = ModelGateway()


class AgentState(TypedDict, total=False):
    messages: list[dict]
    tenant_id: str
    user_id: str
    tool_events: list[dict]
    citations: list[dict]
    _model_result: dict


async def model_node(state: AgentState) -> AgentState:
    result = await gateway.chat(state["messages"])
    messages = list(state.get("messages", []))
    raw_tool_calls = result.get("assistant_tool_calls")

    if raw_tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": result.get("content", "") or "",
                "tool_calls": raw_tool_calls,
            }
        )
    elif result.get("content"):
        messages.append({"role": "assistant", "content": result["content"]})

    return {
        **state,
        "messages": messages,
        "_model_result": result,
    }


async def tool_node(state: AgentState) -> AgentState:
    result = state["_model_result"]
    events = list(state.get("tool_events", []))
    citations = list(state.get("citations", []))
    messages = list(state.get("messages", []))

    for call in result.get("tool_calls", []):
        name = call["name"]
        args = call.get("arguments", {})
        if name == "calculator":
            value = calculator(str(args.get("expression", "1+1")))
        elif name == "get_system_status":
            value = get_system_status()
        elif name == "knowledge_search":
            value, refs = await knowledge_search(state["tenant_id"], str(args.get("query", "")))
            citations.extend(refs)
        else:
            value = f"Tool {name} is not registered."

        events.append({"name": name, "result": value})
        messages.append(
            {
                "role": "tool",
                "content": value,
                "name": name,
                "tool_call_id": call.get("id"),
            }
        )

    return {
        **state,
        "messages": messages,
        "tool_events": events,
        "citations": citations,
    }


def should_continue(state: AgentState) -> str:
    return "tools" if state.get("_model_result", {}).get("tool_calls") else END


builder = StateGraph(AgentState)
builder.add_node("model", model_node)
builder.add_node("tools", tool_node)
builder.add_edge(START, "model")
builder.add_conditional_edges("model", should_continue, {"tools": "tools", END: END})
builder.add_edge("tools", "model")
graph = builder.compile()
