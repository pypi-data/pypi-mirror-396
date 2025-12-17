# -*- coding: utf-8 -*-
"""
BOS-HA训练模块

提供模型训练、评估、转换等功能
"""

from bosha.training.train import train_model
from bosha.training.evaluate import evaluate_model
from bosha.training.convert_to_openvino import convert_model_to_openvino

__all__ = [
    "train_model",
    "evaluate_model",
    "convert_model_to_openvino",
]