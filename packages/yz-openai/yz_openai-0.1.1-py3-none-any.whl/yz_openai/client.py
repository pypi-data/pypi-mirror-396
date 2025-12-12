"""
YZ OpenAI 统一客户端
"""
from typing import Optional

from yz_openai.factory import get_client, get_podcast_client


class YzOpenAI:
    """YZ OpenAI 统一客户端"""

    def __init__(
        self,
        provider: str,
        api_key: Optional[str] = None,
        app_id: Optional[str] = None,
        access_key: Optional[str] = None
    ):
        """
        初始化 YZ OpenAI 客户端

        Args:
            provider: Provider 名称（litellm, volcengine）
            api_key: API 密钥（可选，优先从环境变量读取）
            app_id: Podcast 应用 ID（可选，仅 volcengine 支持）
            access_key: Podcast Access Key（可选，仅 volcengine 支持）

        Raises:
            LLMNoProviderError: Provider 不存在
            LLMAPIKeyError: API 密钥未提供

        Examples:
            >>> # 仅使用 Chat 能力
            >>> client = YzOpenAI(provider="volcengine", api_key="xxx")
            >>> result = await client.chat.completion(model="doubao-pro", messages=[...])
            >>>
            >>> # 同时使用 Chat 和 Podcast 能力
            >>> client = YzOpenAI(
            ...     provider="volcengine",
            ...     api_key="xxx",
            ...     app_id="xxx",
            ...     access_key="xxx"
            ... )
            >>> chat_result = await client.chat.completion(...)
            >>> podcast_result = await client.podcast.create(...)
        """
        self._provider = provider
        self._api_key = api_key

        # Chat 客户端（延迟初始化）
        self._client = None

        # Podcast 客户端（延迟初始化）
        self._podcast_client = None
        self._podcast_config = {
            "app_id": app_id,
            "access_key": access_key
        }

    @property
    def chat(self):
        """
        获取 Chat 功能

        Returns:
            Chat 客户端实例,提供 completion() 和 simple_completion() 方法

        Examples:
            非流式调用:
            >>> result = await client.chat.completion(
            ...     model="doubao-pro",
            ...     messages=[{"role": "user", "content": "你好"}]
            ... )

            流式调用:
            >>> async for chunk in client.chat.completion(
            ...     model="doubao-pro",
            ...     messages=[{"role": "user", "content": "你好"}],
            ...     stream=True
            ... ):
            ...     print(chunk["message"]["content"], end="")
        """
        # 延迟初始化（只在首次访问时创建）
        if self._client is None:
            self._client = get_client(self._provider, self._api_key)
        return self._client

    @property
    def podcast(self):
        """
        获取 Podcast TTS 功能

        Returns:
            Podcast 客户端实例，提供 create() 方法

        Raises:
            LLMNoProviderError: Provider 不支持 Podcast 功能
            LLMAPIKeyError: Podcast 认证信息未提供

        Examples:
            >>> # 非流式生成播客
            >>> result = await client.podcast.create({
            ...     "input_url": "https://example.com/doc.pdf",
            ...     "speakers": ["zh_male_dayixiansheng_v2_saturn_bigtts",
            ...                  "zh_female_mizaitongxue_v2_saturn_bigtts"]
            ... })
            >>> print(f"音频 URL: {result['audio_url']}")
            >>> print(f"文本: {result['texts']}")
        """
        # 延迟初始化（只在首次访问时创建）
        if self._podcast_client is None:
            self._podcast_client = get_podcast_client(
                provider=self._provider,
                **self._podcast_config
            )
        return self._podcast_client

    async def close(self):
        """关闭客户端，释放资源"""
        # 关闭 Chat 客户端
        if hasattr(self._client, 'close'):
            await self._client.close()

        # 关闭 Podcast 客户端
        if self._podcast_client and hasattr(self._podcast_client, 'close'):
            await self._podcast_client.close()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
