# -*- coding: utf-8 -*-
"""
BOS-HA模型模块

提供手语识别模型的实现
"""

from bosha.server.models.hand_sign_model import HandSignModel
from bosha.server.models.openvino_model import OpenVinoHandSignModel

__all__ = [
    "HandSignModel",
    "OpenVinoHandSignModel",
]