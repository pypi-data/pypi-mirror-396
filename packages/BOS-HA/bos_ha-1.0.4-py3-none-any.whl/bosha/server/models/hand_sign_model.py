import numpy as np
from typing import Tuple, List, Dict, Optional
from .preprocessing import VideoPreprocessor
import torch
from transformers import AutoImageProcessor
import os

class HandSignModel:
    """手语识别模型封装类"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.7):
        """
        初始化模型
        
        Args:
            model_path: 模型文件路径
            confidence_threshold: 置信度阈值
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.preprocessor = VideoPreprocessor(target_size=(224, 224))
        self.model = None
        self.image_processor = None
        # 扩展手语类别，包含更多常用词汇
        self.class_names = [
            # 问候类
            "你好", "谢谢", "再见", "早上好", "晚上好", "欢迎", "请问", "没关系", "不客气", "久仰", 
            # 情感类
            "我爱你", "喜欢", "生气", "悲伤", "开心", "惊讶", "感动", "害怕", "骄傲", "失望", 
            # 回答类
            "是", "否", "不知道", "可能", "当然", "抱歉", "是的", "不是", "也许", "一定", 
            # 请求类
            "请", "帮助", "需要", "想要", "给我", "借我", "请问", "麻烦", "拜托", "让一下", 
            # 身份类
            "我", "你", "他", "她", "我们", "你们", "他们", "老师", "医生", "学生", 
            # 生活类
            "家", "学校", "工作", "医院", "商店", "公园", "餐厅", "银行", "超市", "邮局", 
            # 物品类
            "食物", "水", "饮料", "衣服", "鞋子", "帽子", "手机", "电脑", "书包", "书本", 
            "笔", "纸", "杯子", "筷子", "勺子", "碗", "盘子", "桌子", "椅子", "床", 
            # 动作类
            "走", "跑", "坐", "站", "吃", "喝", "看", "听", "说", "写", 
            "读", "画", "唱", "跳", "睡", "醒", "来", "去", "上", "下", 
            # 数量类
            "一", "二", "三", "四", "五", "六", "七", "八", "九", "十", 
            "百", "千", "万", "零", "半", "两", "多", "少", "第一", "第二", 
            # 其他
            "时间", "今天", "明天", "昨天", "星期", "月份", "年", "钱", "价格", "颜色", 
            "红色", "蓝色", "绿色", "黄色", "黑色", "白色", "紫色", "橙色", "粉色", "灰色", 
            "大", "小", "长", "短", "高", "矮", "胖", "瘦", "热", "冷", 
            "早", "晚", "快", "慢", "好", "坏", "对", "错", "新", "旧"
        ]
        
        # 加载模型
        self.load_model()
    
    def load_model(self, model_name=None):
        """
        加载模型
        
        Args:
            model_name: 模型名称（可选），不提供则使用初始化时的模型路径
        """
        try:
            # 动态调整模型路径
            if model_name:
                # 获取模型目录
                model_dir = os.path.dirname(self.model_path)
                # 构建新的模型路径
                self.model_path = os.path.join(model_dir, f"{model_name}.pt")
            
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                print(f"模型文件不存在: {self.model_path}")
                print("请先下载模型: bosha-model download --name <model_name>")
                self.model = None
                self.image_processor = None
                return
            
            # 检查模型文件大小
            if os.path.getsize(self.model_path) < 1024:
                print(f"模型文件太小，可能下载不完整: {self.model_path}")
                print("请重新下载模型: bosha-model download --name <model_name>")
                self.model = None
                self.image_processor = None
                return
            
            # 加载PyTorch模型
            self.model = torch.load(self.model_path, weights_only=False)
            self.model.eval()  # 设置为评估模式
            
            # 加载图像处理器
            model_dir = os.path.dirname(self.model_path)
            try:
                self.image_processor = AutoImageProcessor.from_pretrained(model_dir)
            except Exception as e:
                print(f"加载图像处理器失败，使用默认配置: {e}")
                self.image_processor = AutoImageProcessor.from_pretrained("microsoft/resnet-50")
            
            print(f"模型加载成功: {self.model_path}")
            print(f"图像处理器加载成功")
            
        except Exception as e:
            print(f"加载模型失败: {e}")
            print("请检查模型文件是否完整，或尝试重新下载")
            self.model = None
            self.image_processor = None
    
    def predict(self, frame: np.ndarray) -> Dict:
        """
        对手语进行预测
        
        Args:
            frame: 输入帧，格式为 (高度, 宽度, 通道)
            
        Returns:
            dict: 预测结果，包含类别、置信度等信息
        """
        try:
            if not self.model or not self.image_processor:
                return {
                    "success": False,
                    "message": "模型未加载，请先下载并选择有效的模型。使用命令: bosha-model download --name <model_name> 下载模型",
                    "predicted_class": "",
                    "confidence": 0.0
                }
            
            # 1. 手部检测
            hand_result = self.preprocessor.detect_hand(frame)
            if not hand_result:
                # 重置缓存
                self.result_cache = {
                    "last_predicted_class": "",
                    "last_confidence": 0.0,
                    "last_bbox": None,
                    "cache_count": 0,
                    "max_cache_count": 3
                }
                return {
                    "success": False,
                    "message": "未检测到手部",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": False
                }
            
            hand_region, bbox = hand_result
            
            # 2. 快速图像预处理
            inputs = self.image_processor(
                images=hand_region,
                return_tensors="pt",
                do_resize=True,
                size=(224, 224),
                do_center_crop=True,
                do_normalize=True
            )
            
            # 3. 模型推理（简化）
            with torch.no_grad():
                # 使用更高效的推理方式
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.nn.functional.softmax(logits, dim=1)
                confidence, predicted_idx = torch.max(probabilities, dim=1)
                
                confidence = confidence.item()
                predicted_idx = predicted_idx.item()
            
            # 4. 映射到手语类别
            predicted_class = self.class_names[predicted_idx % len(self.class_names)] if confidence >= self.confidence_threshold else ""
            
            # 5. 使用结果缓存，提高稳定性
            if predicted_class == self.result_cache["last_predicted_class"] and confidence >= self.confidence_threshold:
                # 连续相同结果，增加缓存计数
                self.result_cache["cache_count"] += 1
            else:
                # 新结果，重置缓存计数
                self.result_cache = {
                    "last_predicted_class": predicted_class,
                    "last_confidence": confidence,
                    "last_bbox": bbox,
                    "cache_count": 1,
                    "max_cache_count": 3
                }
            
            # 6. 只有连续多次相同结果才输出，提高稳定性
            if self.result_cache["cache_count"] < self.result_cache["max_cache_count"]:
                return {
                    "success": True,
                    "message": "识别中，等待稳定结果",
                    "predicted_class": "",
                    "confidence": confidence,
                    "hand_detected": True,
                    "hand_bbox": bbox,
                    "class_names": self.class_names
                }
            
            # 7. 生成结果
            result = {
                "success": True,
                "message": "识别成功",
                "predicted_class": predicted_class,
                "confidence": float(confidence),
                "hand_detected": True,
                "hand_bbox": bbox,
                "class_names": self.class_names
            }
            
            return result
            
        except Exception as e:
            # 简化错误处理，减少日志输出
            return {
                "success": False,
                "message": f"预测失败",
                "predicted_class": "",
                "confidence": 0.0,
                "hand_detected": False
            }
    
    def batch_predict(self, frames: List[np.ndarray]) -> List[Dict]:
        """
        批量预测
        
        Args:
            frames: 输入帧列表
            
        Returns:
            list: 预测结果列表
        """
        results = []
        for frame in frames:
            result = self.predict(frame)
            results.append(result)
        return results
    
    def get_model_info(self) -> Dict:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        return {
            "model_path": self.model_path,
            "confidence_threshold": self.confidence_threshold,
            "class_count": len(self.class_names),
            "class_names": self.class_names,
            "model_loaded": self.model is not None,
            "preprocessor": {
                "target_size": self.preprocessor.target_size
            }
        }
    
    def update_confidence_threshold(self, threshold: float):
        """
        更新置信度阈值
        
        Args:
            threshold: 新的置信度阈值
        """
        if 0.0 <= threshold <= 1.0:
            self.confidence_threshold = threshold
            print(f"置信度阈值已更新为: {threshold}")
        else:
            print("置信度阈值必须在 [0.0, 1.0] 范围内")