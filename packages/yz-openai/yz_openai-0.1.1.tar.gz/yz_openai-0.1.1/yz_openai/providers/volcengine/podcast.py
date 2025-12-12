"""
火山引擎 Podcast TTS 客户端
"""
import asyncio
import json
import logging
import uuid
import websockets
from typing import Dict, Any

from yz_openai.base.types import (
    PodcastResult,
    PodcastTextItem,
    Usage
)
from yz_openai.base.exceptions import (
    PodcastError,
    PodcastConnectionError,
    PodcastRoundError
)
from yz_openai.providers.volcengine.websocket_protocol import (
    start_connection,
    finish_connection,
    start_session,
    finish_session,
    receive_message,
    wait_for_event,
    MsgType,
    EventType
)

logger = logging.getLogger(__name__)


class VolcenginePodcast:
    """
    火山引擎 Podcast TTS 客户端

    功能：
    - 基于文档 URL 生成多人对话播客
    - 支持断点续传和重试机制
    - 自动处理 WebSocket 连接和会话管理
    """

    def __init__(self, app_id: str, access_key: str):
        """
        初始化 Volcengine Podcast 客户端

        Args:
            app_id: 火山引擎控制台获取的 APP ID
            access_key: 火山引擎控制台获取的 Access Token
        """
        self.app_id = app_id
        self.access_key = access_key
        self.resource_id = "volc.service_type.10050"
        self.app_key = "aGjiRDfUWi"
        self.endpoint = "wss://openspeech.bytedance.com/api/v3/sami/podcasttts"

    async def create(self, params: Dict[str, Any]) -> PodcastResult:
        """
        创建播客

        Args:
            params: 请求参数字典，包含以下字段：
                - action (int): 播客生成模式（必需），可选值：
                    * 0: 根据文档 URL 或文本总结生成播客
                    * 3: 根据对话文本直接生成播客
                    * 4: 根据提示文本扩展生成播客

                根据不同的 action，需要提供不同的参数：

                action=0 时：
                - input_text (str): 输入文本（与 input_url 二选一）
                - input_url (str): 输入文档 URL（与 input_text 二选一）
                - speakers (List[str]): 说话人列表，至少2个（必需）

                action=3 时：
                - nlp_texts (List[Dict]): 对话文本列表（必需），每项包含：
                    * text (str): 文本内容
                    * speaker (str): 说话人

                action=4 时：
                - prompt_text (str): 提示文本（必需）
                - speakers (List[str]): 说话人列表，至少2个（必需）

                通用可选参数：
                - audio_format (str): 音频格式，默认 "mp3"
                - sample_rate (int): 采样率，默认 24000
                - speech_rate (int): 语速，默认 0
                - use_head_music (bool): 是否添加片头音乐，默认 False
                - use_tail_music (bool): 是否添加片尾音乐，默认 False
                - return_audio_url (bool): 是否返回音频 URL，默认 True
                - only_nlp_text (bool): 是否仅返回 NLP 文本，默认 False
                - max_retries (int): 最大重试次数，默认 5

        Returns:
            PodcastResult: 播客结果对象，包含：
                - audio_data (bytes): 音频数据
                - audio_url (str): 音频 URL（如果 return_audio_url=True）
                - texts (List[PodcastTextItem]): 文本列表
                - total_rounds (int): 总轮次数
                - usage (Usage): Token 使用量统计

        Raises:
            PodcastError: 参数错误
            PodcastConnectionError: 连接失败
            PodcastRoundError: 轮次处理失败

        Examples:
            >>> # action=0: 根据文档 URL 生成
            >>> client = VolcenginePodcast(app_id="xxx", access_key="xxx")
            >>> result = await client.create({
            ...     "action": 0,
            ...     "input_url": "https://example.com/doc.pdf",
            ...     "speakers": ["speaker1", "speaker2"]
            ... })

            >>> # action=3: 根据对话文本生成
            >>> result = await client.create({
            ...     "action": 3,
            ...     "nlp_texts": [
            ...         {"speaker": "speaker1", "text": "你好"},
            ...         {"speaker": "speaker2", "text": "你好啊"}
            ...     ]
            ... })

            >>> # action=4: 根据提示文本扩展生成
            >>> result = await client.create({
            ...     "action": 4,
            ...     "prompt_text": "讨论人工智能的发展",
            ...     "speakers": ["speaker1", "speaker2"]
            ... })
        """
        # 1. 验证 action 参数
        if "action" not in params:
            raise PodcastError("缺少必需参数: action")

        action = params["action"]
        if action not in [0, 3, 4]:
            raise PodcastError(f"action 参数无效: {action}，必须是 0、3 或 4")

        # 2. 根据 action 验证对应的必需参数
        if action == 0:
            # action=0: 需要 input_text 或 input_url，以及 speakers
            has_input_text = "input_text" in params and params["input_text"]
            has_input_url = "input_url" in params and params["input_url"]

            if not has_input_text and not has_input_url:
                raise PodcastError("action=0 时，input_text 和 input_url 必须提供其中一个")

            if "speakers" not in params or len(params["speakers"]) < 2:
                raise PodcastError("action=0 时，speakers 列表至少需要2个说话人")

        elif action == 3:
            # action=3: 需要 nlp_texts
            if "nlp_texts" not in params or not params["nlp_texts"]:
                raise PodcastError("action=3 时，nlp_texts 列表不能为空")

        elif action == 4:
            # action=4: 需要 prompt_text 和 speakers
            if "prompt_text" not in params or not params["prompt_text"]:
                raise PodcastError("action=4 时，prompt_text 不能为空")

            if "speakers" not in params or len(params["speakers"]) < 2:
                raise PodcastError("action=4 时，speakers 列表至少需要2个说话人")

        # 3. 提取通用参数
        audio_format = params.get("audio_format", "mp3")
        sample_rate = params.get("sample_rate", 24000)
        speech_rate = params.get("speech_rate", 0)
        use_head_music = params.get("use_head_music", False)
        use_tail_music = params.get("use_tail_music", False)
        return_audio_url = params.get("return_audio_url", True)
        only_nlp_text = params.get("only_nlp_text", False)
        max_retries = params.get("max_retries", 5)

        # 4. 根据 action 构建请求参数
        req_params = {
            "input_id": f"podcast_{uuid.uuid4().hex[:8]}",
            "action": action,
            "use_head_music": use_head_music,
            "use_tail_music": use_tail_music,
            "audio_config": {
                "format": audio_format,
                "sample_rate": sample_rate,
                "speech_rate": speech_rate
            }
        }

        # 根据不同的 action 添加特定参数
        if action == 0:
            # action=0: 根据文档 URL 或文本总结生成
            input_info = {
                "return_audio_url": return_audio_url,
                "only_nlp_text": only_nlp_text
            }

            if "input_text" in params and params["input_text"]:
                input_info["input_text"] = params["input_text"]

            if "input_url" in params and params["input_url"]:
                input_info["input_url"] = params["input_url"]

            req_params["input_info"] = input_info
            req_params["speaker_info"] = {
                "speakers": params["speakers"]
            }

        elif action == 3:
            # action=3: 根据对话文本直接生成
            req_params["nlp_texts"] = params["nlp_texts"]
            req_params["input_info"] = {
                "return_audio_url": return_audio_url
            }

        elif action == 4:
            # action=4: 根据提示文本扩展生成
            req_params["prompt_text"] = params["prompt_text"]
            req_params["speaker_info"] = {
                "speakers": params["speakers"]
            }

        return await self._create_full(req_params, max_retries)

    async def _create_full(self, req_params: dict, max_retries: int) -> PodcastResult:
        """非流式生成播客（完整响应）"""
        is_podcast_round_end = True
        audio_received = False
        last_round_id = -1
        task_id = ""
        websocket = None
        retry_num = max_retries
        podcast_audio = bytearray()
        audio = bytearray()
        current_round = 0
        podcast_texts = []
        audio_url = None
        total_rounds = 0

        # 累计 Token 使用量
        total_input_tokens = 0
        total_output_tokens = 0

        try:
            while retry_num > 0:
                try:
                    # 建立 WebSocket 连接
                    websocket = await self._connect()
                    logger.info("WebSocket 连接已建立")

                    # 如果是重试，添加重试信息
                    if not is_podcast_round_end:
                        req_params["retry_info"] = {
                            "retry_task_id": task_id,
                            "last_finished_round_id": last_round_id
                        }

                    # Start connection [event=1]
                    await start_connection(websocket)

                    # Connection started [event=50]
                    await wait_for_event(
                        websocket,
                        MsgType.FullServerResponse,
                        EventType.ConnectionStarted
                    )
                    logger.info("连接已启动")

                    # 生成会话 ID
                    session_id = str(uuid.uuid4())
                    if not task_id:
                        task_id = session_id

                    # Start session [event=100]
                    await start_session(
                        websocket,
                        json.dumps(req_params).encode(),
                        session_id
                    )

                    # Session started [event=150]
                    await wait_for_event(
                        websocket,
                        MsgType.FullServerResponse,
                        EventType.SessionStarted
                    )
                    logger.info("会话已启动")

                    # Finish session [event=102]
                    await finish_session(websocket, session_id)

                    # 接收响应
                    while True:
                        msg = await receive_message(websocket)
                        
                        # 音频数据块
                        if msg.type == MsgType.AudioOnlyServer and msg.event == EventType.PodcastRoundResponse:
                            if not audio_received and audio:
                                audio_received = True
                            audio.extend(msg.payload)
                            logger.info(f"收到音频数据: {len(msg.payload)} bytes")

                        # 错误信息
                        elif msg.type == MsgType.Error:
                            error_msg = msg.payload.decode()
                            logger.error(f"服务器错误: {error_msg}")
                            raise PodcastRoundError(f"服务器错误: {error_msg}")

                        elif msg.type == MsgType.FullServerResponse:
                            # 播客 round 开始
                            if msg.event == EventType.PodcastRoundStart:
                                data = json.loads(msg.payload.decode())
                                if data.get("text"):
                                    podcast_texts.append(
                                        PodcastTextItem(
                                            text=data.get("text"),
                                            speaker=data.get("speaker")
                                        )
                                    )
                                current_round = data.get("round_id")
                                is_podcast_round_end = False
                                logger.info(
                                    f"新轮次开始: round_id={current_round}, speaker={data.get('speaker')}")

                            # 播客 round 结束
                            if msg.event == EventType.PodcastRoundEnd:
                                data = json.loads(msg.payload.decode())
                                logger.info(f"轮次结束: {data}")

                                if data.get("is_error"):
                                    error_msg = data.get(
                                        "error_message", "未知错误")
                                    raise PodcastRoundError(
                                        f"轮次处理失败: {error_msg}")

                                is_podcast_round_end = True
                                last_round_id = current_round

                                if audio:
                                    podcast_audio.extend(audio)
                                    logger.info(f"保存轮次音频: {len(audio)} bytes")
                                    audio.clear()

                            # 播客结束
                            if msg.event == EventType.PodcastEnd:
                                data = json.loads(msg.payload.decode())
                                audio_url = data.get("meta_info").get("audio_url")
                                total_rounds = data.get(
                                    "total_rounds", len(podcast_texts))
                                logger.info(
                                    f"播客生成完成: audio_url={audio_url}, total_rounds={total_rounds}")

                            # Token 使用量统计（按轮次累加）
                            if msg.event == EventType.UsageResponse:
                                data = json.loads(msg.payload.decode())
                                usage_info = data.get("usage", {})

                                # 累加每个轮次的 token 使用量
                                input_tokens = usage_info.get("input_text_tokens", 0)
                                output_tokens = usage_info.get("output_audio_tokens", 0)
                                total_input_tokens += input_tokens
                                total_output_tokens += output_tokens

                                logger.info(
                                    f"Token 消耗情况 (当前轮次): input={input_tokens}, output={output_tokens}, "
                                    f"累计: input={total_input_tokens}, output={total_output_tokens}"
                                )

                        # 会话结束
                        if msg.event == EventType.SessionFinished:
                            logger.info("会话已结束")
                            break

                    # 关闭连接
                    await finish_connection(websocket)
                    await wait_for_event(
                        websocket,
                        MsgType.FullServerResponse,
                        EventType.ConnectionFinished
                    )
                    logger.info("连接已关闭")

                    # 播客结束，返回结果
                    if is_podcast_round_end:
                        # 构造 Usage 对象（如果有 token 使用量数据）
                        usage_data = None
                        if total_input_tokens > 0 or total_output_tokens > 0:
                            usage_data = Usage(
                                prompt_tokens=total_input_tokens,
                                completion_tokens=total_output_tokens,
                                total_tokens=total_input_tokens + total_output_tokens
                            )

                        return PodcastResult(
                            audio_data=bytes(podcast_audio),
                            audio_url=audio_url,
                            texts=podcast_texts,
                            total_rounds=total_rounds,
                            usage=usage_data
                        )
                    else:
                        logger.error(f"播客未完成，从 round {last_round_id} 继续")
                        retry_num -= 1
                        await asyncio.sleep(1)

                except Exception as e:
                    logger.error(f"处理过程中出错: {str(e)}")
                    retry_num -= 1
                    if retry_num > 0:
                        logger.info(f"剩余重试次数: {retry_num}")
                        await asyncio.sleep(1)
                    else:
                        raise
                finally:
                    if websocket:
                        await websocket.close()

            raise PodcastError(f"重试次数已用尽，播客生成失败")

        finally:
            if websocket:
                await websocket.close()

    async def _connect(self) -> websockets.WebSocketClientProtocol:
        """建立 WebSocket 连接"""
        headers = {
            "X-Api-App-Id": self.app_id,
            "X-Api-Access-Key": self.access_key,
            "X-Api-App-Key": self.app_key,
            "X-Api-Resource-Id": self.resource_id,
            "X-Api-Connect-Id": str(uuid.uuid4())
        }

        try:
            websocket = await websockets.connect(
                self.endpoint,
                additional_headers=headers
            )
            return websocket
        except Exception as e:
            raise PodcastConnectionError(f"连接失败: {str(e)}")

    async def close(self):
        """关闭客户端"""
        pass
