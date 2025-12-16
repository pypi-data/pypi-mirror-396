#!/usr/bin/env python3
"""
模型管理模块

提供模型的列表、选择、下载等功能
"""

import os
import json
import logging
from typing import Dict, List, Optional
import requests

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ModelManager:
    """
    模型管理类，负责模型的列表、选择、下载等功能
    """
    
    def __init__(self):
        """初始化模型管理器"""
        self.models_dir = self._get_models_dir()
        self.config_file = os.path.join(self.models_dir, "models.json")
        self.config = self._load_config()
    
    def _get_models_dir(self) -> str:
        """
        获取模型目录路径
        
        Returns:
            str: 模型目录的绝对路径
        """
        # 获取当前文件所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 模型目录位于server/models
        models_dir = os.path.join(current_dir, "../server/models")
        models_dir = os.path.abspath(models_dir)
        
        # 确保模型目录存在
        os.makedirs(models_dir, exist_ok=True)
        
        return models_dir
    
    def _load_config(self) -> Dict:
        """
        加载模型配置
        
        Returns:
            dict: 模型配置
        """
        default_config = {
            "current_model": "hand_sign_model",
            "default_model_url": "https://example.com/models/hand_sign_model.pt",
            "models": {}
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except json.JSONDecodeError as e:
                logger.error(f"解析配置文件失败: {e}")
                return default_config
        else:
            logger.info(f"配置文件不存在，使用默认配置")
            return default_config
    
    def _save_config(self):
        """保存模型配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def list_models(self) -> List[Dict[str, str]]:
        """
        列出所有可用模型
        
        Returns:
            list: 模型列表，每个模型包含name和path字段
        """
        models = []
        
        # 遍历模型目录，查找.pt和.xml文件
        if os.path.exists(self.models_dir):
            for file in os.listdir(self.models_dir):
                file_path = os.path.join(self.models_dir, file)
                if os.path.isfile(file_path):
                    if file.endswith('.pt'):
                        # PyTorch模型
                        model_name = os.path.splitext(file)[0]
                        models.append({
                            "name": model_name,
                            "path": file_path
                        })
                    elif file.endswith('.xml'):
                        # OpenVINO模型
                        model_name = os.path.splitext(file)[0]
                        models.append({
                            "name": model_name,
                            "path": file_path
                        })
        
        # 按名称排序
        models.sort(key=lambda x: x["name"])
        
        return models
    
    def select_model(self, model_name: str) -> bool:
        """
        选择要使用的模型
        
        Args:
            model_name: 模型名称
        
        Returns:
            bool: 选择成功返回True，否则返回False
        """
        # 检查模型是否存在
        models = self.list_models()
        model_exists = any(model["name"] == model_name for model in models)
        
        if model_exists:
            self.config["current_model"] = model_name
            self._save_config()
            logger.info(f"已选择模型: {model_name}")
            return True
        else:
            logger.error(f"模型不存在: {model_name}")
            return False
    
    def download_model(self, model_url: Optional[str] = None) -> str:
        """
        下载默认模型
        
        Args:
            model_url: 模型下载URL，默认为配置中的URL
        
        Returns:
            str: 下载的模型路径
        """
        if model_url is None:
            model_url = self.config["default_model_url"]
        
        # 使用get_sign_language_model.py中的下载逻辑
        from bosha.training.train import download_and_save_model
        
        logger.info(f"开始下载模型: {model_url}")
        model_path = download_and_save_model()
        
        if model_path:
            logger.info(f"模型下载成功: {model_path}")
            
            # 获取模型名称
            model_name = os.path.splitext(os.path.basename(model_path))[0]
            
            # 更新当前模型
            self.select_model(model_name)
            
            return model_path
        else:
            logger.error("模型下载失败")
            return ""
    
    def get_current_model(self) -> Dict[str, str]:
        """
        获取当前使用的模型信息
        
        Returns:
            dict: 当前模型的信息，包含name和path字段
        """
        model_name = self.config["current_model"]
        models = self.list_models()
        
        for model in models:
            if model["name"] == model_name:
                return model
        
        # 如果当前模型不存在，返回第一个模型
        if models:
            return models[0]
        else:
            return {"name": "", "path": ""}
    
    def get_model_path(self, model_name: Optional[str] = None) -> str:
        """
        获取模型的完整路径
        
        Args:
            model_name: 模型名称，默认为当前模型
        
        Returns:
            str: 模型的完整路径
        """
        if model_name is None:
            model_name = self.config["current_model"]
        
        models = self.list_models()
        for model in models:
            if model["name"] == model_name:
                return model["path"]
        
        return ""
    
    def get_model_info(self, model_name: Optional[str] = None) -> Dict:
        """
        获取模型的详细信息
        
        Args:
            model_name: 模型名称，默认为当前模型
        
        Returns:
            dict: 模型的详细信息
        """
        if model_name is None:
            model_name = self.config["current_model"]
        
        models = self.list_models()
        for model in models:
            if model["name"] == model_name:
                # 获取文件大小
                file_size = os.path.getsize(model["path"])
                
                # 确定模型类型
                if model["path"].endswith('.pt'):
                    model_type = "PyTorch"
                elif model["path"].endswith('.xml'):
                    model_type = "OpenVINO"
                else:
                    model_type = "Unknown"
                
                return {
                    "name": model["name"],
                    "path": model["path"],
                    "size": file_size,
                    "type": model_type
                }
        
        return {}
