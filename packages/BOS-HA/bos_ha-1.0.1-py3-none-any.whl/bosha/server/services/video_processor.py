import numpy as np
import cv2
from typing import Dict, List, Optional
from bosha.server.utils import info, warning, error, exception
from bosha.server.config import settings
from bosha.server.models import HandSignModel

class VideoProcessor:
    """视频处理器类，处理视频流和手语识别"""
    
    def __init__(self):
        """初始化视频处理器"""
        self.model = None
        self.model_loaded = False
        
        # 加载模型
        self.load_model()
    
    def load_model(self):
        """加载手语识别模型"""
        try:
            self.model = HandSignModel(
                model_path=settings.MODEL_PATH,
                confidence_threshold=settings.MODEL_CONFIDENCE_THRESHOLD
            )
            self.model_loaded = True
            info("手语识别模型加载成功")
        except Exception as e:
            exception(f"加载模型失败: {e}")
            self.model_loaded = False
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        处理单帧视频，进行手语识别
        
        Args:
            frame: 输入帧，格式为 (高度, 宽度, 通道)
            
        Returns:
            dict: 识别结果
        """
        try:
            if not self.model_loaded:
                return {
                    "success": False,
                    "message": "模型未加载",
                    "predicted_class": "",
                    "confidence": 0.0
                }
            
            # 使用模型进行预测
            result = self.model.predict(frame)
            return result
            
        except Exception as e:
            exception(f"处理帧失败: {e}")
            return {
                "success": False,
                "message": f"处理帧失败: {str(e)}",
                "predicted_class": "",
                "confidence": 0.0
            }
    
    def process_frames(self, frames: List[np.ndarray]) -> List[Dict]:
        """
        批量处理视频帧
        
        Args:
            frames: 视频帧列表
            
        Returns:
            list: 识别结果列表
        """
        results = []
        for frame in frames:
            result = self.process_frame(frame)
            results.append(result)
        return results
    
    def draw_result(self, frame: np.ndarray, result: Dict) -> np.ndarray:
        """
        在视频帧上绘制识别结果
        
        Args:
            frame: 输入帧
            result: 识别结果
            
        Returns:
            np.ndarray: 绘制了结果的帧
        """
        try:
            output_frame = frame.copy()
            
            if not result["success"]:
                return output_frame
            
            # 绘制手部边界框
            if result["hand_detected"] and result["hand_bbox"]:
                x, y, w, h = result["hand_bbox"]
                cv2.rectangle(output_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            # 绘制识别结果
            if result["predicted_class"]:
                text = f"{result['predicted_class']}: {result['confidence']:.2f}"
                cv2.putText(
                    output_frame,
                    text,
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )
            
            return output_frame
            
        except Exception as e:
            exception(f"绘制结果失败: {e}")
            return frame
    
    def get_model_info(self) -> Dict:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        if not self.model_loaded:
            return {
                "loaded": False,
                "message": "模型未加载"
            }
        
        try:
            return self.model.get_model_info()
        except Exception as e:
            exception(f"获取模型信息失败: {e}")
            return {
                "loaded": False,
                "message": f"获取模型信息失败: {str(e)}"
            }
    
    def update_model_threshold(self, threshold: float):
        """
        更新模型置信度阈值
        
        Args:
            threshold: 新的置信度阈值
        """
        try:
            if self.model_loaded:
                self.model.update_confidence_threshold(threshold)
                info(f"模型置信度阈值已更新为: {threshold}")
        except Exception as e:
            exception(f"更新模型阈值失败: {e}")
    
    def is_model_loaded(self) -> bool:
        """
        检查模型是否已加载
        
        Returns:
            bool: 模型加载状态
        """
        return self.model_loaded
    
    def release(self):
        """释放资源"""
        try:
            # 释放模型资源
            self.model = None
            self.model_loaded = False
            info("视频处理器资源已释放")
        except Exception as e:
            exception(f"释放资源失败: {e}")
