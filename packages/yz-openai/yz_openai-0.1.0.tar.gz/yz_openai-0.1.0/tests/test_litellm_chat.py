"""
测试 LLM Client 基本功能
"""
import pytest
import pytest_asyncio
from yz_openai import YzOpenAI


client = YzOpenAI(provider="litellm")

@pytest_asyncio.fixture
async def litellm_client():
    """创建 LiteLLM 客户端 fixture"""
    client = YzOpenAI(provider="litellm")
    yield client
    await client.close()


@pytest.mark.asyncio
async def test_non_stream_completion(litellm_client):
    """测试非流式补全"""
    # Act
    response = await litellm_client.chat.completion(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？"}
        ]
    )

    # Assert
    assert response is not None
    assert response.message is not None
    assert response.message.role == "assistant"
    assert response.message.content is not None
    assert len(response.message.content) > 0
    assert response.model == "gpt-4o"
    assert response.finish_reason in ["stop", "length", None]
    assert response.usage is not None
    assert response.usage.total_tokens > 0

    # Print for debugging
    print(f"\nRole: {response.message.role}")
    print(f"Content: {response.message.content}")
    print(f"Model: {response.model}")
    print(f"Finish Reason: {response.finish_reason}")
    print(f"Usage: {response.usage}")


@pytest.mark.asyncio
async def test_stream_completion(litellm_client):
    """测试流式补全（使用 AsyncIterator[CompletionResult]）"""
    # Act
    stream = await litellm_client.chat.completion(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "你是谁？"}
        ],
        stream=True,
        stream_options={"include_usage": True}
    )

    # Assert
    content_chunks = []
    last_result = None

    print("\nStream response: ", end="", flush=True)

    async for result in stream:
        assert result is not None
        assert result.message is not None

        if result.message.content:
            content_chunks.append(result.message.content)
            print(result.message.content, end="", flush=True)

        last_result = result

    # 验证流式响应
    assert len(content_chunks) > 0, "应该至少有一个内容块"
    assert last_result is not None

    if last_result.finish_reason:
        print(f"\n\nFinish Reason: {last_result.finish_reason}")
        assert last_result.finish_reason in ["stop", "length"]

    if last_result.usage:
        print(f"Usage: {last_result.usage}")
        assert last_result.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_json_mode_completion(litellm_client):
    """测试 JSON 模式补全"""
    # Act
    result = await litellm_client.chat.completion(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "请抽取用户的姓名与年龄信息，以JSON格式返回"
            },
            {
                "role": "user",
                "content": "大家好，我叫刘五，今年34岁，邮箱是liuwu@example.com，平时喜欢打篮球和旅游",
            },
        ],
        response_format={"type": "json_object"}
    )

    # Assert
    assert result is not None
    assert result.message is not None
    assert result.message.content is not None

    # 验证返回的是 JSON 格式
    import json
    try:
        json_data = json.loads(result.message.content)
        assert isinstance(json_data, dict)
        print(f"\nJSON result: {json_data}")
    except json.JSONDecodeError:
        pytest.fail("返回内容不是有效的 JSON 格式")


@pytest.mark.asyncio
async def test_tool_completion(litellm_client):
    """测试工具调用（Function Calling）"""
    # Arrange
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "当你想查询指定城市的天气时非常有用。",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "城市或县区，比如北京市、杭州市、余杭区等。",
                        }
                    },
                    "required": ["location"],
                },
            },
        },
    ]
    messages = [{"role": "user", "content": "北京天气咋样"}]

    # Act
    result = await litellm_client.chat.completion(
        model="gpt-4o",
        messages=messages,
        tools=tools,
    )

    # Assert
    assert result is not None
    assert result.message is not None

    # 验证工具调用
    if result.message.tool_calls:
        assert len(result.message.tool_calls) > 0
        tool_call = result.message.tool_calls[0]
        assert tool_call.type == "function"
        assert tool_call.function is not None
        print(f"\nTool call: {tool_call}")

    print(f"\nResult: {result}")


@pytest.mark.asyncio
async def test_simple_completion(litellm_client):
    """测试简单补全"""
    # Act
    result = await litellm_client.chat.simple_completion(
        model="gpt-4o",
        prompt="你是谁?"
    )

    # Assert
    assert result is not None
    assert result.message is not None
    assert result.message.content is not None
    assert len(result.message.content) > 0
    assert result.message.role == "assistant"

    print(f"\nSimple completion result: {result.message.content}")
