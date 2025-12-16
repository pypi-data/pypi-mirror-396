# -*- coding: utf-8 -*-
"""
BOS-HA服务端模块

提供WebSocket服务、模型管理等功能
"""

from bosha.server.main import start_server
from bosha.server.models.hand_sign_model import HandSignModel
from bosha.server.models.openvino_model import OpenVinoHandSignModel

__all__ = [
    "start_server",
    "HandSignModel",
    "OpenVinoHandSignModel",
]