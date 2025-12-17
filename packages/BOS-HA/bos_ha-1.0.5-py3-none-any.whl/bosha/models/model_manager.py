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
import time
import concurrent.futures
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
    
    def list_models(self, model_type: Optional[str] = None) -> List[Dict]:
        """
        列出所有可用模型
        
        Args:
            model_type: 模型类型过滤，可选值为 "pytorch", "onnx", "openvino" 或 None
            
        Returns:
            可用模型列表
        """
        models = []
        available_models = self.list_available_models()
        
        # 遍历模型目录
        if os.path.exists(self.models_dir):
            for filename in os.listdir(self.models_dir):
                file_path = os.path.join(self.models_dir, filename)
                if os.path.isfile(file_path):
                    # 获取文件大小
                    size = os.path.getsize(file_path)
                    
                    # 从文件名中提取模型名称（去掉扩展名）
                    name, ext = os.path.splitext(filename)
                    
                    # 检测模型类型
                    model_type_detected = "pytorch"
                    if ext == ".onnx":
                        model_type_detected = "onnx"
                    elif ext == ".xml":
                        model_type_detected = "openvino"
                    
                    # 过滤模型类型
                    if model_type and model_type_detected != model_type:
                        continue
                    
                    # 获取模型详细信息
                    model_info = available_models.get(name, {})
                    
                    models.append({
                        "name": name,
                        "path": file_path,
                        "size": size,
                        "size_human": self._get_human_readable_size(size),
                        "type": model_type_detected,
                        "status": "已下载",
                        "description": model_info.get("description", ""),
                        "arch": model_info.get("arch", "")
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
        
        # 检查模型是否存在于本地
        for model in self.list_models():
            if model["name"] == model_name:
                # 合并配置中的模型信息
                config_info = self.config.get("models", {}).get(model_name, {})
                model.update(config_info)
                return model
        
        # 检查模型是否在可用模型列表中
        available_models = self.list_available_models()
        if model_name in available_models:
            return {
                "name": model_name,
                "status": "未下载",
                "description": available_models[model_name].get("description", ""),
                "arch": available_models[model_name].get("arch", ""),
                "url": available_models[model_name].get("url", ""),
                "type": available_models[model_name].get("type", "")
            }
        
        return None
    
    def list_all_models(self) -> List[Dict]:
        """
        列出所有模型，包括已下载和未下载的
        
        Returns:
            所有模型列表
        """
        all_models = []
        
        # 获取已下载模型
        downloaded_models = self.list_models()
        downloaded_names = {model["name"] for model in downloaded_models}
        
        # 获取所有可下载模型
        available_models = self.list_available_models()
        
        # 合并已下载和可下载模型
        for model_name, model_info in available_models.items():
            if model_name in downloaded_names:
                # 已下载模型
                for model in downloaded_models:
                    if model["name"] == model_name:
                        all_models.append(model)
                        break
            else:
                # 未下载模型
                all_models.append({
                    "name": model_name,
                    "status": "未下载",
                    "description": model_info.get("description", ""),
                    "arch": model_info.get("arch", ""),
                    "url": model_info.get("url", ""),
                    "type": model_info.get("type", "")
                })
        
        return all_models
    
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
    
    def _get_human_readable_size(self, size_bytes: int) -> str:
        """
        将字节大小转换为人类可读格式
        
        Args:
            size_bytes: 字节大小
            
        Returns:
            人类可读的大小字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def download_model(self, url: Optional[str] = None, model_name: Optional[str] = None, force: bool = False) -> Optional[str]:
        """
        下载模型
        
        Args:
            url: 模型下载URL，默认为配置中的URL
            model_name: 模型名称，用于从可用模型列表中获取URL
            force: 是否强制重新下载已存在的模型
            
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
        
        # 检查模型是否已存在
        if os.path.exists(model_path) and not force:
            print(f"模型 {filename} 已存在，跳过下载")
            return model_path
        
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
                            current_size = self._get_human_readable_size(downloaded_size)
                            total_size_human = self._get_human_readable_size(total_size)
                            print(f"\r下载进度: {progress:.1f}% | {current_size} / {total_size_human}", end="")
            
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
                "download_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "description": available_models.get(model_name, {}).get("description", ""),
                "arch": available_models.get(model_name, {}).get("arch", "")
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
    
    def _download_single_model(self, model_name: str, force: bool = False) -> Optional[str]:
        """
        下载单个模型的内部方法，用于并发下载
        
        Args:
            model_name: 模型名称
            force: 是否强制重新下载已存在的模型
            
        Returns:
            成功下载的模型路径，失败返回None
        """
        print(f"\n=== 下载模型: {model_name} ===")
        return self.download_model(model_name=model_name, force=force)
    
    def download_models(self, model_names: List[str], force: bool = False, max_workers: int = 3) -> List[str]:
        """
        下载多个模型（支持并发下载）
        
        Args:
            model_names: 模型名称列表
            force: 是否强制重新下载已存在的模型
            max_workers: 并发下载的最大工作线程数
            
        Returns:
            成功下载的模型路径列表
        """
        downloaded_paths = []
        
        if not model_names:
            return downloaded_paths
        
        # 使用并发下载
        print(f"开始并发下载 {len(model_names)} 个模型，最大工作线程数: {max_workers}")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交下载任务
            future_to_model = {
                executor.submit(self._download_single_model, model_name, force): model_name
                for model_name in model_names
            }
            
            # 获取下载结果
            for future in concurrent.futures.as_completed(future_to_model):
                model_name = future_to_model[future]
                try:
                    model_path = future.result()
                    if model_path:
                        downloaded_paths.append(model_path)
                except Exception as e:
                    print(f"模型 {model_name} 下载失败: {e}")
        
        print(f"\n=== 并发下载完成 ===")
        return downloaded_paths
    
    def download_all(self, force: bool = False, max_workers: int = 3) -> List[str]:
        """
        下载所有可用模型（支持并发下载）
        
        Args:
            force: 是否强制重新下载已存在的模型
            max_workers: 并发下载的最大工作线程数
            
        Returns:
            成功下载的模型路径列表
        """
        # 获取所有可用模型名称
        available_models = self.list_available_models()
        model_names = list(available_models.keys())
        
        print(f"开始下载所有 {len(model_names)} 个可用模型")
        return self.download_models(model_names, force=force, max_workers=max_workers)
    
    def validate_model(self, model_path: str) -> bool:
        """
        验证模型是否有效
        
        Args:
            model_path: 模型路径
            
        Returns:
            模型是否有效的布尔值
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(model_path):
                print(f"模型文件不存在: {model_path}")
                return False
            
            # 检查文件大小
            file_size = os.path.getsize(model_path)
            if file_size < 1024:
                print(f"模型文件太小，可能不完整: {model_path}")
                return False
            
            # 根据文件扩展名进行特定验证
            ext = os.path.splitext(model_path)[1].lower()
            
            if ext == ".pt":
                # PyTorch模型验证
                try:
                    import torch
                    model = torch.load(model_path, map_location="cpu", weights_only=True)
                    print(f"PyTorch模型验证成功: {model_path}")
                    return True
                except Exception as e:
                    print(f"PyTorch模型验证失败: {e}")
                    return False
            elif ext == ".onnx":
                # ONNX模型验证
                try:
                    import onnx
                    model = onnx.load(model_path)
                    onnx.checker.check_model(model)
                    print(f"ONNX模型验证成功: {model_path}")
                    return True
                except Exception as e:
                    print(f"ONNX模型验证失败: {e}")
                    return False
            elif ext == ".xml":
                # OpenVINO模型验证
                try:
                    from openvino.runtime import Core
                    core = Core()
                    model = core.read_model(model_path)
                    print(f"OpenVINO模型验证成功: {model_path}")
                    return True
                except Exception as e:
                    print(f"OpenVINO模型验证失败: {e}")
                    return False
            else:
                # 其他类型模型，只检查文件存在和大小
                print(f"模型类型 {ext} 不支持特定验证，仅检查文件存在和大小")
                return True
        except Exception as e:
            print(f"模型验证失败: {e}")
            return False
    
    def validate_all_models(self) -> List[Dict]:
        """
        验证所有已下载的模型
        
        Returns:
            验证结果列表
        """
        results = []
        downloaded_models = self.list_models()
        
        for model in downloaded_models:
            result = {
                "name": model["name"],
                "path": model["path"],
                "type": model["type"],
                "valid": self.validate_model(model["path"])
            }
            results.append(result)
        
        return results
