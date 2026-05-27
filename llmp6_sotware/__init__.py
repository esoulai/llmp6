"""
LLMP6 - 六层可组合大语言模型架构

一种面向大型语言模型应用的六层可组合架构，支持灵活配置每层的模型和执行方式。

项目地址：https://github.com/esoulai/llmp6
"""

__version__ = "1.0.0"
__author__ = "刘洋秀"
__email__ = "liuyangxiu@esoulai.com"

from .pipeline import LLMP6Pipeline
from .config import LLMP6Config
from .cli import main

__all__ = ["LLMP6Pipeline", "LLMP6Config", "main"]
