import numpy as np
from typing import Dict, Any, List
import os
import sys
import time
from .preprocessing import VideoPreprocessor

class OpenVinoHandSignModel:
    """OpenVINO手语识别模型封装类"""
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.7):
        """
        初始化OpenVINO模型
        
        Args:
            model_path: 模型文件路径（.xml文件）
            confidence_threshold: 置信度阈值
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.preprocessor = VideoPreprocessor(target_size=(224, 224))
        self.model = None
        self.compiled_model = None
        self.infer_request = None
        self.input_tensor_name = None
        self.output_tensor_name = None
        self.core = None
        
        # 扩展手语类别，与原有模型保持一致
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
            "早", "晚", "快", "慢", "好", "坏", "对", "错", "新", "旧",
            # 扩展类别
            "朋友", "家人", "父母", "兄弟", "姐妹", "孩子", "老人", "年轻人", "男人", "女人",
            "水果", "蔬菜", "肉类", "米饭", "面条", "面包", "牛奶", "果汁", "咖啡", "茶",
            "汽车", "火车", "飞机", "地铁", "公交", "自行车", "步行", "驾驶", "乘坐", "到达",
            "开始", "结束", "继续", "停止", "等待", "出发", "返回", "离开", "到达", "停留"
        ]
        
        # 添加结果缓存，提高稳定性
        self.result_cache = {
            "last_predicted_class": "",
            "last_confidence": 0.0,
            "last_bbox": None,
            "cache_count": 0,
            "max_cache_count": 3  # 连续3次相同结果才输出
        }
        
        # 加载模型
        self.load_model()
    
    def load_model(self, model_name=None):
        """
        加载OpenVINO模型
        
        Args:
            model_name: 模型名称（可选），不提供则使用初始化时的模型路径
        """
        try:
            # 动态调整模型路径
            if model_name:
                # 获取模型目录
                model_dir = os.path.dirname(self.model_path)
                # 构建新的模型路径
                self.model_path = os.path.join(model_dir, f"{model_name}.xml")
            
            # 检查模型文件是否存在
            if not os.path.exists(self.model_path):
                print(f"OpenVINO模型文件不存在: {self.model_path}")
                print("请确保模型文件已正确下载或转换")
                print("使用命令: bosha-model download --name <model_name> 下载模型")
                self._release_resources()
                return False
            
            # 检查模型文件大小
            if os.path.getsize(self.model_path) < 1024:
                print(f"OpenVINO模型文件太小，可能下载不完整: {self.model_path}")
                print("请重新下载模型或检查模型文件")
                self._release_resources()
                return False
            
            # 释放旧资源
            self._release_resources()
            
            # 检查是否已安装OpenVINO
            try:
                from openvino.runtime import Core
                self.core = Core()
            except ImportError as e:
                print(f"未安装OpenVINO: {e}")
                print("请使用命令: pip install openvino openvino-dev 安装OpenVINO")
                self.model = None
                self.compiled_model = None
                self.infer_request = None
                return False
            except Exception as e:
                print(f"导入OpenVINO时发生错误: {e}")
                print("请检查OpenVINO安装是否正确")
                self.model = None
                self.compiled_model = None
                self.infer_request = None
                return False
            
            # 尝试加载模型（最多重试3次）
            max_retries = 3
            for i in range(max_retries):
                try:
                    print(f"正在加载OpenVINO模型 (尝试 {i+1}/{max_retries}): {self.model_path}")
                    self.model = self.core.read_model(self.model_path)
                    break
                except Exception as e:
                    print(f"加载模型失败 (尝试 {i+1}/{max_retries}): {e}")
                    if i == max_retries - 1:
                        print(f"多次尝试加载模型失败: {self.model_path}")
                        self.model = None
                        self.compiled_model = None
                        self.infer_request = None
                        return False
                    time.sleep(1)  # 等待1秒后重试
            
            # 尝试编译模型，支持设备故障转移
            try:
                # 获取可用设备列表
                available_devices = self.core.available_devices
                print(f"可用设备: {available_devices}")
                
                # 智能设备排序（优先使用GPU，然后CPU）
                device_priority = {
                    "GPU": 3,    # 通用GPU
                    "GPU.0": 3,  # 特定GPU设备
                    "GPU.1": 3,
                    "CPU": 1,    # CPU作为 fallback
                    "AUTO": 2    # AUTO设备
                }
                
                # 按优先级排序设备
                sorted_devices = sorted(
                    available_devices,
                    key=lambda d: max((v for k, v in device_priority.items() if k in d), default=0),
                    reverse=True
                )
                
                print(f"设备优先级排序: {sorted_devices}")
                
                # 尝试在每个设备上编译模型，直到成功
                compilation_succeeded = False
                for target_device in sorted_devices:
                    try:
                        print(f"尝试使用设备: {target_device} 编译模型...")
                        self.compiled_model = self.core.compile_model(self.model, target_device)
                        print(f"使用设备: {target_device} 编译模型成功")
                        compilation_succeeded = True
                        break
                    except Exception as e:
                        print(f"使用设备 {target_device} 编译模型失败: {e}")
                        continue
                
                # 如果所有设备都失败，尝试使用AUTO设备
                if not compilation_succeeded and "AUTO" in self.core.available_devices:
                    try:
                        print("尝试使用 AUTO 设备编译模型...")
                        self.compiled_model = self.core.compile_model(self.model, "AUTO")
                        print("使用 AUTO 设备编译模型成功")
                        compilation_succeeded = True
                    except Exception as e:
                        print(f"使用 AUTO 设备编译模型失败: {e}")
                
                if not compilation_succeeded:
                    print(f"所有设备编译模型都失败: {self.model_path}")
                    self.model = None
                    self.compiled_model = None
                    self.infer_request = None
                    return False
            except Exception as e:
                print(f"模型编译过程中发生错误: {e}")
                self.model = None
                self.compiled_model = None
                self.infer_request = None
                return False
            
            # 获取输入和输出张量名称
            try:
                self.input_tensor_name = next(iter(self.compiled_model.inputs))
                self.output_tensor_name = next(iter(self.compiled_model.outputs))
            except Exception as e:
                print(f"获取张量名称失败: {e}")
                self.model = None
                self.compiled_model = None
                self.infer_request = None
                return False
            
            # 创建推理请求
            try:
                self.infer_request = self.compiled_model.create_infer_request()
            except Exception as e:
                print(f"创建推理请求失败: {e}")
                self.model = None
                self.compiled_model = None
                self.infer_request = None
                return False
            
            print(f"OpenVINO模型加载成功: {self.model_path}")
            print(f"使用设备: {target_device}")
            print(f"输入张量: {self.input_tensor_name}")
            print(f"输出张量: {self.output_tensor_name}")
            return True
            
        except Exception as e:
            print(f"加载OpenVINO模型失败: {e}")
            print("请检查模型文件是否完整，或尝试重新下载")
            self.model = None
            self.compiled_model = None
            self.infer_request = None
            return False
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        预处理输入图像
        
        Args:
            image: 输入图像，格式为 (高度, 宽度, 通道)
            
        Returns:
            np.ndarray: 预处理后的图像，格式为 (1, 通道, 高度, 宽度)
        """
        try:
            # 调整图像大小
            resized_image = self.preprocessor.resize(image)
            
            # 转换为RGB
            if resized_image.shape[-1] == 4:
                resized_image = resized_image[..., :3]  # 移除Alpha通道
            
            # 转换为(通道, 高度, 宽度)格式
            input_tensor = resized_image.transpose(2, 0, 1)
            
            # 添加batch维度
            input_tensor = np.expand_dims(input_tensor, axis=0)
            
            # 归一化
            input_tensor = input_tensor.astype(np.float32) / 255.0
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32).reshape((3, 1, 1))
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32).reshape((3, 1, 1))
            input_tensor = (input_tensor - mean) / std
            
            return input_tensor
        except Exception as e:
            print(f"图像预处理失败: {e}")
            return None
    
    def __init__(self, model_path: str, confidence_threshold: float = 0.7):
        """
        初始化OpenVINO模型
        
        Args:
            model_path: 模型文件路径（.xml文件）
            confidence_threshold: 置信度阈值
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.preprocessor = VideoPreprocessor(target_size=(224, 224))
        self.model = None
        self.compiled_model = None
        self.infer_request = None
        self.input_tensor_name = None
        self.output_tensor_name = None
        self.core = None
        
        # 扩展手语类别，与原有模型保持一致
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
            "早", "晚", "快", "慢", "好", "坏", "对", "错", "新", "旧",
            # 扩展类别
            "朋友", "家人", "父母", "兄弟", "姐妹", "孩子", "老人", "年轻人", "男人", "女人",
            "水果", "蔬菜", "肉类", "米饭", "面条", "面包", "牛奶", "果汁", "咖啡", "茶",
            "汽车", "火车", "飞机", "地铁", "公交", "自行车", "步行", "驾驶", "乘坐", "到达",
            "开始", "结束", "继续", "停止", "等待", "出发", "返回", "离开", "到达", "停留"
        ]
        
        # 添加结果缓存，提高稳定性
        self.result_cache = {
            "last_predicted_class": "",
            "last_confidence": 0.0,
            "last_bbox": None,
            "cache_count": 0,
            "max_cache_count": 3  # 连续3次相同结果才输出
        }
        
        # 添加序列识别支持
        self.sequence_buffer = []  # 存储连续帧的识别结果
        self.sequence_length = 5  # 序列长度，使用最近5帧的结果
        self.sequence_weights = [0.1, 0.15, 0.2, 0.25, 0.3]  # 权重，越新的帧权重越高
        
        # 加载模型
        self.load_model()
    
    def predict(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        对手语进行预测
        
        Args:
            frame: 输入帧，格式为 (高度, 宽度, 通道)
            
        Returns:
            dict: 预测结果，包含类别、置信度等信息
        """
        try:
            if not self.model or not self.compiled_model or not self.infer_request:
                return {
                    "success": False,
                    "message": "OpenVINO模型未加载，请先下载并选择有效的模型",
                    "predicted_class": "",
                    "confidence": 0.0
                }
            
            # 1. 手部检测
            hand_result = self.preprocessor.detect_hand(frame)
            if not hand_result:
                # 重置缓存和序列缓冲区
                self.result_cache = {
                    "last_predicted_class": "",
                    "last_confidence": 0.0,
                    "last_bbox": None,
                    "cache_count": 0,
                    "max_cache_count": 3
                }
                self.sequence_buffer = []
                return {
                    "success": False,
                    "message": "未检测到手部",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": False
                }
            
            hand_region, bbox = hand_result
            
            # 2. 图像预处理
            input_tensor = self.preprocess_image(hand_region)
            if input_tensor is None:
                return {
                    "success": False,
                    "message": "图像预处理失败",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": True
                }
            
            # 3. 真实模型推理
            inference_attempts = 0
            max_inference_attempts = 2  # 最多尝试2次推理（包括模型重载）
            
            while inference_attempts < max_inference_attempts:
                try:
                    self.infer_request.infer({self.input_tensor_name: input_tensor})
                    # 4. 获取推理结果
                    output = self.infer_request.get_output_tensor(self.output_tensor_name).data
                    # 5. 后处理结果
                    probabilities = softmax(output[0])
                    confidence = np.max(probabilities)
                    predicted_idx = np.argmax(probabilities)
                    break  # 推理成功，跳出循环
                except Exception as e:
                    inference_attempts += 1
                    print(f"推理过程中发生错误 (尝试 {inference_attempts}/{max_inference_attempts}): {e}")
                    
                    if inference_attempts < max_inference_attempts:
                        # 尝试重新加载模型
                        print("尝试重新加载模型...")
                        if self.load_model():
                            print("模型重新加载成功，继续推理")
                        else:
                            print("模型重新加载失败，无法继续推理")
                            return {
                                "success": False,
                                "message": "模型重新加载失败",
                                "predicted_class": "",
                                "confidence": 0.0,
                                "hand_detected": True
                            }
                    else:
                        # 所有尝试都失败
                        return {
                            "success": False,
                            "message": f"推理失败: {str(e)}",
                            "predicted_class": "",
                            "confidence": 0.0,
                            "hand_detected": True
                        }
            
            # 6. 添加到序列缓冲区
            self.sequence_buffer.append({
                "probabilities": probabilities,
                "confidence": confidence,
                "predicted_idx": predicted_idx
            })
            
            # 保持序列缓冲区大小
            if len(self.sequence_buffer) > self.sequence_length:
                self.sequence_buffer = self.sequence_buffer[-self.sequence_length:]
            
            # 7. 序列融合：使用加权平均融合连续帧的概率
            final_probabilities = self._fuse_sequence_probabilities()
            final_confidence = np.max(final_probabilities)
            final_predicted_idx = np.argmax(final_probabilities)
            
            # 8. 映射到类别名称
            predicted_class = self.class_names[final_predicted_idx % len(self.class_names)] if final_confidence >= self.confidence_threshold else ""
            
            # 9. 使用结果缓存，提高稳定性
            if predicted_class == self.result_cache["last_predicted_class"] and final_confidence >= self.confidence_threshold:
                # 连续相同结果，增加缓存计数
                self.result_cache["cache_count"] += 1
            else:
                # 新结果，重置缓存计数
                self.result_cache = {
                    "last_predicted_class": predicted_class,
                    "last_confidence": final_confidence,
                    "last_bbox": bbox,
                    "cache_count": 1,
                    "max_cache_count": 3
                }
            
            # 10. 只有连续多次相同结果才输出，提高稳定性
            if self.result_cache["cache_count"] < self.result_cache["max_cache_count"]:
                return {
                    "success": True,
                    "message": "识别中，等待稳定结果",
                    "predicted_class": "",
                    "confidence": float(final_confidence),
                    "hand_detected": True,
                    "hand_bbox": bbox,
                    "class_names": self.class_names
                }
            
            # 11. 生成结果
            result = {
                "success": True,
                "message": "识别成功",
                "predicted_class": predicted_class,
                "confidence": float(final_confidence),
                "hand_detected": True,
                "hand_bbox": bbox,
                "class_names": self.class_names,
                "sequence_length": len(self.sequence_buffer)  # 添加序列长度信息
            }
            
            return result
            
        except Exception as e:
            # 简化错误处理，减少日志输出
            return {
                "success": False,
                "message": f"预测失败: {e}",
                "predicted_class": "",
                "confidence": 0.0,
                "hand_detected": False
            }
    
    def predict_batch(self, frames: List[np.ndarray]) -> List[Dict[str, Any]]:
        """
        批量预测手语
        
        Args:
            frames: 输入帧列表，每个帧格式为 (高度, 宽度, 通道)
            
        Returns:
            list: 预测结果列表，每个结果包含类别、置信度等信息
        """
        results = []
        
        # 批量预处理
        processed_frames = []
        hand_detections = []
        
        # 1. 预处理所有帧
        for frame in frames:
            # 手部检测
            hand_result = self.preprocessor.detect_hand(frame)
            if not hand_result:
                hand_detections.append(None)
                processed_frames.append(None)
            else:
                hand_region, bbox = hand_result
                # 图像预处理
                input_tensor = self.preprocess_image(hand_region)
                hand_detections.append((input_tensor, bbox))
                processed_frames.append(input_tensor)
        
        # 2. 过滤无效帧
        valid_indices = [i for i, frame in enumerate(processed_frames) if frame is not None]
        valid_frames = [processed_frames[i] for i in valid_indices]
        
        if not valid_frames:
            # 所有帧都无效
            for _ in frames:
                results.append({
                    "success": False,
                    "message": "未检测到手部",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": False
                })
            return results
        
        # 3. 批量推理
        try:
            # 合并为一个批量输入
            batch_input = np.concatenate(valid_frames, axis=0)
            
            # 执行批量推理
            self.infer_request.infer({self.input_tensor_name: batch_input})
            
            # 获取批量输出
            outputs = self.infer_request.get_output_tensor(self.output_tensor_name).data
        except Exception as e:
            print(f"批量推理失败: {e}")
            # 回退到单帧推理
            for frame in frames:
                results.append(self.predict(frame))
            return results
        
        # 4. 处理批量结果
        result_index = 0
        for i in range(len(frames)):
            if i not in valid_indices:
                # 无效帧
                results.append({
                    "success": False,
                    "message": "未检测到手部",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": False
                })
            else:
                # 处理有效帧结果
                output = outputs[result_index]
                probabilities = softmax(output)
                confidence = np.max(probabilities)
                predicted_idx = np.argmax(probabilities)
                
                predicted_class = self.class_names[predicted_idx % len(self.class_names)] if confidence >= self.confidence_threshold else ""
                _, bbox = hand_detections[i]
                
                results.append({
                    "success": True,
                    "message": "识别成功",
                    "predicted_class": predicted_class,
                    "confidence": float(confidence),
                    "hand_detected": True,
                    "hand_bbox": bbox,
                    "class_names": self.class_names
                })
                result_index += 1
        
        return results
    
    def _fuse_sequence_probabilities(self) -> np.ndarray:
        """
        融合序列中多个帧的概率
        
        Returns:
            np.ndarray: 融合后的概率分布
        """
        if not self.sequence_buffer:
            return np.zeros(len(self.class_names))
        
        # 调整权重长度，确保与序列长度匹配
        current_length = len(self.sequence_buffer)
        if current_length < self.sequence_length:
            # 使用前current_length个权重
            weights = self.sequence_weights[-current_length:]
            # 归一化权重
            weights = np.array(weights) / np.sum(weights)
        else:
            weights = np.array(self.sequence_weights) / np.sum(self.sequence_weights)
        
        # 初始化融合后的概率
        fused_probabilities = np.zeros_like(self.sequence_buffer[0]["probabilities"])
        
        # 加权平均融合
        for i, result in enumerate(self.sequence_buffer):
            fused_probabilities += weights[i] * result["probabilities"]
        
        return fused_probabilities
    
    def predict_sequence(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """
        对连续帧序列进行预测，实现真正的序列融合
        
        Args:
            frames: 输入帧列表，格式为 (高度, 宽度, 通道)
            
        Returns:
            dict: 预测结果，包含类别、置信度等信息
        """
        if not frames:
            return {
                "success": False,
                "message": "输入帧列表为空",
                "predicted_class": "",
                "confidence": 0.0,
                "hand_detected": False
            }
        
        # 重置序列缓冲区，专门用于此序列预测
        original_buffer = self.sequence_buffer.copy()
        self.sequence_buffer = []
        
        try:
            # 对每个帧进行预测，累积到序列缓冲区
            all_predictions = []
            for frame in frames:
                result = self.predict(frame)
                all_predictions.append(result)
            
            # 过滤成功的结果
            successful_results = [r for r in all_predictions if r["success"] and r["hand_detected"]]
            
            if not successful_results:
                return {
                    "success": False,
                    "message": "未检测到手部",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": False
                }
            
            # 提取每个帧的预测类别
            predicted_classes = [r["predicted_class"] for r in successful_results if r["predicted_class"]]
            
            if not predicted_classes:
                return {
                    "success": False,
                    "message": "未识别到有效手语",
                    "predicted_class": "",
                    "confidence": 0.0,
                    "hand_detected": True
                }
            
            # 计算每个类别的出现频率
            from collections import Counter
            class_counter = Counter(predicted_classes)
            
            # 计算加权频率，考虑时间权重（越后面的帧权重越高）
            weighted_counter = Counter()
            total_weight = sum(range(1, len(predicted_classes) + 1))
            for i, cls in enumerate(predicted_classes):
                weight = (i + 1) / total_weight
                weighted_counter[cls] += weight
            
            # 获取最频繁的类别
            final_class = weighted_counter.most_common(1)[0][0]
            
            # 计算平均置信度
            avg_confidence = np.mean([r["confidence"] for r in successful_results if r["predicted_class"] == final_class])
            
            # 生成最终结果
            return {
                "success": True,
                "message": "序列识别成功",
                "predicted_class": final_class,
                "confidence": float(avg_confidence),
                "hand_detected": True,
                "sequence_length": len(successful_results),
                "all_predictions": predicted_classes,
                "class_distribution": dict(class_counter)
            }
        finally:
            # 恢复原始序列缓冲区
            self.sequence_buffer = original_buffer
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息
        
        Returns:
            dict: 模型信息
        """
        return {
            "model_path": self.model_path,
            "model_type": "openvino",
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
    
    def close(self):
        """
        释放模型资源
        """
        try:
            # 释放推理请求
            if hasattr(self, 'infer_request') and self.infer_request is not None:
                # OpenVINO会自动管理资源，这里主要是标记为None
                self.infer_request = None
            
            # 释放编译模型
            if hasattr(self, 'compiled_model') and self.compiled_model is not None:
                self.compiled_model = None
            
            # 释放模型
            if hasattr(self, 'model') and self.model is not None:
                self.model = None
            
            # 释放Core对象
            if hasattr(self, 'core') and self.core is not None:
                self.core = None
            
            print(f"已释放模型资源: {self.model_path}")
        except Exception as e:
            print(f"释放模型资源时发生错误: {e}")
    
    def __del__(self):
        """
        析构函数，确保资源被释放
        """
        self.close()
    
    def _release_resources(self):
        """
        内部方法：释放当前资源，用于模型重新加载前
        """
        try:
            # 先关闭当前资源
            self.close()
        except Exception as e:
            print(f"释放资源失败: {e}")
            # 即使释放失败，也要继续执行，将资源标记为None
        finally:
            # 确保所有资源被标记为None
            self.model = None
            self.compiled_model = None
            self.infer_request = None
            self.core = None

def softmax(x):
    """
    计算softmax值
    
    Args:
        x: 输入数组
        
    Returns:
        np.ndarray: softmax结果
    """
    try:
        # 检查输入是否为None或空
        if x is None:
            raise ValueError("softmax输入不能为空")
        
        # 转换为numpy数组
        x = np.asarray(x)
        
        # 检查是否包含无穷大或NaN值
        if not np.isfinite(x).all():
            # 替换无穷大和NaN值为合理范围
            x = np.nan_to_num(x, nan=0.0, posinf=100.0, neginf=-100.0)
        
        # 避免数值溢出，减去最大值
        max_val = np.max(x)
        e_x = np.exp(x - max_val)
        
        # 计算总和，添加极小值避免除以零
        sum_e_x = np.sum(e_x) + 1e-10
        
        return e_x / sum_e_x
    except Exception as e:
        print(f"softmax计算错误: {e}")
        # 返回均匀分布作为 fallback
        return np.ones_like(x) / len(x) if len(x) > 0 else np.array([1.0])
