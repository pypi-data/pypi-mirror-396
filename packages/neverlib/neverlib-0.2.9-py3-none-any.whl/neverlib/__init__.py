'''
Author: 凌逆战 | Never
Date: 2025-09-07
Description: neverlib - 音频处理和VAD工具集

这是一个提供音频处理、增强、分析和语音活动检测(VAD)功能的Python库。
该库使用懒加载机制，可以根据需要导入模块，提高启动速度并减少内存占用。

主要功能模块:
- utils: 实用工具函数
- vad: 语音活动检测
- audio_aug: 音频增强和数据增广
- filter: 滤波和音频处理
- data_analyze: 数据分析工具
- metrics: 音频质量评估指标

注意: 所有功能需要通过具体子模块导入，例如:
  from neverlib.audio_aug import limiter
  from neverlib.vad import EnergyVad_C
  from neverlib.filter import HPFilter
'''
try:
    import re
    import pathlib

    # 获取pyproject.toml的路径
    _pyproject_path = pathlib.Path(__file__).parent.parent / "pyproject.toml"

    # 读取版本号
    if _pyproject_path.exists():
        with open(_pyproject_path, "r", encoding="utf-8") as f:
            content = f.read()
            # 使用正则表达式匹配版本号
            version_match = re.search(r'version\s*=\s*"([^"]+)"', content)
            if version_match:
                __version__ = version_match.group(1)
except Exception:
    __version__ = "0.1.2"  # 如果出错, 使用默认版本号

from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from .utils import get_path_list
    from .filter import HPFilter
    from .audio_aug import volume_norm

# 懒加载子包，减少初始导入开销
from lazy_loader import attach

__getattr__, __dir__, __all__ = attach(
    __name__,
    submodules=["audio_aug", "data_analyze", "filter", "metrics", "utils", "vad", ],
    # 只导出子模块，不直接导出函数
    submod_attrs={
        "utils": ["get_path_list"],
        "filter": ["HPFilter"],
        "audio_aug": ["volume_norm"],
    }
)

if TYPE_CHECKING:
    __all__ = [
        "get_path_list",
        "HPFilter",
        "volume_norm",
    ]
