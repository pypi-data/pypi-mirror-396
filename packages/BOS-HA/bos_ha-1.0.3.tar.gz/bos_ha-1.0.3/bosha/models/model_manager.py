#!/usr/bin/env python3
"""
模型管理器

用于管理手语识别模型，包括：
1. 模型列表管理
2. 模型下载
3. 模型选择
4. 模型配置
"""

import os
import json
import requests
import shutil
from typing import Dict, List, Optional

class ModelManager:
    """模型管理器类"""
    
    def __init__(self, config_path: str = None):
        """
        初始化模型管理器
        
        Args:
            config_path: 配置文件路径，默认为 None
        """
        # 默认配置路径
        if config_path is None:
            self.config_path = os.path.join(os.path.expanduser("~"), ".bosha", "config.json")
        else:
            self.config_path = config_path
        
        # 创建配置目录
        self.config_dir = os.path.dirname(self.config_path)
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        
        # 加载配置
        self.config = self._load_config()
        
        # 确保模型目录存在
        self.models_dir = os.path.join(os.path.expanduser("~"), ".bosha", "models")
        if not os.path.exists(self.models_dir):
            os.makedirs(self.models_dir)
    
    def _load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        # 默认配置
        default_config = {
            "current_model": "hand_sign_model",
            "default_model_url": "https://example.com/models/hand_sign_model.pt",
            "models": {},
            "available_models": {
                "sign_gemma": {
                    "name": "SignGemma",
                    "type": "大规模手语翻译模型",
                    "description": "由谷歌 DeepMind 推出，定位为最强手语到文本/语音的 AI 模型，提供从手语到文本、语音的完整翻译能力，支持多种手语语言，具有强大的上下文理解能力和实时翻译能力。",
                    "url": "https://example.com/models/sign_gemma.pt",
                    "arch": "transformer"
                },
                "clip_sla": {
                    "name": "CLIP-SLA",
                    "type": "跨模态手语理解模型",
                    "description": "结合了 CLIP 的跨模态学习能力，专注于手语与文本、图像之间的跨模态理解，支持手语分类、检索和生成等多种任务，具有良好的泛化能力。",
                    "url": "https://example.com/models/clip_sla.pt",
                    "arch": "clip-based"
                },
                "tslformer": {
                    "name": "TSLFormer",
                    "type": "时序手语翻译模型",
                    "description": "基于 Transformer 的时序手语翻译模型，专注于将连续手语动作序列转换为自然语言文本，具有良好的时序建模能力和长文本生成能力。",
                    "url": "https://example.com/models/tslformer.pt",
                    "arch": "transformer"
                },
                "signer_invariant": {
                    "name": "Signer-Invariant Conformer",
                    "type": "说话者不变性手语识别模型",
                    "description": "基于 Conformer 架构，具有强大的说话者不变性，能够适应不同说话者的手语风格和习惯，提高跨说话者的识别准确率。",
                    "url": "https://example.com/models/signer_invariant.pt",
                    "arch": "conformer"
                },
                "siformer": {
                    "name": "Siformer",
                    "type": "高效手语识别模型",
                    "description": "专为高效手语识别设计的轻量级模型，在保证识别准确率的同时，降低了模型参数量和计算复杂度，适合部署在资源受限的设备上。",
                    "url": "https://example.com/models/siformer.pt",
                    "arch": "lightweight-transformer"
                }
            }
        }
        
        # 如果配置文件存在，则加载配置
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                
                # 合并配置，确保所有必要的字段都存在
                config = self._merge_configs(default_config, config)
                return config
            except Exception as e:
                print(f"加载配置失败: {e}")
                return default_config
        else:
            # 保存默认配置
            self._save_config(default_config)
            return default_config
    
    def _merge_configs(self, default: Dict, user: Dict) -> Dict:
        """
        合并配置，确保所有必要的字段都存在
        
        Args:
            default: 默认配置
            user: 用户配置
            
        Returns:
            合并后的配置
        """
        merged = default.copy()
        
        # 合并用户配置
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # 递归合并字典
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
        
        return merged
    
    def _save_config(self, config: Dict) -> bool:
        """
        保存配置文件
        
        Args:
            config: 配置字典
            
        Returns:
            是否保存成功
        """
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def list_models(self) -> List[Dict]:
        """
        列出所有可用模型
        
        Returns:
            可用模型列表
        """
        models = []
        
        # 遍历模型目录
        if os.path.exists(self.models_dir):
            for filename in os.listdir(self.models_dir):
                file_path = os.path.join(self.models_dir, filename)
                if os.path.isfile(file_path):
                    # 获取文件大小
                    size = os.path.getsize(file_path)
                    
                    # 从文件名中提取模型名称（去掉扩展名）
                    name, _ = os.path.splitext(filename)
                    
                    models.append({
                        "name": name,
                        "path": file_path,
                        "size": size,
                        "type": "pytorch"
                    })
        
        return models
    
    def list_available_models(self) -> Dict:
        """
        列出所有可下载模型
        
        Returns:
            可下载模型字典
        """
        return self.config.get("available_models", {})
    
    def get_model_info(self, model_name: Optional[str] = None) -> Optional[Dict]:
        """
        获取模型信息
        
        Args:
            model_name: 模型名称，默认为当前模型
            
        Returns:
            模型信息字典
        """
        if model_name is None:
            model_name = self.config.get("current_model")
        
        # 检查模型是否存在
        for model in self.list_models():
            if model["name"] == model_name:
                return model
        
        return None
    
    def select_model(self, model_name: str) -> bool:
        """
        选择模型
        
        Args:
            model_name: 模型名称
            
        Returns:
            是否选择成功
        """
        # 检查模型是否存在
        model_exists = False
        for model in self.list_models():
            if model["name"] == model_name:
                model_exists = True
                break
        
        if not model_exists:
            return False
        
        # 更新当前模型
        self.config["current_model"] = model_name
        return self._save_config(self.config)
    
    def download_model(self, url: Optional[str] = None, model_name: Optional[str] = None) -> Optional[str]:
        """
        下载模型
        
        Args:
            url: 模型下载URL，默认为配置中的URL
            model_name: 模型名称，用于从可用模型列表中获取URL
            
        Returns:
            下载的模型路径
        """
        # 获取可用模型列表
        available_models = self.list_available_models()
        
        # 获取模型URL
        if model_name:
            if model_name in available_models:
                url = available_models[model_name]["url"]
                # 使用模型名称作为文件名
                filename = f"{model_name}.pt"
            else:
                print(f"模型 {model_name} 不在可用模型列表中")
                return None
        else:
            if url is None:
                url = self.config.get("default_model_url")
            # 从URL中提取文件名
            filename = url.split("/")[-1]
        
        # 模型保存路径
        model_path = os.path.join(self.models_dir, filename)
        
        print(f"开始下载模型: {url}")
        print(f"保存路径: {model_path}")
        
        try:
            # 下载模型
            print(f"正在从 {url} 下载模型...")
            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()
            
            # 获取文件大小
            total_size = int(response.headers.get("content-length", 0))
            downloaded_size = 0
            
            # 写入文件
            with open(model_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\r下载进度: {progress:.1f}%", end="")
            
            print("\n模型下载成功")
            
            # 检测模型类型
            model_type = "pytorch"
            if filename.endswith(".onnx"):
                model_type = "onnx"
            elif filename.endswith(".xml"):
                model_type = "openvino"
            
            # 更新配置中的模型列表
            model_name, _ = os.path.splitext(filename)
            self.config["models"][model_name] = {
                "name": model_name,
                "path": model_path,
                "url": url,
                "type": model_type,
                "size": os.path.getsize(model_path),
                "description": available_models.get(model_name, {}).get("description", "")
            }
            self._save_config(self.config)
            
            return model_path
        except requests.exceptions.RequestException as e:
            print(f"下载失败: {e}")
            # 清理失败的下载
            if os.path.exists(model_path):
                os.remove(model_path)
            return None
        except Exception as e:
            print(f"下载过程中发生错误: {e}")
            # 清理失败的下载
            if os.path.exists(model_path):
                os.remove(model_path)
            return None
