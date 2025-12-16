"""Gemini API 타입 정의"""

from typing import TypedDict, Optional, List, Any, Dict


class RequestParams(TypedDict, total=False):
    """Gemini API 요청 파라미터"""

    model: str
    contents: List[Dict[str, Any]]
    generation_config: Optional[Dict[str, Any]]
    safety_settings: Optional[List[Dict[str, Any]]]
    system_instruction: Optional[str]
