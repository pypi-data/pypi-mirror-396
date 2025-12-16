"""
MCP 图像超分辨率服务器

基于Model Context Protocol (MCP)的服务器，提供阿里云图像超分辨率功能。
使用AI算法将图像放大2-4倍并智能提升清晰度。
"""

__version__ = "0.1.0"
__author__ = "fengjinchao"

# 导入主要模块和函数
from .server import main

__all__ = [
    "main",
]
