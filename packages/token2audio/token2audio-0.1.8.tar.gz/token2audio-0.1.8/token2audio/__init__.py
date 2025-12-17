import sys

# 注册模块别名，让 hyperpyyaml 能找到类
# 模型配置文件中使用 cosyvoice2.xxx，但实际路径是 token2audio.cosyvoice2.xxx
from token2audio import cosyvoice2
from token2audio.cosyvoice2 import flow, transformer, utils

sys.modules['cosyvoice2'] = cosyvoice2
sys.modules['cosyvoice2.flow'] = flow
sys.modules['cosyvoice2.flow.flow'] = flow.flow
sys.modules['cosyvoice2.flow.flow_matching'] = flow.flow_matching
sys.modules['cosyvoice2.flow.decoder_dit'] = flow.decoder_dit
sys.modules['cosyvoice2.transformer'] = transformer
sys.modules['cosyvoice2.utils'] = utils

from .server import run_app
from .app import create_app

__all__ = ["run_app", "create_app"]
