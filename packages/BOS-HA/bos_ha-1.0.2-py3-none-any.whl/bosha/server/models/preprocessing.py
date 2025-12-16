import cv2
import numpy as np
from typing import Tuple, Optional

class VideoPreprocessor:
    """视频帧预处理类"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        """
        初始化预处理器
        
        Args:
            target_size: 目标尺寸 (宽度, 高度)
        """
        self.target_size = target_size
        
        # 加载人脸检测级联分类器
        self.face_cascade = self._load_face_cascade()
    
    def _load_face_cascade(self):
        """
        加载人脸检测级联分类器
        
        Returns:
            cv2.CascadeClassifier: 人脸检测分类器
        """
        try:
            # 使用OpenCV内置的Haar级联分类器
            face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(face_cascade_path)
            if face_cascade.empty():
                print("无法加载人脸检测分类器")
                return None
            return face_cascade
        except Exception as e:
            print(f"加载人脸检测分类器失败: {e}")
            return None
    
    def detect_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        检测人脸
        
        Args:
            frame: 输入帧
            
        Returns:
            tuple: 人脸边界框 (x, y, w, h) 或 None
        """
        try:
            if self.face_cascade is None:
                return None
            
            # 转换为灰度图
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            
            # 检测人脸
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            # 返回第一个检测到的人脸
            if len(faces) > 0:
                return tuple(faces[0])
            return None
            
        except Exception as e:
            print(f"人脸检测失败: {e}")
            return None
    
    def preprocess_frame(self, frame: np.ndarray) -> Tuple[np.ndarray, Optional[dict]]:
        """
        预处理单帧图像
        
        Args:
            frame: 输入帧，格式为 (高度, 宽度, 通道)
            
        Returns:
            tuple: (预处理后的帧, 预处理元数据)
        """
        try:
            # 1. 转换为RGB格式
            if frame.shape[-1] == 4:  # RGBA格式
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
            elif frame.shape[-1] == 1:  # 灰度图
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            
            # 2. 调整尺寸
            resized_frame = cv2.resize(frame, self.target_size)
            
            # 3. 归一化
            normalized_frame = resized_frame / 255.0
            
            # 4. 调整通道顺序 (HWC -> CHW)
            if normalized_frame.shape[-1] == 3:
                normalized_frame = normalized_frame.transpose(2, 0, 1)
            
            # 5. 转换为float32
            normalized_frame = normalized_frame.astype(np.float32)
            
            # 6. 生成元数据
            metadata = {
                "original_shape": frame.shape,
                "resized_shape": resized_frame.shape,
                "target_size": self.target_size
            }
            
            return normalized_frame, metadata
            
        except Exception as e:
            print(f"预处理帧失败: {e}")
            return np.zeros((3, *self.target_size), dtype=np.float32), None
    
    def detect_hand(self, frame: np.ndarray) -> Optional[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        检测手部区域，确保不包含人脸
        
        Args:
            frame: 输入帧
            
        Returns:
            tuple: (手部区域图像, 边界框坐标) 或 None
        """
        try:
            # 1. 快速人脸检测（降低检测频率）
            if np.random.rand() < 0.3:  # 30%概率检测人脸，减少计算量
                face_bbox = self.detect_face(frame)
                if face_bbox is not None:
                    # print("检测到人脸，跳过此帧")
                    return None
            
            # 2. 快速肤色检测
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            
            # 扩大肤色范围，提高检测率
            lower_skin = np.array([0, 15, 60], dtype=np.uint8)
            upper_skin = np.array([30, 255, 255], dtype=np.uint8)
            
            # 肤色掩码
            mask = cv2.inRange(hsv, lower_skin, upper_skin)
            
            # 简化形态学操作，减少计算量
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
            
            # 寻找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            # 找到最大的轮廓
            max_contour = max(contours, key=cv2.contourArea)
            
            # 计算边界框
            x, y, w, h = cv2.boundingRect(max_contour)
            
            # 调整最小尺寸，提高检测率
            if w < 40 or h < 40:  # 最小尺寸调整为40x40
                return None
            
            # 简化边界框扩展
            margin = 15
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(frame.shape[1] - x, w + 2 * margin)
            h = min(frame.shape[0] - y, h + 2 * margin)
            
            # 降低再次检测人脸的频率
            if np.random.rand() < 0.2:  # 20%概率再次检测
                hand_region = frame[y:y+h, x:x+w]
                if self.detect_face(hand_region) is not None:
                    # print("手部区域包含人脸，跳过此帧")
                    return None
            
            # 确保手部区域有足够的皮肤像素
            hand_region = frame[y:y+h, x:x+w]
            hand_hsv = cv2.cvtColor(hand_region, cv2.COLOR_RGB2HSV)
            skin_pixels = cv2.inRange(hand_hsv, lower_skin, upper_skin)
            skin_ratio = np.sum(skin_pixels > 0) / (hand_region.shape[0] * hand_region.shape[1])
            
            # 提高检测率，降低皮肤比例阈值
            if skin_ratio > 0.2:  # 皮肤比例调整为20%
                return hand_region, (x, y, w, h)
            
            return None
            
        except Exception as e:
            # 简化错误处理，减少日志输出
            return None
    
    def normalize_landmarks(self, landmarks: np.ndarray, frame_size: Tuple[int, int]) -> np.ndarray:
        """
        归一化关键点坐标
        
        Args:
            landmarks: 关键点坐标，格式为 (N, 2)
            frame_size: 帧尺寸 (宽度, 高度)
            
        Returns:
            np.ndarray: 归一化后的关键点坐标
        """
        try:
            # 将坐标归一化到 [0, 1] 范围
            normalized = landmarks.copy()
            normalized[:, 0] /= frame_size[0]  # x坐标归一化
            normalized[:, 1] /= frame_size[1]  # y坐标归一化
            
            return normalized
            
        except Exception as e:
            print(f"归一化关键点失败: {e}")
            return landmarks
    
    def augment_frame(self, frame: np.ndarray, rotation_range: int = 10, zoom_range: float = 0.1) -> np.ndarray:
        """
        数据增强
        
        Args:
            frame: 输入帧
            rotation_range: 旋转角度范围
            zoom_range: 缩放范围
            
        Returns:
            np.ndarray: 增强后的帧
        """
        try:
            h, w = frame.shape[:2]
            
            # 随机旋转
            angle = np.random.uniform(-rotation_range, rotation_range)
            M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1.0)
            frame = cv2.warpAffine(frame, M, (w, h))
            
            # 随机缩放
            zoom = np.random.uniform(1 - zoom_range, 1 + zoom_range)
            M = cv2.getRotationMatrix2D((w/2, h/2), 0, zoom)
            frame = cv2.warpAffine(frame, M, (w, h))
            
            return frame
            
        except Exception as e:
            print(f"数据增强失败: {e}")
            return frame