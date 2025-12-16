#!/usr/bin/env python3
"""
Token2Audio Server - 重构版本
提供音频合成服务的HTTP和WebSocket接口
"""

import logging
import argparse
import uvicorn
import torch

from .app import create_app

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 默认配置
DEFAULT_MODEL_PATH = ""
DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8000
DEFAULT_SESSION_TIMEOUT = 60

def run_app():
    """主函数"""
    parser = argparse.ArgumentParser(description="Token2Audio Server")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind to")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="Port to bind to"
    )
    parser.add_argument(
        "--model-path", default=DEFAULT_MODEL_PATH, help="Path to model directory"
    )
    parser.add_argument(
        "--session-timeout",
        type=int,
        default=DEFAULT_SESSION_TIMEOUT,
        help="WebSocket session timeout",
    )
    parser.add_argument("--voice-list", nargs="*", help="语音列表 (voice_id:path 格式)")
    args = parser.parse_args()

    # 解析命令行传入的 voice_list
    cmd_voice_list = []
    if args.voice_list:
        for item in args.voice_list:
            parts = item.split(":")
            if len(parts) == 2:
                cmd_voice_list.append({"voice_id": parts[0], "path": parts[1]})

    print("=== Token2Audio Server ===")
    print(f"启动服务器: {args.host}:{args.port}")
    print(f"模型路径: {args.model_path}")
    print("API 接口:")
    print("  POST /v1/token2audio - 同步音频合成")
    print("  WebSocket /v1/token2audio - 流式音频合成")
    print("  GET /healthz - 健康检查")
    print("\n启动中...")

    # 创建应用
    app = create_app(
        args.model_path,
        voice_list=cmd_voice_list,
        active_session_timeout=args.session_timeout,
    )

    # 启动服务器
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    run_app()

