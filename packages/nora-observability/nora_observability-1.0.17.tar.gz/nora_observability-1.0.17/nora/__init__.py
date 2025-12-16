"""
Nora Observability SDK
AI 라이브러리 호출을 자동으로 trace하는 Observability 서비스

사용법:
    import nora

    nora.init(api_key="YOUR_KEY")

    # 이제 OpenAI, Anthropic 등의 호출이 자동으로 trace됩니다!
"""

import os
import sys
import time
import json
import inspect
from functools import wraps
from pathlib import Path
from typing import Optional, Dict, Any, Callable, List

from .client import NoraClient, get_client, set_client, TraceGroup, _current_trace_group

__version__ = "1.0.17"

# 패치 상태 추적
_patched = False

# 자동 추적할 함수명 리스트
_traced_functions: List[str] = []
_original_trace_func = None


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
    traced_functions: Optional[List[str]] = None,
    service_url: Optional[str] = None,
    environment: str = "default",
) -> None:
    """
    Nora Observability를 초기화하고 자동 trace를 활성화합니다.

    Args:
        api_key: Nora API 키
        api_url: Trace 데이터를 전송할 API 엔드포인트 URL
        auto_patch: 자동으로 AI 라이브러리를 패치할지 여부 (기본값: True)
        traced_functions: 자동으로 trace_group으로 감쌀 함수명 리스트 (기본값: None)
        service_url: 외부 서비스 URL (선택사항, 나중에 외부 API 호출에 사용)
        environment: 환경 정보 (기본값: "default")

    예제:
        >>> import nora
        >>> nora.init(api_key="your-api-key")
        >>> # 이제 OpenAI, Anthropic 등의 호출이 자동으로 trace됩니다!

        >>> # 특정 함수들을 자동으로 trace_group으로 감싸기
        >>> nora.init(
        ...     api_key="your-api-key",
        ...     traced_functions=["functionA", "functionB"]
        ... )
        >>> # functionA, functionB가 호출되면 자동으로 trace_group으로 감싸집니다!

        >>> # service_url과 함께 초기화
        >>> nora.init(
        ...     api_key="your-api-key",
        ...     traced_functions=["functionA", "functionB"],
        ...     service_url="http://localhost:8000"
        ... )
    """
    global _patched, _traced_functions

    # .env 파일 자동 로드 (OpenAI, Anthropic API 키 등)
    _load_env_file()

    # 클라이언트 생성 및 설정
    client = NoraClient(
        api_key=api_key, api_url=api_url, service_url=service_url, environment=environment
    )
    set_client(client)

    # service_url이 있으면 project_id와 organization_id를 받아서 feedback 엔드포인트 호출
    if service_url:
        project_info = _get_project_info(api_key)
        if project_info:
            project_id = project_info.get("project_id")
            organization_id = project_info.get("organization_id")
            # 클라이언트에 저장
            if project_id:
                client.project_id = project_id
            if organization_id:
                client.organization_id = organization_id
            # service_url 등록
            if project_id:
                _register_service_url(service_url, api_key, project_id)

    # 자동 패치 활성화
    if auto_patch and not _patched:
        _apply_patches()
        _patched = True

    # traced_functions 설정
    if traced_functions:
        _traced_functions = traced_functions
        _setup_function_tracing()


def _apply_patches() -> None:
    """사용 가능한 모든 AI 라이브러리를 자동으로 패치합니다."""
    from .patches import apply_all_patches

    apply_all_patches()


def _get_project_info(api_key: str) -> Optional[Dict[str, str]]:
    """API 키를 사용하여 project_id와 organization_id를 가져옵니다."""
    try:
        import requests
    except ImportError:
        print("[Nora] Warning: 'requests' library not found. Cannot get project info.")
        return None

    check_url = "https://noraobservabilitybackend-staging.up.railway.app/v1/projects/check/api-key"

    try:
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

        response = requests.get(check_url, headers=headers, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                project_id = data.get("project_id")
                organization_id = data.get("organization_id")

                if project_id:
                    print(f"[Nora] ✅ Project ID retrieved: {project_id}")
                    if organization_id:
                        print(f"[Nora] ✅ Organization ID retrieved: {organization_id}")
                    return {
                        "project_id": project_id,
                        "organization_id": organization_id,
                    }
                else:
                    print("[Nora] ⚠️  Warning: project_id not found in response")
                    return None
            except (ValueError, KeyError) as e:
                print(f"[Nora] ⚠️  Warning: Failed to parse project info from response: {str(e)}")
                return None
        else:
            print(f"[Nora] ⚠️  Warning: Failed to get project info (status: {response.status_code})")
            try:
                print(f"[Nora] Response: {response.text[:200]}")
            except Exception:
                pass
            return None
    except requests.exceptions.RequestException as e:
        # 네트워크 에러는 조용히 처리 (사용자 코드에 영향 없음)
        print(f"[Nora] ⚠️  Warning: Could not get project info: {str(e)}")
        return None
    except Exception as e:
        # 기타 예상치 못한 에러
        print(f"[Nora] ⚠️  Warning: Unexpected error getting project info: {str(e)}")
        return None


def _register_service_url(service_url: str, api_key: str, project_id: str) -> None:
    """service_url을 feedback 엔드포인트에 등록합니다."""
    try:
        import requests
    except ImportError:
        print("[Nora] Warning: 'requests' library not found. Cannot register service_url.")
        return

    feedback_url = "https://noraobservabilitybackend-staging.up.railway.app/v1/feedback/endpoint"

    try:
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

        # service_url에서 경로 부분만 추출 (name으로 사용)
        from urllib.parse import urlparse

        parsed_url = urlparse(service_url)
        # 경로 부분만 사용 (예: /v1/feedback/endpoint)
        name = parsed_url.path if parsed_url.path else "/"
        # 경로가 없으면 기본값 사용
        if name == "/" or not name:
            name = "default_service"

        # API 스키마에 따르면 필드들이 루트 레벨에 있어야 함
        payload = {
            "project_id": project_id,
            "name": name,
            "endpoint": service_url,
        }

        print(f"[Nora] 📤 Registering service URL with payload: {payload}")
        response = requests.post(feedback_url, json=payload, headers=headers, timeout=10)

        if response.status_code in (200, 201):
            print(f"[Nora] ✅ Service URL registered: {service_url}")
        else:
            print(
                f"[Nora] ⚠️  Warning: Failed to register service URL (status: {response.status_code})"
            )
            try:
                print(f"[Nora] Full Response: {response.text}")
                print(f"[Nora] Response Headers: {dict(response.headers)}")
            except Exception:
                pass
    except requests.exceptions.RequestException as e:
        # 네트워크 에러는 조용히 처리 (사용자 코드에 영향 없음)
        print(f"[Nora] ⚠️  Warning: Could not register service URL: {str(e)}")
    except Exception as e:
        # 기타 예상치 못한 에러
        print(f"[Nora] ⚠️  Warning: Unexpected error registering service URL: {str(e)}")


def _setup_function_tracing() -> None:
    """로드된 모든 모듈에서 traced_functions에 있는 함수를 찾아서 자동으로 trace_group 데코레이터를 적용합니다."""
    import sys as sys_module
    import importlib

    for func_name in _traced_functions:
        # 모든 로드된 모듈 검색
        for module_name, module in list(sys_module.modules.items()):
            try:
                # 모듈이 None이거나 접근할 수 없는 경우 스킵
                if module is None:
                    continue

                # 모듈에서 함수 찾기
                if hasattr(module, func_name):
                    func = getattr(module, func_name)
                    # 함수인지 확인 (클래스가 아닌)
                    if callable(func) and not inspect.isclass(func):
                        # 이미 래핑되었는지 확인
                        if not hasattr(func, "_nora_traced"):
                            # 함수를 자동으로 trace_group으로 감싸기
                            wrapped_func = _wrap_function_with_trace_group(func, func_name)
                            if wrapped_func:
                                setattr(module, func_name, wrapped_func)
            except (AttributeError, TypeError, ImportError):
                # 에러가 발생해도 계속 진행 (모듈 접근 권한 등)
                continue
            except Exception:
                # 기타 예외도 무시하고 계속 진행
                continue


def _wrap_function_with_trace_group(func: Callable, func_name: str) -> Optional[Callable]:
    """함수를 trace_group으로 자동 감싸는 래퍼를 생성합니다."""
    # 이미 래핑되었는지 확인
    if hasattr(func, "_nora_traced"):
        return None

    # 함수 타입 확인
    is_async = inspect.iscoroutinefunction(func)
    is_async_gen = inspect.isasyncgenfunction(func)
    is_gen = inspect.isgeneratorfunction(func)

    if is_async_gen:

        @wraps(func)
        async def async_gen_wrapper(*args, **kwargs):
            group = TraceGroup(name=func_name)
            async with group:
                async for item in func(*args, **kwargs):
                    yield item

        async_gen_wrapper._nora_traced = True
        return async_gen_wrapper

    elif is_async:

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            group = TraceGroup(name=func_name)
            async with group:
                return await func(*args, **kwargs)

        async_wrapper._nora_traced = True
        return async_wrapper

    elif is_gen:

        @wraps(func)
        def gen_wrapper(*args, **kwargs):
            group = TraceGroup(name=func_name)
            with group:
                yield from func(*args, **kwargs)

        gen_wrapper._nora_traced = True
        return gen_wrapper

    else:

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            group = TraceGroup(name=func_name)
            with group:
                return func(*args, **kwargs)

        sync_wrapper._nora_traced = True
        return sync_wrapper


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
                    client.trace(
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
