"""
LLM 异常定义
"""


class LLMException(Exception):
    """LLM 基础异常"""
    pass

class LLMAPIKeyError(LLMException):
    """LLM API key 错误"""
    pass

class LLMAPIError(LLMException):
    """LLM API 错误"""
    pass


class LLMTimeoutError(LLMException):
    """LLM 超时错误"""
    pass


class LLMAuthenticationError(LLMException):
    """LLM 认证错误"""
    pass


class LLMRateLimitError(LLMException):
    """LLM 速率限制错误"""
    pass


class LLMInvalidRequestError(LLMException):
    """LLM 无效请求错误"""
    pass

class LLMNoProviderError(LLMException):
    """LLM 无效provider错误"""
    pass

class LLMConfigError(LLMException):
    """LLM配置错误"""
    pass


# ==================== Podcast TTS 相关异常 ====================

class PodcastError(LLMException):
    """Podcast TTS 基础异常"""
    pass


class PodcastConnectionError(PodcastError):
    """Podcast 连接异常"""
    pass


class PodcastRoundError(PodcastError):
    """Podcast 轮次处理异常"""
    pass