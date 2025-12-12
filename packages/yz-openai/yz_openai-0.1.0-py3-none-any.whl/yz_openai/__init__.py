"""
YZ-OpenAI: 统一的大语言模型客户端库
"""
# 统一客户端
from yz_openai.client import YzOpenAI

# Chat 类型定义
from yz_openai.base.types import (
    ToolCall,
    Message,
    Usage,
    CompletionResult,
    # Podcast 类型定义
)

# 异常
from yz_openai.base.exceptions import (
    LLMException,
    LLMAPIError,
    LLMTimeoutError,
    LLMAuthenticationError,
    LLMRateLimitError,
    LLMInvalidRequestError,
    LLMNoProviderError,
    LLMAPIKeyError,
    # Podcast 异常
    PodcastError,
    PodcastConnectionError,
    PodcastRoundError,
)

__version__ = "0.1.0"

__all__ = [
    # 版本
    "__version__",

    # 统一客户端
    "YzOpenAI",

    # Chat 类型
    "ToolCall",
    "Message",
    "Usage",
    "CompletionResult",

    # 异常
    "LLMException",
    "LLMAPIError",
    "LLMTimeoutError",
    "LLMAuthenticationError",
    "LLMRateLimitError",
    "LLMInvalidRequestError",
    "LLMNoProviderError",
    "LLMAPIKeyError",
    "PodcastError",
    "PodcastConnectionError",
    "PodcastRoundError",
]
