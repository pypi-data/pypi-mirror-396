"""
Excel Merger - 合并多个 Excel 文件的工具

支持 CLI 和 Python API 两种使用方式。
"""

from .core import merge_excels
from .version import __version__

__all__ = ["merge_excels", "__version__"]
