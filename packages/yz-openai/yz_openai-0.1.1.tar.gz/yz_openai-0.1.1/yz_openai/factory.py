"""
LLM 客户端工厂
"""
from typing import Dict, Optional
import os
import importlib

from yz_openai.base.exceptions import LLMNoProviderError, LLMAPIKeyError

# Provider 注册表
_PROVIDER_REGISTRY: Dict[str, Dict] = {
    "litellm": {
        "module": "yz_openai.providers.litellm.chat",
        "class": "LiteLLMChat",
        "base_api": "https://litellm.prod.qima-inc.com",
        "env_key": "LITELLM_API_KEY"
    },
    "volcengine": {
        "module": "yz_openai.providers.volcengine.chat",
        "class": "VolcengineChat",
        "base_api": "https://ark.cn-beijing.volces.com",
        "env_key": "VOLCENGINE_API_KEY"
    }
}


def get_client(provider: str, api_key: Optional[str] = None):
    """
    获取 Provider 客户端（内部使用）

    Args:
        provider: Provider 名称（litellm, volcengine）
        api_key: API 密钥（可选，优先从环境变量读取）
        base_api: 自定义 API 地址（可选）

    Returns:
        Provider Chat 客户端实例

    Raises:
        LLMNoProviderError: Provider 不存在
        LLMAPIKeyError: API 密钥未提供
    """
    # 1. 检查 provider 是否存在
    if provider not in _PROVIDER_REGISTRY:
        supported = ", ".join(_PROVIDER_REGISTRY.keys())
        raise LLMNoProviderError(
            f"Unsupported provider: '{provider}'. "
            f"Supported providers: {supported}"
        )

    provider_cfg = _PROVIDER_REGISTRY[provider]

    # 2. 处理 api_key：入参优先，其次 env
    if api_key is None:
        env_key = provider_cfg.get("env_key")
        api_key = os.getenv(env_key)

    if not api_key:
        raise LLMAPIKeyError(
            f"请提供 api_key 或设置环境变量 {provider_cfg.get('env_key')}")

    # 3. 处理 base_api：入参优先，其次使用默认值
    final_base_api = provider_cfg.get("base_api")

    # 4. 动态导入并实例化客户端
    module = importlib.import_module(provider_cfg["module"])
    client_class = getattr(module, provider_cfg["class"])

    return client_class(base_api=final_base_api, api_key=api_key)


# Podcast Provider 注册表
_PODCAST_PROVIDER_REGISTRY: Dict[str, Dict] = {
    "volcengine": {
        "module": "yz_openai.providers.volcengine.podcast",
        "class": "VolcenginePodcast",
        "endpoint": "wss://openspeech.bytedance.com/api/v3/sami/podcasttts",
        "env_keys": {
            "app_id": "VOLCENGINE_APP_ID",
            "access_key": "VOLCENGINE_ACCESS_KEY"
        },
        "resource_id": "volc.service_type.10050"
    }
}


def get_podcast_client(
    provider: str,
    app_id: Optional[str] = None,
    access_key: Optional[str] = None
):
    """
    获取 Podcast TTS 客户端

    Args:
        provider: Provider 名称（目前仅支持 volcengine）
        app_id: 应用 ID（可选，优先从环境变量读取）
        access_key: Access Key（可选）

    Returns:
        Podcast 客户端实例

    Raises:
        LLMNoProviderError: Provider 不存在或不支持 Podcast
        LLMAPIKeyError: 必需的认证信息未提供

    Example:
        >>> # 从环境变量读取配置
        >>> client = get_podcast_client("volcengine")
        >>>
        >>> # 显式传递配置
        >>> client = get_podcast_client(
        ...     "volcengine",
        ...     app_id="xxx",
        ...     access_key="xxx"
        ... )
    """
    # 1. 检查 provider 是否支持 Podcast
    if provider not in _PODCAST_PROVIDER_REGISTRY:
        supported = ", ".join(_PODCAST_PROVIDER_REGISTRY.keys())
        raise LLMNoProviderError(
            f"Provider '{provider}' 不支持 Podcast 功能。"
            f"支持 Podcast 的 Provider: {supported}"
        )

    provider_cfg = _PODCAST_PROVIDER_REGISTRY[provider]

    # 2. 处理认证信息：入参优先，其次环境变量
    env_keys = provider_cfg.get("env_keys", {})

    if app_id is None:
        app_id = os.getenv(env_keys.get("app_id"))
    if access_key is None:
        access_key = os.getenv(env_keys.get("access_key"))

    # 验证必需参数
    if not all([app_id, access_key]):
        missing = []
        if not app_id:
            missing.append(f"app_id (环境变量: {env_keys.get('app_id')})")
        if not access_key:
            missing.append(f"access_key (环境变量: {env_keys.get('access_key')})")

        raise LLMAPIKeyError(
            f"缺少必需的 Podcast 认证信息: {', '.join(missing)}"
        )

    # 3. 动态导入并实例化客户端
    module = importlib.import_module(provider_cfg["module"])
    client_class = getattr(module, provider_cfg["class"])

    return client_class(
        app_id=app_id,
        access_key=access_key
    )
