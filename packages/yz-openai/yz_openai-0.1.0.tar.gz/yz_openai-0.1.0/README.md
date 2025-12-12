# YZ-OpenAI

有赞 LLM 统一调用库 - 提供简单、统一的接口调用多个 LLM 提供商和 TTS 服务。

## 特性

- 🚀 **统一接口**：支持多个 LLM 提供商（LiteLLM, Volcengine）
- 🎙️ **Podcast TTS**：支持火山引擎 Podcast TTS 播客生成
- 🔄 **流式支持**：完整的流式响应支持
- 🛡️ **类型安全**：完整的类型注解支持
- 🔌 **异步优先**：基于 asyncio 的异步设计
- 📦 **轻量级**：最小依赖，易于集成

## 安装

### 使用 pip 安装

```bash
pip install yz-openai
```

### 使用 requirements.txt 安装

```bash
pip install -r requirements.txt
```

### 开发版本安装

```bash
# 仅核心功能
pip install -e .

# 包含开发工具
pip install -e ".[dev]"
```

### 依赖说明

**核心依赖**（自动安装）：
- `httpx>=0.24.0` - HTTP 客户端
- `litellm>=1.0.0` - LLM 统一调用库
- `openai>=1.0.0` - OpenAI SDK
- `websockets>=12.0` - WebSocket 支持（Podcast TTS）
- `volcengine-python-sdk[ark]>=1.0.0` - 火山引擎 SDK

**开发依赖**（可选）：
```bash
pip install yz-openai[dev]
```

## 使用场景

### 1. Chat 对话 - 非流式调用

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    # 使用 LiteLLM 提供商
    async with YzOpenAI(provider="litellm", api_key="your-api-key") as client:
        result = await client.chat.completion(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "你好，介绍一下你自己"}
            ]
        )
        print(result.message.content)

asyncio.run(main())
```

### 2. Chat 对话 - 流式调用

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    # 使用火山引擎提供商
    async with YzOpenAI(provider="volcengine", api_key="your-api-key") as client:
        async for chunk in client.chat.completion(
            model="doubao-pro-32k",
            messages=[
                {"role": "user", "content": "写一篇关于人工智能的文章"}
            ],
            stream=True
        ):
            print(chunk["message"]["content"], end="", flush=True)

asyncio.run(main())
```

### 3. Podcast TTS - 根据文档 URL 生成播客 (action=0)

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    client = YzOpenAI(
        provider="volcengine",
        api_key="your-api-key",
        app_id="your-app-id",
        access_key="your-access-key"
    )

    result = await client.podcast.create({
        "action": 0,
        "input_url": "https://example.com/document.pdf",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ],
        "audio_format": "mp3",
        "sample_rate": 24000,
        "use_head_music": True,
        "use_tail_music": True
    })

    # 保存音频
    with open("podcast.mp3", "wb") as f:
        f.write(result.audio_data)

    print(f"音频 URL: {result.audio_url}")
    print(f"总轮次: {result.total_rounds}")
    print(f"Token 使用: {result.usage}")

    # 查看对话文本
    for item in result.texts:
        print(f"{item.speaker}: {item.text}")

    await client.close()

asyncio.run(main())
```

### 4. Podcast TTS - 根据文本生成播客 (action=0)

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    client = YzOpenAI(
        provider="volcengine",
        app_id="your-app-id",
        access_key="your-access-key"
    )

    result = await client.podcast.create({
        "action": 0,
        "input_text": "人工智能（AI）正在改变我们的生活方式...",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ],
        "only_nlp_text": False,
        "return_audio_url": True
    })

    with open("podcast.mp3", "wb") as f:
        f.write(result.audio_data)

    await client.close()

asyncio.run(main())
```

### 5. Podcast TTS - 根据对话文本直接生成 (action=3)

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    client = YzOpenAI(
        provider="volcengine",
        app_id="your-app-id",
        access_key="your-access-key"
    )

    result = await client.podcast.create({
        "action": 3,
        "nlp_texts": [
            {
                "speaker": "zh_male_dayixiansheng_v2_saturn_bigtts",
                "text": "大家好，今天我们来聊聊人工智能的发展。"
            },
            {
                "speaker": "zh_female_mizaitongxue_v2_saturn_bigtts",
                "text": "是的，人工智能确实是当今最热门的话题之一。"
            },
            {
                "speaker": "zh_male_dayixiansheng_v2_saturn_bigtts",
                "text": "从 GPT 到图像生成，AI 技术正在快速发展。"
            },
            {
                "speaker": "zh_female_mizaitongxue_v2_saturn_bigtts",
                "text": "没错，让我们深入探讨一下这个话题。"
            }
        ],
        "audio_format": "mp3",
        "return_audio_url": True
    })

    with open("podcast.mp3", "wb") as f:
        f.write(result.audio_data)

    print(f"生成完成，共 {result.total_rounds} 轮对话")

    await client.close()

asyncio.run(main())
```

### 6. Podcast TTS - 根据提示文本扩展生成 (action=4)

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    client = YzOpenAI(
        provider="volcengine",
        app_id="your-app-id",
        access_key="your-access-key"
    )

    result = await client.podcast.create({
        "action": 4,
        "prompt_text": "讨论人工智能在医疗领域的应用和未来发展",
        "speakers": [
            "zh_male_dayixiansheng_v2_saturn_bigtts",
            "zh_female_mizaitongxue_v2_saturn_bigtts"
        ],
        "audio_format": "mp3",
        "sample_rate": 24000,
        "speech_rate": 0,
        "use_head_music": True,
        "use_tail_music": True
    })

    with open("podcast.mp3", "wb") as f:
        f.write(result.audio_data)

    # 查看生成的对话内容
    for item in result.texts:
        print(f"{item.speaker}: {item.text}")

    await client.close()

asyncio.run(main())
```

### 7. Chat + Podcast 混合使用

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    # 同时使用 Chat 和 Podcast 功能
    async with YzOpenAI(
        provider="volcengine",
        api_key="your-api-key",
        app_id="your-app-id",
        access_key="your-access-key"
    ) as client:
        # 使用 Chat 生成内容
        chat_result = await client.chat.completion(
            model="doubao-pro-32k",
            messages=[
                {"role": "user", "content": "生成一段关于人工智能的对话脚本"}
            ]
        )

        print("Chat 生成的内容：")
        print(chat_result.message.content)

        # 使用 Podcast 将内容转为语音
        podcast_result = await client.podcast.create({
            "action": 4,
            "prompt_text": chat_result.message.content,
            "speakers": [
                "zh_male_dayixiansheng_v2_saturn_bigtts",
                "zh_female_mizaitongxue_v2_saturn_bigtts"
            ]
        })

        with open("ai_podcast.mp3", "wb") as f:
            f.write(podcast_result.audio_data)

        print(f"播客生成完成: {podcast_result.total_rounds} 轮对话")

asyncio.run(main())
```

## API 参数说明

### Chat 参数

```python
client.chat.completion(
    model="doubao-pro-32k",           # 模型名称
    messages=[...],                    # 消息列表
    stream=False,                      # 是否流式输出
    temperature=0.7,                   # 温度参数（0-1）
    top_p=1.0,                        # Top-p 参数
    max_tokens=None,                  # 最大 token 数
)
```

### Podcast 参数

#### action=0（根据文档/文本生成）
```python
{
    "action": 0,                      # 必需
    "input_url": "https://...",       # 文档 URL（与 input_text 二选一）
    "input_text": "...",              # 输入文本（与 input_url 二选一）
    "speakers": ["speaker1", "speaker2"],  # 说话人列表（至少2个）
    "audio_format": "mp3",            # 音频格式，默认 "mp3"
    "sample_rate": 24000,             # 采样率，默认 24000
    "speech_rate": 0,                 # 语速，默认 0
    "use_head_music": False,          # 是否添加片头音乐
    "use_tail_music": False,          # 是否添加片尾音乐
    "return_audio_url": True,         # 是否返回音频 URL
    "only_nlp_text": False,           # 是否仅返回 NLP 文本
    "max_retries": 5                  # 最大重试次数
}
```

#### action=3（根据对话文本直接生成）
```python
{
    "action": 3,                      # 必需
    "nlp_texts": [                    # 对话文本列表（必需）
        {"speaker": "speaker1", "text": "..."},
        {"speaker": "speaker2", "text": "..."}
    ],
    "audio_format": "mp3",
    "sample_rate": 24000,
    "return_audio_url": True,
    "max_retries": 5
}
```

#### action=4（根据提示文本扩展生成）
```python
{
    "action": 4,                      # 必需
    "prompt_text": "...",             # 提示文本（必需）
    "speakers": ["speaker1", "speaker2"],  # 说话人列表（至少2个）
    "audio_format": "mp3",
    "sample_rate": 24000,
    "speech_rate": 0,
    "use_head_music": False,
    "use_tail_music": False,
    "max_retries": 5
}
```

## 异常处理

```python
from yz_openai import (
    LLMException,
    LLMAPIError,
    LLMTimeoutError,
    LLMAuthenticationError,
    LLMRateLimitError,
    PodcastError,
    PodcastConnectionError,
    PodcastRoundError
)

try:
    result = await client.chat.completion(...)
except LLMAuthenticationError as e:
    print(f"认证失败: {e}")
except LLMRateLimitError as e:
    print(f"速率限制: {e}")
except LLMTimeoutError as e:
    print(f"请求超时: {e}")
except LLMAPIError as e:
    print(f"API 错误: {e}")

try:
    result = await client.podcast.create(...)
except PodcastConnectionError as e:
    print(f"连接失败: {e}")
except PodcastRoundError as e:
    print(f"轮次处理失败: {e}")
except PodcastError as e:
    print(f"Podcast 错误: {e}")
```

## 环境变量配置

可以通过环境变量配置 API 密钥，避免硬编码：

```bash
# LiteLLM
export LITELLM_API_KEY="your-api-key"

# Volcengine Chat
export VOLCENGINE_API_KEY="your-api-key"

# Volcengine Podcast
export VOLCENGINE_APP_ID="your-app-id"
export VOLCENGINE_ACCESS_KEY="your-access-key"
```

使用环境变量：

```python
import asyncio
from yz_openai import YzOpenAI

async def main():
    # API 密钥会自动从环境变量读取
    async with YzOpenAI(provider="volcengine") as client:
        result = await client.chat.completion(
            model="doubao-pro-32k",
            messages=[{"role": "user", "content": "你好"}]
        )
        print(result.message.content)

asyncio.run(main())
```

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black yz_openai tests
```

### 类型检查

```bash
mypy yz_openai
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
