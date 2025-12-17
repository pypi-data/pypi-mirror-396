# -*- coding: utf-8 -*-
"""
BOS-HA - 基于深度学习的手语识别系统

BOS-HA是一个完整的手语识别系统，包括：
- 模型训练模块
- 服务端服务
- 客户端界面
- 模型管理功能

版本: 1.0.0
"""

__version__ = "1.0.3"
__author__ = "BOS-HA Team"
__description__ = "基于深度学习的手语识别系统"

# 导出主要模块和类
from bosha.training import train_model, evaluate_model, convert_model_to_openvino
from bosha.server import start_server
from bosha.client import start_client
from bosha.server.models import HandSignModel, OpenVinoHandSignModel

__all__ = [
    "train_model",
    "evaluate_model",
    "convert_model_to_openvino",
    "start_server",
    "start_client",
    "HandSignModel",
    "OpenVinoHandSignModel",
]