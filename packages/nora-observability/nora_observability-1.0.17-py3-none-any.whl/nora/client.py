"""
Nora Observability Client
자동으로 AI 라이브러리 호출을 trace하고 API로 전송합니다.
"""

import time
import threading
import inspect
from typing import Optional, Dict, Any, List, Callable, TypeVar
from datetime import datetime
import uuid
from contextvars import ContextVar
from functools import wraps

try:
    import requests
except ImportError:
    requests = None


# Context variables for trace grouping
_current_trace_group: ContextVar[Optional["TraceGroup"]] = ContextVar(
    "_current_trace_group", default=None
)

F = TypeVar("F", bound=Callable[..., Any])


class TraceGroup:
    """
    여러 LLM 호출을 하나의 논리적 그룹으로 묶는 컨텍스트.

    Context manager 또는 데코레이터로 사용 가능합니다.

    사용법 (Context Manager):
        with nora.trace_group(name="multi_agent_pipeline"):
            # 이 블록 안의 모든 LLM 호출이 그룹으로 묶임
            response1 = client.chat.completions.create(...)
            response2 = client.chat.completions.create(...)

    사용법 (데코레이터):
        @nora.trace_group(name="batch_process")
        async def generate():
            async for chunk in agent.streaming():
                yield chunk
    """

    def __init__(self, name: str, metadata: Optional[Dict[str, Any]] = None):
        self.group_id = str(uuid.uuid4())
        self.name = name
        self.metadata = metadata or {}
        self.start_time = None
        self.end_time = None
        self.traces = []
        self._prev_auto_flush = None  # 이전 auto flush 상태 저장
        self._prev_trace_group = None  # 이전 trace_group 저장 (중첩 지원)

    def __enter__(self):
        self.start_time = time.time()
        # 이전 trace_group 저장 (중첩 지원)
        self._prev_trace_group = _current_trace_group.get()
        _current_trace_group.set(self)

        # 자동 플러시 비활성화 (trace_group 내부에서는 모아두기 위해)
        client = get_client()
        if client:
            self._prev_auto_flush = getattr(client, "_auto_flush_enabled", True)
            client._auto_flush_enabled = False

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        # 이전 trace_group 복원 (중첩 지원)
        _current_trace_group.set(self._prev_trace_group)

        # 자동 플러시 재개
        client = get_client()
        flush_after_exit = False
        if client:
            if self._prev_auto_flush is not None:
                flush_after_exit = self._prev_auto_flush
                client._auto_flush_enabled = self._prev_auto_flush

        # 그룹 요약 정보 생성
        if self.traces:
            if client:
                # 각 trace에 그룹 정보 추가
                for trace in self.traces:
                    if trace.get("metadata") is None:
                        trace["metadata"] = {}
                    trace["metadata"]["trace_group"] = {
                        "id": self.group_id,
                        "name": self.name,
                        "metadata": self.metadata,
                    }

        # trace_group 종료 시 적체된 trace를 바로 플러시 (데코레이터 사용 시에도 보장)
        if client and flush_after_exit and client._traces:
            client.flush()

        return False  # 예외를 재발생시킴

    async def __aenter__(self):
        """비동기 context manager 진입."""
        self.start_time = time.time()
        # 이전 trace_group 저장 (중첩 지원)
        self._prev_trace_group = _current_trace_group.get()
        _current_trace_group.set(self)

        # 자동 플러시 비활성화 (trace_group 내부에서는 모아두기 위해)
        client = get_client()
        if client:
            self._prev_auto_flush = getattr(client, "_auto_flush_enabled", True)
            client._auto_flush_enabled = False

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 context manager 종료."""
        self.end_time = time.time()
        # 이전 trace_group 복원 (중첩 지원)
        _current_trace_group.set(self._prev_trace_group)

        # 자동 플러시 재개
        client = get_client()
        flush_after_exit = False
        if client:
            if self._prev_auto_flush is not None:
                flush_after_exit = self._prev_auto_flush
                client._auto_flush_enabled = self._prev_auto_flush

        # 그룹 요약 정보 생성
        if self.traces:
            if client:
                # 각 trace에 그룹 정보 추가
                for trace in self.traces:
                    if trace.get("metadata") is None:
                        trace["metadata"] = {}
                    trace["metadata"]["trace_group"] = {
                        "id": self.group_id,
                        "name": self.name,
                        "metadata": self.metadata,
                    }

        # 비동기 컨텍스트 종료 시에도 적체된 trace를 즉시 플러시
        if client and flush_after_exit and client._traces:
            client.flush()

        return False  # 예외를 재발생시킴

    def __call__(self, func: F) -> F:
        """데코레이터로 사용될 때 호출됩니다."""
        group_name = self.name
        group_metadata = self.metadata

        def _new_group() -> "TraceGroup":
            meta_copy = dict(group_metadata) if isinstance(group_metadata, dict) else group_metadata
            return TraceGroup(name=group_name, metadata=meta_copy)

        # Async generator
        if inspect.isasyncgenfunction(func):

            @wraps(func)
            async def async_gen_wrapper(*args, **kwargs):
                group = _new_group()
                async with group:
                    async for item in func(*args, **kwargs):
                        yield item

            return async_gen_wrapper  # type: ignore

        # Generator
        elif inspect.isgeneratorfunction(func):

            @wraps(func)
            def gen_wrapper(*args, **kwargs):
                group = _new_group()
                with group:
                    yield from func(*args, **kwargs)

            return gen_wrapper  # type: ignore

        # Async function
        elif inspect.iscoroutinefunction(func):

            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                group = _new_group()
                async with group:
                    return await func(*args, **kwargs)

            return async_wrapper  # type: ignore

        # Sync function
        else:

            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                group = _new_group()
                with group:
                    return func(*args, **kwargs)

            return sync_wrapper  # type: ignore


class NoraClient:
    """
    Nora Observability 클라이언트

    Trace 데이터를 수집하고 배치로 API에 전송합니다.
    """

    def __init__(
        self,
        api_key: str,
        api_url: str = "https://api.nora.ai/v1/traces",
        batch_size: int = 10,
        flush_interval: float = 5.0,
        service_url: Optional[str] = None,
        environment: str = "default",
    ):
        """
        Args:
            api_key: Nora API 키
            api_url: Trace 데이터를 전송할 API 엔드포인트 URL
            batch_size: 한 번에 전송할 trace 개수 (기본값: 10)
            flush_interval: 자동 전송 간격(초) (기본값: 5.0)
            service_url: 외부 서비스 URL (선택사항, 나중에 외부 API 호출에 사용)
            environment: 환경 정보 (기본값: "default")
        """
        self.api_key = api_key
        self.api_url = api_url
        self.service_url = service_url
        self.environment = environment
        self.project_id: Optional[str] = None
        self.organization_id: Optional[str] = None
        self.enabled = True
        self._auto_flush_enabled = True  # trace_group에서 제어 가능

        self._traces: List[Dict[str, Any]] = []
        self._lock = threading.Lock()
        self._batch_size = batch_size
        self._flush_interval = flush_interval
        self._last_flush = time.time()

    def trace(
        self,
        provider: str,
        model: str,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        start_time: Optional[float] = None,
        end_time: Optional[float] = None,
        tokens_used: Optional[int] = None,
        error: Optional[str] = None,
        finish_reason: Optional[str] = None,
        response_id: Optional[str] = None,
        system_fingerprint: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        **extra_fields,
    ) -> None:
        """
        Trace 데이터를 수집합니다.

        Args:
            provider: AI 제공자 (openai, anthropic, etc.)
            model: 사용된 모델 이름
            prompt: 입력 프롬프트
            response: 응답 내용
            metadata: 추가 메타데이터
            start_time: 요청 시작 시간 (timestamp)
            end_time: 요청 종료 시간 (timestamp)
            tokens_used: 사용된 토큰 수
            error: 에러 메시지 (있는 경우)
            finish_reason: 완료 이유 (stop, length, tool_calls, etc.)
            response_id: API 응답 ID
            system_fingerprint: 시스템 fingerprint
            tool_calls: Tool/Function calls 정보
            **extra_fields: 추가 필드 (확장성)
        """
        if not self.enabled:
            return

        trace_data = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "response": response,
            "metadata": metadata or {},
            "start_time": start_time,
            "end_time": end_time,
            "duration": (end_time - start_time) if (start_time and end_time) else None,
            "tokens_used": tokens_used,
            "error": error,
            "finish_reason": finish_reason,
            "response_id": response_id,
            "system_fingerprint": system_fingerprint,
            "tool_calls": tool_calls,
            "environment": self.environment,
        }

        # 추가 필드 병합
        trace_data.update(extra_fields)

        # 현재 활성화된 trace group 정보 추가
        current_group = get_current_trace_group()

        if current_group:
            if trace_data["metadata"] is None:
                trace_data["metadata"] = {}
            trace_data["metadata"]["trace_group"] = {
                "id": current_group.group_id,
                "name": current_group.name,
            }
            current_group.traces.append(trace_data)

        with self._lock:
            self._traces.append(trace_data)

            # trace_group 내부에서는 자동 플러시 비활성화
            if not self._auto_flush_enabled:
                return

            # 배치 크기나 시간 간격에 따라 자동 전송
            should_flush = (
                len(self._traces) >= self._batch_size
                or (time.time() - self._last_flush) >= self._flush_interval
            )

            if should_flush:
                self._flush()

    def _flush(self, sync: bool = False) -> None:
        """수집된 trace 데이터를 API로 전송합니다.

        Args:
            sync: True면 동기적으로 전송 (기본값: False, 비동기 전송)
        """
        if not self._traces:
            return

        if not requests:
            # requests가 없으면 경고 출력 (한 번만)
            if not hasattr(self, "_warned_no_requests"):
                print("[Nora] Warning: 'requests' library not found. Install it to send traces.")
                self._warned_no_requests = True
            return

        traces_to_send = self._traces.copy()
        self._traces.clear()
        self._last_flush = time.time()

        if sync:
            # 동기적으로 전송 (테스트용)
            self._send_traces(traces_to_send)
        else:
            # 비동기로 전송 (메인 스레드 블로킹 방지)
            thread = threading.Thread(target=self._send_traces, args=(traces_to_send,), daemon=True)
            thread.start()

    def _send_traces(self, traces: List[Dict[str, Any]]) -> None:
        """실제 API로 trace 데이터를 전송합니다.

        TraceGroup별로 묶어서 전송합니다.
        """
        if not traces:
            return

        # TraceGroup별로 그룹화
        traces_by_group: Dict[str, List[Dict[str, Any]]] = {}

        for trace in traces:
            # trace_group 정보 추출
            trace_group_info = trace.get("metadata", {}).get("trace_group", {})
            trace_name = trace_group_info.get("name", "default")

            if trace_name not in traces_by_group:
                traces_by_group[trace_name] = []
            traces_by_group[trace_name].append(trace)

        # 각 trace_group별로 전송
        for trace_name, group_traces in traces_by_group.items():
            try:
                headers = {
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                }

                payload = {
                    "trace_name": trace_name,
                    "trace_data": group_traces,
                    "environment": self.environment,
                }

                print(
                    f"[Nora] 📤 Sending {len(group_traces)} trace(s) with trace_name='{trace_name}' to {self.api_url}"
                )
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=10)

                if response.status_code in (200, 201):
                    print(
                        f"[Nora] ✅ Successfully sent {len(group_traces)} trace(s) (status: {response.status_code})"
                    )
                else:
                    print(
                        f"[Nora] ⚠️  Warning: Failed to send traces (status: {response.status_code})"
                    )
                    try:
                        print(f"[Nora] Response: {response.text[:200]}")
                    except Exception:
                        pass

            except requests.exceptions.RequestException as e:
                # 네트워크 에러는 조용히 처리 (사용자 코드에 영향 없음)
                print(f"[Nora] ❌ Error sending traces: {str(e)}")
            except Exception as e:
                # 기타 예상치 못한 에러
                print(f"[Nora] ❌ Unexpected error: {str(e)}")

    def flush(self, sync: bool = False) -> None:
        """수동으로 trace 데이터를 즉시 전송합니다.

        Args:
            sync: True면 동기적으로 전송 (기본값: False, 비동기 전송)
        """
        with self._lock:
            self._flush(sync=sync)

    def disable(self) -> None:
        """Trace 기능을 비활성화합니다."""
        self.flush()  # 비활성화 전에 남은 데이터 전송
        self.enabled = False

    def enable(self) -> None:
        """Trace 기능을 활성화합니다."""
        self.enabled = True

    def find_traces_by_group(self, group_name: str) -> List[Dict[str, Any]]:
        """특정 trace group 이름으로 수집된 모든 traces를 검색합니다."""
        matching_traces = []
        with self._lock:
            for trace in self._traces:
                group_info = trace.get("metadata", {}).get("trace_group", {})
                if group_info.get("name") == group_name:
                    matching_traces.append(trace)
        return matching_traces

    def find_traces_by_group_id(self, group_id: str) -> List[Dict[str, Any]]:
        """특정 trace group ID로 수집된 모든 traces를 검색합니다."""
        matching_traces = []
        with self._lock:
            for trace in self._traces:
                group_info = trace.get("metadata", {}).get("trace_group", {})
                if group_info.get("id") == group_id:
                    matching_traces.append(trace)
        return matching_traces

    def get_trace_groups(self) -> List[Dict[str, Any]]:
        """현재 수집된 모든 trace group 정보를 반환합니다."""
        groups_dict = {}
        with self._lock:
            for trace in self._traces:
                group_info = trace.get("metadata", {}).get("trace_group", {})
                if group_info:
                    group_id = group_info.get("id")
                    if group_id and group_id not in groups_dict:
                        groups_dict[group_id] = {
                            "id": group_id,
                            "name": group_info.get("name"),
                            "metadata": group_info.get("metadata", {}),
                            "trace_count": 0,
                            "total_tokens": 0,
                            "total_duration": 0.0,
                            "trace_ids": [],
                        }
                    if group_id:
                        groups_dict[group_id]["trace_count"] += 1
                        tokens = trace.get("tokens_used") or 0
                        groups_dict[group_id]["total_tokens"] += tokens
                        groups_dict[group_id]["trace_ids"].append(trace.get("id"))
                        duration = trace.get("duration") or 0.0
                        groups_dict[group_id]["total_duration"] += duration
        return list(groups_dict.values())


# 전역 클라이언트 인스턴스
_client: Optional[NoraClient] = None


def get_client() -> Optional[NoraClient]:
    """전역 클라이언트 인스턴스를 반환합니다."""
    return _client


def set_client(client: NoraClient) -> None:
    """전역 클라이언트 인스턴스를 설정합니다."""
    global _client
    _client = client


def get_current_trace_group() -> Optional[TraceGroup]:
    """현재 활성화된 trace group을 반환합니다."""
    return _current_trace_group.get()
