import asyncio
import time
import uuid
import logging
from dataclasses import dataclass
from typing import Optional, List
from fastapi import WebSocket, WebSocketDisconnect
from ..utils.model_manager import ModelManager
import sys
import os

from ..protocol import (
    WSRequest,
    WSEventType,
    WSResponseCreatedEvent,
    WSResponseCreatedData,
    WSResponseAudioDeltaEvent,
    WSResponseAudioDeltaData,
    WSResponseAudioFlushEvent,
    WSResponseAudioFlushData,
    WSResponseAudioDoneEvent,
    WSResponseAudioDoneData,
    WSErrorEvent,
    WSErrorData,
)

logger = logging.getLogger(__name__)


@dataclass
class SessionState:
    """WebSocket 会话状态"""

    session_id: Optional[str] = None
    voice_id: Optional[str] = None
    chunks_idx: int = 0
    all_audio_chunks: List[bytes] = None
    chunk_list: List[int] = None
    audio_sr: Optional[int] = None
    last_received_event_time: Optional[float] = None
    last_response_event_time: Optional[float] = None
    start_time: Optional[float] = None
    exception_occurred: bool = False
    accumulated_tokens: List[int] = None
    model: Optional[object] = None  # Store the model instance

    def __post_init__(self):
        if self.all_audio_chunks is None:
            self.all_audio_chunks = []
        if self.accumulated_tokens is None:
            self.accumulated_tokens = []

    def reset(self):
        """重置会话状态"""
        self.session_id = None
        self.voice_id = None
        self.chunks_idx = 0
        self.all_audio_chunks = []
        self.audio_sr = None
        self.accumulated_tokens = []
        self.model = None


class WebSocketHandler:
    """WebSocket请求处理器"""

    def __init__(
        self,
        model_path: str,
        voice_list: list = None,
        chunk_list: List[int] = [16, 16, 24, 24, 48],
        active_session_timeout: int = 60,
    ):
        self.model_path = model_path
        self.voice_list = voice_list
        self.active_session_timeout = active_session_timeout
        self.chunk_list = chunk_list
        # 预先获取模型实例（模型已在 app.py 中初始化）
        self.model = ModelManager.get_model(model_path, voice_list)

    async def handle_websocket(self, websocket: WebSocket):
        """处理WebSocket连接"""
        await websocket.accept()

        session_state = SessionState()
        session_state.chunk_list = self.chunk_list

        while True:
            try:
                message = await asyncio.wait_for(
                    websocket.receive_json(), timeout=self.active_session_timeout
                )
                request = WSRequest.model_validate(message)
                print("got request", request)

                if session_state.start_time is None:
                    session_state.start_time = time.perf_counter()

                if session_state.last_received_event_time is None:
                    session_state.last_received_event_time = session_state.start_time

                current_stream_received_time = time.perf_counter()
                if session_state.last_response_event_time is None:
                    session_state.last_response_event_time = session_state.start_time

                if request.type == WSEventType.TOKEN2AUDIO_CREATE:
                    await self._handle_create_request(websocket, request, session_state)

                elif request.type == WSEventType.TOKEN2AUDIO_DELTA:
                    await self._handle_delta_request(websocket, request, session_state)

                elif request.type == WSEventType.TOKEN2AUDIO_FLUSH:
                    await self._handle_flush_request(websocket, request, session_state)
                    # 重置会话状态
                    session_state.reset()

                elif request.type == WSEventType.TOKEN2AUDIO_DONE:
                    await self._handle_done_request(websocket, request, session_state)
                    await websocket.close()
                    return
                else:
                    raise ValueError(
                        f"Please check your event type, only support [{WSEventType.TOKEN2AUDIO_CREATE} | {WSEventType.TOKEN2AUDIO_DELTA} | {WSEventType.TOKEN2AUDIO_DONE}], but get {request.type}"
                    )

                session_state.last_received_event_time = current_stream_received_time

            except WebSocketDisconnect as e:
                session_state.exception_occurred = True
                logger.info(
                    f"WebSocket connection closed: {session_state.session_id}, error: {e}"
                )
                return
            except asyncio.TimeoutError:
                session_state.exception_occurred = True
                logger.warning(
                    f"WebSocket message receive timeout: {session_state.session_id}"
                )
                await self._send_error_response(
                    websocket,
                    session_state.session_id,
                    "TIMEOUT_ERROR",
                    "Timeout waiting for message",
                    {
                        "error": f"Fail to receive message within {self.active_session_timeout} seconds"
                    },
                )
                await websocket.close(1011)
                return
            except Exception as e:
                session_state.exception_occurred = True
                if "CUDA failed with error out of memory" in str(e):
                    model = ModelManager.get_model(self.model_path, self.voice_list)
                    model.health_status = False
                elif "CUDA error: an illegal memory access was encountered" in str(e):
                    model = ModelManager.get_model(self.model_path, self.voice_list)
                    model.health_status = False
                logger.error(f"Error in create_websocket_stream_response: {e}")
                raise
            finally:
                if session_state.exception_occurred:
                    # print stack
                    import traceback
                    traceback.print_exc()
                    # clean up vocoder cache.
                    logger.info(
                        f"{session_state.session_id} has exception occurred, do clean up cache auto now."
                    )
                    model = ModelManager.get_model(self.model_path, self.voice_list)
                    model.clean_up()

    async def _handle_create_request(
        self, websocket, request, session_state: SessionState
    ):
        """处理创建请求"""
        if session_state.session_id is not None:
            raise ValueError("TTS session already created")

        session_state.session_id = websocket.headers.get("x-request-id", None)
        if session_state.session_id is None:
            session_state.session_id = f"ws_{uuid.uuid4()}"
        logger.info(f"Received request - session_id: {session_state.session_id}")

        # 从请求中获取 voice_id
        session_state.voice_id = request.data.get("voice_id")
        if not session_state.voice_id:
            raise ValueError("voice_id is required in create request")

        # 获取并存储模型实例到会话状态
        model = ModelManager.get_model(self.model_path, self.voice_list)
        session_state.model = model

        # 验证 voice_id 是否存在于预加载的缓存中
        if session_state.voice_id not in model.prompt_caches:
            raise ValueError(
                f"Voice ID '{session_state.voice_id}' not found in preloaded cache"
            )

        # 初始化流式缓存
        prompt_dict = model.prompt_caches[session_state.voice_id]
        # 使用预加载的 prompt_dict 来设置流式缓存
        model.set_stream_cache_from_prompt_dict(prompt_dict)

        response = WSResponseCreatedEvent(
            event_id=request.event_id,
            type=WSEventType.RESPONSE_CREATED,
            data=WSResponseCreatedData(id=session_state.session_id),
        )

        await websocket.send_json(response.model_dump())

    async def _handle_delta_request(
        self, websocket, request, session_state: SessionState
    ):
        """处理增量请求"""
        if session_state.session_id is None:
            raise ValueError("Token2Audio session not created")

        # 将新的 tokens 添加到累积列表中
        new_tokens = request.data["tokens"]
        session_state.accumulated_tokens.extend(new_tokens)

        # 获取当前 chunk 的大小
        if session_state.chunks_idx < len(session_state.chunk_list):
            current_chunk_size = session_state.chunk_list[session_state.chunks_idx]
        else:
            # 如果 chunk_idx 超出范围，使用最后一个元素的大小
            current_chunk_size = session_state.chunk_list[-1]

        # 检查是否达到当前 chunk 的大小
        if len(session_state.accumulated_tokens) >= current_chunk_size:
            # 取出需要处理的 tokens
            tokens_to_process = session_state.accumulated_tokens[:current_chunk_size]
            session_state.accumulated_tokens = session_state.accumulated_tokens[
                current_chunk_size:
            ]

            # 进行推理
            await self._process_tokens_chunk(
                websocket, session_state, tokens_to_process
            )

            # 增加 chunk 索引
            session_state.chunks_idx += 1

    async def _process_tokens_chunk(
        self, websocket, session_state: SessionState, tokens_to_process: List[int], last_chunk: bool = False
    ):
        """处理一个 chunk 的 tokens"""
        if session_state.model is None:
            raise ValueError("Model instance not found in session state")

        model = session_state.model
        prompt_dict = model.prompt_caches[session_state.voice_id]

        # 记录推理开始时间
        import time

        inference_start_time = time.perf_counter()

        out_audio, out_audio_sr = model.token2wav_stream(
            tokens_to_process, prompt_dict, session_state.session_id, last_chunk
        )

        # 计算推理耗时
        inference_time = (
            time.perf_counter() - inference_start_time
        ) * 1000  # 转换为毫秒

        if session_state.audio_sr is None:
            session_state.audio_sr = out_audio_sr
        if out_audio is not None:
            session_state.all_audio_chunks.append(out_audio)
            encoded_wav, duration = model.encode_wav(out_audio, out_audio_sr)
            audio_response = WSResponseAudioDeltaEvent(
                event_id=str(uuid.uuid4()),
                type=WSEventType.RESPONSE_AUDIO_DELTA,
                data=WSResponseAudioDeltaData(
                    response_id=session_state.session_id
                    + f"_{session_state.chunks_idx}",
                    status="finished" if last_chunk else "unfinished",
                    audio=encoded_wav,
                    audio_tokens=tokens_to_process,
                    duration=duration,
                    inference_time=inference_time,
                ),
            )
            await websocket.send_json(audio_response.model_dump())

    async def _handle_flush_request(
        self, websocket, request, session_state: SessionState
    ):
        """处理刷新请求"""
        if session_state.session_id:
            model = ModelManager.get_model(self.model_path, self.voice_list)
            prompt_dict = model.prompt_caches[session_state.voice_id]
            out_audio, out_audio_sr = model.token2wav_stream(
                [], prompt_dict, session_state.session_id, True
            )
            if out_audio is not None:
                session_state.all_audio_chunks.append(out_audio)
                encoded_wav, duration = model.encode_wav(out_audio, out_audio_sr)
                audio_response = WSResponseAudioDeltaEvent(
                    event_id=str(uuid.uuid4()),
                    type=WSEventType.RESPONSE_AUDIO_DELTA,
                    data=WSResponseAudioDeltaData(
                        response_id=session_state.session_id
                        + f"_{session_state.chunks_idx}",
                        status="finished",
                        audio=encoded_wav,
                        audio_tokens="",
                        duration=duration,
                    ),
                )
                print("send delta response", audio_response)
                await websocket.send_json(audio_response.model_dump())

            # 清理资源
            model.clean_up()

        flush_response = WSResponseAudioFlushEvent(
            event_id=str(uuid.uuid4()),
            type=WSEventType.RESPONSE_AUDIO_FLUSH,
            data=WSResponseAudioFlushData(
                response_id=(
                    session_state.session_id if session_state.session_id else ""
                ),
                audio="",
                audio_tokens="",
            ),
        )
        await websocket.send_json(flush_response.model_dump())

    async def _handle_done_request(
        self, websocket, request, session_state: SessionState
    ):
        """处理完成请求"""
        if session_state.session_id is None:
            raise ValueError("Token2Audio session not created")

        # 处理剩余的 tokens
        if len(session_state.accumulated_tokens) > 0:
            # 获取当前 chunk 的大小
            if session_state.chunks_idx < len(session_state.chunk_list):
                current_chunk_size = session_state.chunk_list[session_state.chunks_idx]
            else:
                # 如果 chunk_idx 超出范围，使用最后一个元素的大小
                current_chunk_size = session_state.chunk_list[-1]

            # 处理剩余的 tokens
            remaining_tokens = session_state.accumulated_tokens
            while remaining_tokens:
                # 取出当前 chunk 大小的 tokens
                tokens_to_process = remaining_tokens[:current_chunk_size]
                remaining_tokens = remaining_tokens[current_chunk_size:]

                # 判断是否是最后一个 chunk
                is_last_chunk = len(remaining_tokens) == 0

                # 进行推理，最后一个 chunk 标记为 last_chunk=True
                await self._process_tokens_chunk(
                    websocket, session_state, tokens_to_process, is_last_chunk
                )

                # 增加 chunk 索引
                session_state.chunks_idx += 1

                # 更新 chunk 大小（如果还有剩余 tokens）
                if remaining_tokens:
                    if session_state.chunks_idx < len(session_state.chunk_list):
                        current_chunk_size = session_state.chunk_list[
                            session_state.chunks_idx
                        ]
                    else:
                        current_chunk_size = session_state.chunk_list[-1]

        else:
            pass

        done_response = WSResponseAudioDoneEvent(
            event_id=str(uuid.uuid4()),
            type=WSEventType.RESPONSE_AUDIO_DONE,
            data=WSResponseAudioDoneData(
                response_id=session_state.session_id,
                audio="",
                audio_tokens="",
            ),
        )
        print("send done response", done_response.model_dump())
        await websocket.send_json(done_response.model_dump())

    async def _send_error_response(self, websocket, session_id, code, message, details):
        """发送错误响应"""
        try:
            error_response = WSErrorEvent(
                event_id=str(uuid.uuid4()),
                type=WSEventType.RESPONSE_ERROR,
                data=WSErrorData(
                    response_id=session_id or "unknown",
                    code=code,
                    message=message,
                    details=details,
                ),
            )
            await websocket.send_json(error_response.model_dump())
        except Exception as e:
            logger.error(f"Failed to send error response: {str(e)}")
