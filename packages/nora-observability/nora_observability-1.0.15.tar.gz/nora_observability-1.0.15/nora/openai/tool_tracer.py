"""
Tool 실행 자동 감지 및 trace 생성
"""

import time
import json
from typing import Any, Dict, List, Optional
from ..client import _current_trace_group
from .types import ToolExecutionInfo


def auto_trace_tool_executions(request_params: Dict[str, Any], client: Any) -> None:
    """
    Messages에서 tool role을 감지하여 자동으로 tool execution trace를 생성합니다.
    TraceGroup 내부에서만 작동합니다.

    Args:
        request_params: 요청 파라미터 (messages 포함)
        client: Nora client 인스턴스
    """
    if not _current_trace_group.get():
        return

    messages = request_params.get("messages", [])
    if not messages:
        return

    for i, msg in enumerate(messages):
        if not isinstance(msg, dict) or msg.get("role") != "tool":
            continue

        tool_info = _extract_tool_info_from_messages(messages, i, msg)
        if not tool_info:
            continue

        if _is_tool_already_traced(client, tool_info["call_id"], tool_info["name"]):
            continue

        _create_tool_execution_trace(client, tool_info, msg.get("content", ""))


def _extract_tool_info_from_messages(
    messages: List[Dict], tool_msg_index: int, tool_msg: Dict
) -> Optional[ToolExecutionInfo]:
    """
    Tool message로부터 tool call 정보를 추출합니다.

    Args:
        messages: 메시지 리스트
        tool_msg_index: Tool 메시지의 인덱스
        tool_msg: Tool 메시지

    Returns:
        Tool 정보 dict 또는 None (찾지 못한 경우)
    """
    tool_call_id = tool_msg.get("tool_call_id", "")

    # 이전 메시지에서 assistant의 tool_calls 찾기
    for j in range(tool_msg_index - 1, -1, -1):
        prev_msg = messages[j]
        if not isinstance(prev_msg, dict) or prev_msg.get("role") != "assistant":
            continue

        tool_calls = prev_msg.get("tool_calls", [])
        for tc in tool_calls:
            if isinstance(tc, dict) and tc.get("id") == tool_call_id:
                func_info = tc.get("function", {})
                return ToolExecutionInfo(
                    call_id=tool_call_id,
                    name=func_info.get("name", "unknown"),
                    arguments=func_info.get("arguments", "{}"),
                )

    return None


def _is_tool_already_traced(client: Any, tool_call_id: str, tool_name: str) -> bool:
    """
    Tool이 이미 trace되었는지 확인합니다.

    Args:
        client: Nora client 인스턴스
        tool_call_id: Tool call ID
        tool_name: Tool 이름

    Returns:
        이미 trace되었으면 True
    """
    if not hasattr(client, "_traced_tools"):
        client._traced_tools = set()

    trace_key = f"{tool_call_id}_{tool_name}"
    if trace_key in client._traced_tools:
        return True

    client._traced_tools.add(trace_key)
    return False


def _create_tool_execution_trace(
    client: Any, tool_info: ToolExecutionInfo, tool_result: str
) -> None:
    """
    Tool execution trace를 생성합니다.

    Args:
        client: Nora client 인스턴스
        tool_info: Tool 실행 정보
        tool_result: Tool 실행 결과
    """
    try:
        args_dict = (
            json.loads(tool_info["arguments"])
            if isinstance(tool_info["arguments"], str)
            else tool_info["arguments"]
        )
    except (json.JSONDecodeError, TypeError):
        args_dict = {}

    client.trace(
        provider="tool_execution",
        model=tool_info["name"],
        prompt=f"Tool: {tool_info['name']}\nArguments: {json.dumps(args_dict, ensure_ascii=False)}",
        response=tool_result,
        start_time=time.time() - 0.001,
        end_time=time.time(),
        tokens_used=0,
        metadata={
            "tool_name": tool_info["name"],
            "tool_call_id": tool_info["call_id"],
            "arguments": args_dict,
            "result": tool_result,
            "is_tool_execution": True,
        },
    )
