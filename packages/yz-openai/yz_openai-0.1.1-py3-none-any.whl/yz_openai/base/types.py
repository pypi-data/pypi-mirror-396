"""
LLM 类型定义
"""
from dataclasses import dataclass
from typing import List, Optional, Dict, Any


@dataclass
class ToolCall:
    """工具调用"""
    id: str
    type: str
    function: Dict[str, Any]


@dataclass
class Message:
    """消息"""
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None


@dataclass
class Usage:
    """Token 使用统计"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class CompletionResult:
    """补全结果"""
    message: Message
    model: str
    finish_reason: Optional[str] = None
    usage: Optional[Usage] = None
    raw_response: Optional[Dict[str, Any]] = None


# ==================== Podcast TTS 相关类型 ====================

@dataclass
class PodcastTextItem:
    """播客文本项"""
    text: str
    speaker: str

@dataclass
class PodcastResult:
    """播客完整响应"""
    audio_data: bytes
    audio_url: Optional[str]
    texts: List[PodcastTextItem]
    total_rounds: int
    usage: Optional[Usage] = None
