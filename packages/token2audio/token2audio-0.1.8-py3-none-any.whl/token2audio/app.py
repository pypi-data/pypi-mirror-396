import logging
import argparse
from fastapi import FastAPI, WebSocket
from fastapi.responses import FileResponse
from .handlers import HTTPHandler, WebSocketHandler
from typing import Optional
import os

from .protocol import Token2AudioRequest

logger = logging.getLogger(__name__)

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(CURRENT_DIR, "assets")


def load_and_process_voices():
    """加载并处理 assets 目录下的语音文件"""
    voice_list = []
    if not os.path.exists(ASSETS_DIR):
        logger.warning(f"Assets directory not found: {ASSETS_DIR}")
        return voice_list

    logger.info(f"Scanning assets directory: {ASSETS_DIR}")
    for filename in os.listdir(ASSETS_DIR):
        if filename.lower().endswith(".wav"):
            file_path = os.path.join(ASSETS_DIR, filename)
            voice_id = os.path.splitext(filename)[0]

            voice_list.append({"voice_id": voice_id, "path": file_path})
            logger.info(f"Loaded voice: {voice_id}")

    return voice_list


def create_app(
    model_path: str,
    voice_list: Optional[list] = None,
    chunk_list=[16, 16, 24, 24, 48],
    active_session_timeout: int = 60,
) -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(title="Token2Audio Server", version="0.0.1")

    # 加载默认语音并合并
    default_voices = load_and_process_voices()
    if voice_list:
        final_voice_list = default_voices + voice_list
    else:
        final_voice_list = default_voices

    # 预先初始化模型（在创建应用时立即加载）
    from .utils.model_manager import ModelManager
    logger.info("正在初始化模型和预加载语音...")
    ModelManager.get_model(model_path, final_voice_list)
    logger.info("模型初始化完成，语音缓存已预加载")

    # 初始化处理器
    http_handler = HTTPHandler(model_path, final_voice_list)
    websocket_handler = WebSocketHandler(
        model_path, final_voice_list, chunk_list, active_session_timeout
    )

    @app.get("/")
    async def root():
        """返回测试页面"""
        html_path = os.path.join(ASSETS_DIR, "index.html")
        return FileResponse(html_path)

    @app.get("/v1/voices")
    async def get_voices():
        """获取可用的语音列表"""
        from .utils.model_manager import ModelManager

        model = ModelManager.get_model(model_path, final_voice_list)
        voice_list_response = []
        for voice_id in model.prompt_caches.keys():
            voice_list_response.append({"voice_id": voice_id})
        return {"voices": voice_list_response}

    @app.post("/v1/token2audio")
    async def token2audio_http(request: Token2AudioRequest):
        """同步 HTTP 接口"""
        return await http_handler.token2audio_http(request)

    @app.websocket("/v1/token2audio")
    async def token2audio_websocket(websocket: WebSocket):
        """流式 WebSocket 接口"""
        await websocket_handler.handle_websocket(websocket)

    @app.get("/healthz")
    async def health():
        """健康检查接口"""
        return await http_handler.health_check()

    return app


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(description="Token2Audio Server")
    parser.add_argument("--model-path", required=True, help="模型路径")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--host", default="0.0.0.0", help="绑定地址")
    parser.add_argument("--voice-list", nargs="*", help="语音列表 (voice_id:path 格式)")
    parser.add_argument("--session-timeout", type=int, default=60, help="会话超时时间")
    args = parser.parse_args()

    # 解析 voice_list
    voice_list = None
    if args.voice_list:
        voice_list = []
        for item in args.voice_list:
            parts = item.split(":")
            if len(parts) == 2:
                voice_list.append({"voice_id": parts[0], "path": parts[1]})

    import uvicorn
    app = create_app(
        model_path=args.model_path,
        voice_list=voice_list,
        active_session_timeout=args.session_timeout,
    )
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
