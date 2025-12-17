import logging
import torch
from typing import Optional
from ..models.token2wav import Token2wav

logger = logging.getLogger(__name__)


class ModelManager:
    """模型管理器，负责模型的初始化和获取"""
    
    _instance: Optional[Token2wav] = None
    
    @classmethod
    def get_model(cls, model_path: str, voice_list: list) -> Token2wav:
        """获取模型实例（单例模式）"""
        if cls._instance is None:
            cls._instance = cls._initialize_model(model_path, voice_list)
        return cls._instance
    
    @classmethod
    def _initialize_model(cls, model_path: str, voice_list: list) -> Token2wav:
        """初始化模型"""
        # 检测 CUDA 和 ROCm 支持
        use_rocm = False
        use_cuda = False

        if torch.cuda.is_available():
            try:
                device_name = torch.cuda.get_device_name()
                logger.info(f"检测到 GPU: {device_name}")
                if "AMD" in device_name or "Radeon" in device_name:
                    use_rocm = True
                    logger.info("检测到 AMD GPU，启用 ROCm 支持")
                else:
                    use_cuda = True
                    logger.info("检测到 NVIDIA GPU，启用 CUDA 支持")
            except:
                logger.info("GPU 检测失败，使用 CPU 模式")
        else:
            logger.info("未检测到 CUDA 支持，使用 CPU 模式")

        # 如果没有提供 voice_list，使用空列表
        if voice_list is None:
            voice_list = []
            logger.warning("未提供 voice_list，将使用空列表")

        # 尝试使用相应的 GPU 支持，如果失败则回退到 CPU
        try:
            if use_rocm:
                model_instance = Token2wav(model_path, voice_list, use_rocm=True)
            elif use_cuda:
                model_instance = Token2wav(model_path, voice_list, use_rocm=False)
                # 在 Token2wav 内部，如果 use_rocm=False 且 CUDA 可用，会自动使用 CUDA
            else:
                model_instance = Token2wav(model_path, voice_list, use_rocm=False)
        except Exception as e:
            logger.error(f"GPU 初始化失败: {e}")
            logger.info("回退到 CPU 模式...")
            model_instance = Token2wav(model_path, voice_list, use_rocm=False)

        return model_instance
    
    @classmethod
    def reset_model(cls):
        """重置模型实例"""
        cls._instance = None

