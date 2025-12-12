"""
Volcengine Chat 实现
"""
from volcenginesdkarkruntime import Ark
from typing import AsyncIterator, Union

from yz_openai.base.utils import stream_response_wrapper, parse_non_stream_response
from yz_openai.base.exceptions import LLMAPIError
from yz_openai.base.types import CompletionResult


class VolcengineChat:
    """Volcengine Chat 实现"""

    def __init__(self, base_api: str, api_key: str):
        """
        初始化 Volcengine Chat 客户端

        Args:
            base_api: API 基础地址
            api_key: API 密钥
        """
        self.client = Ark(
            base_url=f"{base_api}/api/v3",
            api_key=api_key,
        )

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

            必需参数:
                model (str): 模型名称，如 "doubao-pro" 等
                messages (List[Dict]): 消息列表，格式为 [{"role": "user", "content": "..."}]

            可选参数:
                temperature (float): 温度参数，控制随机性 (0.0-2.0)
                top_p (float): 核采样参数 (0.0-1.0)
                stream (bool): 是否流式输出（默认False）
                stream_options (Dict): 流式选项，如 {"include_usage": true}
                max_tokens (int): 最大生成token数
                stop (Union[str, List[str]]): 停止词
                presence_penalty (float): 存在惩罚 (-2.0 to 2.0)
                frequency_penalty (float): 频率惩罚 (-2.0 to 2.0)
                response_format (Dict): 响应格式，如 {"type": "json_object"}
                tools (List[Dict]): 工具列表（函数调用）
                tool_choice (str): 工具选择策略

        Returns:
            - 如果 stream=False: 返回 Dict 对象
            - 如果 stream=True: 返回 AsyncIterator[Dict]，异步迭代器

        Raises:
            LLMAPIError: LLM 调用异常

        Examples:
            非流式调用:
            >>> result = await chat.completion(
            ...     model="doubao-pro",
            ...     messages=[
            ...         {"role": "system", "content": "You are a helpful assistant."},
            ...         {"role": "user", "content": "你是谁？"}
            ...     ]
            ... )

            流式调用:
            >>> async for result in chat.completion(
            ...     model="doubao-pro",
            ...     messages=[{"role": "user", "content": "你是谁？"}],
            ...     stream=True
            ... ):
            ...     if result["message"]["content"]:
            ...         print(result["message"]["content"], end="", flush=True)
        """
        try:
            # 调用 Ark 客户端
            response = self.client.chat.completions.create(**kwargs)

            # 判断是否为流式响应
            is_stream = kwargs.get('stream', False)

            if is_stream:
                # 流式响应：返回异步生成器
                return stream_response_wrapper(response)
            else:
                # 非流式响应：解析并返回字典
                return parse_non_stream_response(response)

        except Exception as e:
            raise LLMAPIError(f"Volcengine API error: {str(e)}")

    async def close(self):
        """关闭客户端，释放资源"""
        pass
