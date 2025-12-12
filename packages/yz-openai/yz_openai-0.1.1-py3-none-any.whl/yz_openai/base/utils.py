"""
LLM 工具函数
"""
from typing import Optional, List, AsyncIterator
from yz_openai.base.exceptions import LLMAPIError
from yz_openai.base.types import ToolCall, Message, Usage, CompletionResult


def extract_tool_calls(source, is_delta: bool = False) -> Optional[List[ToolCall]]:
    """
    提取工具调用

    Args:
        source: 消息对象或 delta 对象
        is_delta: 是否为流式 delta（需要更宽松的字段检查）

    Returns:
        Optional[List[ToolCall]]: 工具调用列表
    """
    if not hasattr(source, 'tool_calls') or not source.tool_calls:
        return None

    tool_calls = []
    for tc in source.tool_calls:
        if is_delta:
            # 流式 delta 的字段可能不完整
            tool_calls.append(ToolCall(
                id=tc.id if hasattr(tc, 'id') else "",
                type=tc.type if hasattr(tc, 'type') else "function",
                function=tc.function if isinstance(tc.function, dict) else {
                    "name": tc.function.name if hasattr(tc.function, 'name') else "",
                    "arguments": tc.function.arguments if hasattr(tc.function, 'arguments') else ""
                }
            ))
        else:
            # 非流式响应的字段完整
            tool_calls.append(ToolCall(
                id=tc.id,
                type=tc.type,
                function=tc.function if isinstance(tc.function, dict) else {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            ))
    return tool_calls


def extract_usage(response) -> Optional[Usage]:
    """
    提取 token 使用统计

    Args:
        response: 响应对象

    Returns:
        Optional[Usage]: 使用统计
    """
    if not hasattr(response, 'usage') or not response.usage:
        return None

    return Usage(
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
        total_tokens=response.usage.total_tokens
    )


def build_completion_result(
    message: Message,
    model: str,
    finish_reason: Optional[str],
    usage: Optional[Usage],
    raw_response: Optional[dict]
) -> CompletionResult:
    """
    构造 CompletionResult

    Args:
        message: 消息对象
        model: 模型名称
        finish_reason: 结束原因
        usage: token 使用统计
        raw_response: 原始响应

    Returns:
        CompletionResult: 补全结果
    """
    return CompletionResult(
        message=message,
        model=model,
        finish_reason=finish_reason,
        usage=usage,
        raw_response=raw_response
    )


async def stream_response_wrapper(stream) -> AsyncIterator[CompletionResult]:
    """
    包装流式响应为 AsyncIterator[CompletionResult]

    Args:
        stream: 返回的流式对象

    Yields:
        CompletionResult: 封装后的流式数据块
    """
    try:
        for chunk in stream:
            if hasattr(chunk, 'choices') and chunk.choices:
                choice = chunk.choices[0]
                delta = choice.delta

                # 提取工具调用增量
                tool_calls = extract_tool_calls(delta, is_delta=True)

                # 构造增量消息
                message = Message(
                    role=delta.role if hasattr(delta, 'role') else "assistant",
                    content=delta.content if hasattr(delta, 'content') else None,
                    tool_calls=tool_calls
                )

                # 提取 usage（通常只在最后一个 chunk 存在）
                usage = extract_usage(chunk)

                # 获取 finish_reason
                finish_reason = choice.finish_reason if hasattr(choice, 'finish_reason') else None

                # 获取原始响应
                raw_response = chunk.model_dump() if hasattr(chunk, 'model_dump') else None

                # 构造 CompletionResult
                result = build_completion_result(
                    message=message,
                    model=chunk.model,
                    finish_reason=finish_reason,
                    usage=usage,
                    raw_response=raw_response
                )

                yield result

    except Exception as e:
        raise LLMAPIError(f"Stream processing error: {str(e)}")


def parse_non_stream_response(response) -> CompletionResult:
    """
    解析非流式响应

    Args:
        response: 响应对象

    Returns:
        CompletionResult: 解析后的结果
    """
    # 提取消息
    message = None
    finish_reason = None

    if response.choices and len(response.choices) > 0:
        choice = response.choices[0]
        msg = choice.message

        # 提取工具调用
        tool_calls = extract_tool_calls(msg, is_delta=False)

        # 构造消息对象
        message = Message(
            role=msg.role,
            content=msg.content if hasattr(msg, 'content') else None,
            name=msg.name if hasattr(msg, 'name') and msg.name else None,
            function_call=msg.function_call if hasattr(msg, 'function_call') and msg.function_call else None,
            tool_calls=tool_calls,
            tool_call_id=msg.tool_call_id if hasattr(msg, 'tool_call_id') and msg.tool_call_id else None
        )

        # 提取 finish_reason
        finish_reason = choice.finish_reason

    # 提取 usage
    usage = extract_usage(response)

    # 获取原始响应
    raw_response = response.model_dump() if hasattr(response, 'model_dump') else None

    # 构造并返回结果
    return build_completion_result(
        message=message,
        model=response.model,
        finish_reason=finish_reason,
        usage=usage,
        raw_response=raw_response
    )
