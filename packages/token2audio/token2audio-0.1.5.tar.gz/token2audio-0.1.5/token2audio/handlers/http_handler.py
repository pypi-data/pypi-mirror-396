import logging
import torch
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from ..utils.model_manager import ModelManager
import sys
import os

from ..protocol import Token2AudioRequest

logger = logging.getLogger(__name__)


class HTTPHandler:
    """HTTP请求处理器"""

    def __init__(self, model_path: str, voice_list: list):
        self.model_path = model_path
        self.voice_list = voice_list
        # 预先获取模型实例（模型已在 app.py 中初始化）
        self.model = ModelManager.get_model(model_path, voice_list)

    async def token2audio_http(self, request: Token2AudioRequest):
        """同步 HTTP 接口"""
        logger.info(f"[INFO] Received token2audio request - {request.model_dump()}")

        try:
            model = ModelManager.get_model(self.model_path, self.voice_list)

            # 验证 voice_id 是否存在于预加载的缓存中
            if request.voice_id not in model.prompt_caches:
                raise ValueError(
                    f"Voice ID '{request.voice_id}' not found in preloaded cache"
                )

            # 使用预加载的缓存
            prompt_dict = model.prompt_caches[request.voice_id]
            audio, audio_sr = model.token2audio_nonstream(
                torch.tensor(request.tokens).unsqueeze(0), prompt_dict
            )
            [audio, duration] = model.encode_wav(audio, audio_sr)
            return JSONResponse(
                content={"audio": audio, "duration": duration}, status_code=200
            )
        except Exception as e:
            logger.error(f"Exception occurred: {e}")
            model = ModelManager.get_model(self.model_path, self.voice_list)
            model.health_status = False
            return JSONResponse(
                content={"error": f"Error occurred when transcribe audio: {str(e)}"},
                status_code=500,
            )

    async def health_check(self):
        """健康检查接口"""
        model = ModelManager.get_model(self.model_path, self.voice_list)
        if model.health_status == False:
            logger.info("Health check failed, restarting service...")
            return JSONResponse(
                content={"status": "error", "message": "Service unhealthy"},
                status_code=503,
            )
        else:
            return {"status": "ok"}
