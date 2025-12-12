"""
LiteLLM Chat 实现
"""
import os
import litellm
from typing import AsyncIterator, Union

from yz_openai.base.utils import stream_response_wrapper, parse_non_stream_response
from yz_openai.base.exceptions import LLMAPIError
from yz_openai.base.types import CompletionResult


class LiteLLMChat:
    """LiteLLM Chat 实现"""

    def __init__(self, base_api: str, api_key: str):
        """
        初始化 LiteLLM Chat 客户端

        Args:
            base_api: API 基础地址
            api_key: API 密钥
        """
        self.api_base = base_api
        os.environ["OPENAI_API_KEY"] = api_key

    async def simple_completion(self, prompt: str, **kwargs) -> Union[CompletionResult, AsyncIterator[CompletionResult]]:
        """
        简单补全

        Args:
            prompt: 提示词
            **kwargs: 其他参数

        Returns:
            CompletionResult 或 AsyncIterator[CompletionResult]
        """
        return await self.completion(**kwargs, messages=[{"role": "user", "content": prompt}])

    async def completion(self, **kwargs) -> Union[CompletionResult, AsyncIterator[CompletionResult]]:
        """
        文本补全（支持流式和非流式）

        Args:
            **kwargs: 所有参数直接透传

        Returns:
            CompletionResult 或 AsyncIterator[CompletionResult]
        """
        try:
            # 调用 LiteLLM
            params = {**kwargs, "api_base": self.api_base}
            response = litellm.completion(**params)

            # 判断是否为流式响应
            is_stream = kwargs.get('stream', False)

            if is_stream:
                # 流式响应：返回异步生成器
                return stream_response_wrapper(response)
            else:
                # 非流式响应：解析并返回字典
                return parse_non_stream_response(response)

        except Exception as e:
            raise LLMAPIError(f"LiteLLM API error: {str(e)}")

    async def close(self):
        """关闭客户端，释放资源"""
        pass
