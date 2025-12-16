"""
Nora Observability SDK
AI 라이브러리 호출을 자동으로 trace하는 Observability 서비스

사용법:
    import nora

    nora.init(api_key="YOUR_KEY")

    # 이제 OpenAI, Anthropic 등의 호출이 자동으로 trace됩니다!
"""

import os
import time
import json
from functools import wraps
from pathlib import Path
from typing import Optional, Dict, Any, Callable

from .client import NoraClient, get_client, set_client, TraceGroup, _current_trace_group

__version__ = "1.0.15"

# 패치 상태 추적
_patched = False


def _load_env_file() -> None:
    """프로젝트 루트의 .env 파일을 자동으로 로드합니다."""
    # 이미 로드된 환경변수가 있으면 스킵
    if os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY"):
        return

    # 현재 작업 디렉토리부터 상위로 올라가며 .env 파일 찾기
    current = Path.cwd()
    max_depth = 5  # 최대 5단계까지 상위로 탐색

    for _ in range(max_depth):
        env_file = current / ".env"
        if env_file.exists():
            try:
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            # 이미 설정된 환경변수는 덮어쓰지 않음
                            if key and not os.getenv(key):
                                os.environ[key] = value
                return
            except Exception:
                pass

        parent = current.parent
        if parent == current:  # 루트에 도달
            break
        current = parent


def init(
    api_key: str,
    api_url: str = "https://noraobservabilitybackend-staging.up.railway.app/v1/traces/",
    auto_patch: bool = True,
) -> None:
    """
    Nora Observability를 초기화하고 자동 trace를 활성화합니다.

    Args:
        api_key: Nora API 키
        api_url: Trace 데이터를 전송할 API 엔드포인트 URL
        auto_patch: 자동으로 AI 라이브러리를 패치할지 여부 (기본값: True)

    예제:
        >>> import nora
        >>> nora.init(api_key="your-api-key")
        >>> # 이제 OpenAI, Anthropic 등의 호출이 자동으로 trace됩니다!
    """
    global _patched

    # .env 파일 자동 로드 (OpenAI, Anthropic API 키 등)
    _load_env_file()

    # 클라이언트 생성 및 설정
    client = NoraClient(api_key=api_key, api_url=api_url)
    set_client(client)

    # 자동 패치 활성화
    if auto_patch and not _patched:
        _apply_patches()
        _patched = True


def _apply_patches() -> None:
    """사용 가능한 모든 AI 라이브러리를 자동으로 패치합니다."""
    from .patches import apply_all_patches

    apply_all_patches()


def flush(sync: bool = False) -> None:
    """수집된 trace 데이터를 즉시 전송합니다.

    Args:
        sync: True면 동기적으로 전송 (기본값: False, 비동기 전송)
    """
    client = get_client()
    if client:
        client.flush(sync=sync)


def disable() -> None:
    """Trace 기능을 비활성화합니다."""
    client = get_client()
    if client:
        client.disable()


def enable() -> None:
    """Trace 기능을 활성화합니다."""
    client = get_client()
    if client:
        client.enable()


def trace_group(
    name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    여러 LLM 호출을 하나의 논리적 그룹으로 묶습니다.

    Context manager 또는 데코레이터로 사용 가능합니다.

    Args:
        name: 그룹 이름 (데코레이터 사용 시 기본값: 함수 이름)
        metadata: 그룹 메타데이터

    Returns:
        TraceGroup 객체 (context manager이자 데코레이터)

    예제 (Context Manager):
        >>> with nora.trace_group("multi_agent_workflow"):
        ...     response1 = client.chat.completions.create(...)
        ...     response2 = client.chat.completions.create(...)

    예제 (데코레이터):
        >>> @nora.trace_group(name="batch_process")
        ... async def generate():
        ...     async for chunk in agent.streaming():
        ...         yield chunk

        >>> # 또는 이름 생략 (함수 이름 사용)
        >>> @nora.trace_group()
        ... def process_data():
        ...     return client.chat.completions.create(...)

        >>> # 또는 인자 없이 직접 적용
        >>> @nora.trace_group
        ... def simple_function():
        ...     return client.chat.completions.create(...)
    """
    # @nora.trace_group (인자 없이 직접 적용) - name이 callable 함수
    if name is not None and callable(name):
        func = name
        group_name = func.__name__
        return TraceGroup(name=group_name, metadata=metadata)(func)

    # @nora.trace_group() : 함수 이름을 그룹 이름으로 자동 사용
    if name is None:

        def decorator(func: Callable) -> Callable:
            group = TraceGroup(name=func.__name__, metadata=metadata)
            return group(func)

        return decorator

    # name이 문자열인 경우: context manager 또는 데코레이터 이름 명시
    return TraceGroup(name=name, metadata=metadata)


def find_traces_by_group(group_name: str):
    """
    특정 trace group 이름으로 수집된 모든 traces를 검색합니다.

    Args:
        group_name: 검색할 trace group 이름

    Returns:
        매칭되는 trace들의 리스트

    예제:
        >>> traces = nora.find_traces_by_group("multi_agent_pipeline")
        >>> for trace in traces:
        ...     print(f"Model: {trace['model']}, Tokens: {trace['tokens_used']}")
    """
    client = get_client()
    if client:
        return client.find_traces_by_group(group_name)
    return []


def find_traces_by_group_id(group_id: str):
    """
    특정 trace group ID로 수집된 모든 traces를 검색합니다.

    Args:
        group_id: 검색할 trace group ID

    Returns:
        매칭되는 trace들의 리스트
    """
    client = get_client()
    if client:
        return client.find_traces_by_group_id(group_id)
    return []


def get_trace_groups():
    """
    현재 수집된 모든 trace group 정보를 반환합니다.

    Returns:
        Unique한 trace group 정보 리스트 (id, name, trace_count, total_tokens, total_duration)

    예제:
        >>> groups = nora.get_trace_groups()
        >>> for group in groups:
        ...     print(f"Group: {group['name']}, Traces: {group['trace_count']}")
    """
    client = get_client()
    if client:
        return client.get_trace_groups()
    return []


def tool(
    func: Optional[Callable] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
) -> Callable:
    """
    함수를 tool로 표시하고 자동으로 trace를 생성합니다.

    TraceGroup 안에서 호출되면 그룹에 포함되고,
    독립적으로 호출되면 독자적인 trace를 생성합니다.

    Args:
        func: 래핑할 함수
        name: Tool 이름 (기본값: 함수 이름)
        description: Tool 설명 (기본값: 함수 docstring)

    Returns:
        래핑된 함수

    예제:
        >>> @nora.tool
        ... def get_weather(location: str, unit: str = "celsius"):
        ...     '''날씨 정보를 가져옵니다'''
        ...     return f"The weather in {location} is 22°{unit}"
        ...
        >>> # TraceGroup 안에서 사용
        >>> with nora.trace_group("weather_query"):
        ...     result = get_weather("New York", "celsius")
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            client = get_client()
            if not client:
                # Client가 없으면 그냥 실행
                return f(*args, **kwargs)

            # TraceGroup 체크
            current_group = _current_trace_group.get()

            # TraceGroup이 없으면 trace 생성 안 함 (조건 2)
            if not current_group:
                return f(*args, **kwargs)

            # Tool 정보
            tool_name = name or f.__name__
            tool_description = description or (f.__doc__ or "").strip()

            # Arguments 준비
            import inspect

            sig = inspect.signature(f)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            arguments = dict(bound_args.arguments)

            # Tool 실행
            start_time = time.time()
            try:
                result = f(*args, **kwargs)
                end_time = time.time()
                error = None
            except Exception as e:
                end_time = time.time()
                error = str(e)
                result = None
                raise
            finally:
                # Trace 생성 (TraceGroup 안에서만)
                if current_group:
                    client.add_trace(
                        provider="tool_execution",
                        model=tool_name,
                        prompt=f"Tool: {tool_name}\nArguments: {json.dumps(arguments, ensure_ascii=False)}",
                        response=str(result) if result is not None else "",
                        start_time=start_time,
                        end_time=end_time,
                        tokens_used=0,  # Tool은 토큰 사용 안 함
                        error=error,
                        metadata={
                            "tool_name": tool_name,
                            "tool_description": tool_description,
                            "arguments": arguments,
                            "result": result,
                            "is_tool_execution": True,
                        },
                    )

            return result

        return wrapper

    # @nora.tool 또는 @nora.tool() 둘 다 지원
    if func is None:
        return decorator
    else:
        return decorator(func)


# 주요 API를 직접 export
__all__ = [
    "init",
    "flush",
    "disable",
    "enable",
    "trace_group",
    "find_traces_by_group",
    "find_traces_by_group_id",
    "get_trace_groups",
    "tool",
    "NoraClient",
    "get_client",
    "__version__",
]
