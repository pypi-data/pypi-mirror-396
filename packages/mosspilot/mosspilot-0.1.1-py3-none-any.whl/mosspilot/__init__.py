"""
MossPilot 自动化测试框架

全功能自动化测试框架，支持API、UI和性能测试
"""

__version__ = "0.1.1"
__author__ = "MossPilot Team"
__email__ = "team@mosspilot.com"

from .core.config import settings
from .core.base import TestBase

__all__ = ["settings", "TestBase", "__version__"]