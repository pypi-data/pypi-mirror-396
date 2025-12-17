import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from bosha.server.utils import CryptoUtils, info, warning, error, exception
from bosha.server.config import settings
from bosha.server.models.sentence_generator import SentenceGenerator

class WebSocketService:
    """WebSocket服务类，处理WebSocket消息"""
    
    def __init__(self, resource_manager, hand_sign_model):
        """
        初始化WebSocket服务
        
        Args:
            resource_manager: 资源管理器实例
            hand_sign_model: 手语识别模型实例
        """
        self.resource_manager = resource_manager
        self.hand_sign_model = hand_sign_model
        self.clients = {}  # 存储客户端信息
        # 配置检测频率（每3秒一次，每分钟20次）
        self.detection_interval = 3.0  # 秒
        # 句子合并窗口（秒）
        self.merge_window = 5.0  # 句子合并窗口
    
    def validate_client(self, secret: str, client_id: str, passwd: str) -> bool:
        """
        验证客户端
        
        Args:
            secret: 客户端提供的密钥
            client_id: 客户端ID
            passwd: 客户端提供的密码（签名）
            
        Returns:
            bool: 验证结果
        """
        return CryptoUtils.validate_client(
            secret=secret,
            client_id=client_id,
            passwd=passwd,
            valid_clients=settings.VALID_CLIENTS
        )
    
    async def handle_message(
        self, 
        client_id: str, 
        message: Dict[str, Any], 
        send_message_func: Callable[[str], None]
    ):
        """
        处理WebSocket消息
        
        Args:
            client_id: 客户端ID
            message: 消息内容
            send_message_func: 发送消息的函数
        """
        try:
            func = message.get("function", "")
            info(f"处理客户端 {client_id} 的消息类型: {func}")
            
            # 根据消息类型处理
            if func == "hand_getresource":
                await self.handle_get_resource(client_id, message, send_message_func)
            elif func == "hand_DHeart":
                await self.handle_heartbeat(client_id, message, send_message_func)
            elif func == "hand_releaseresource":
                await self.handle_release_resource(client_id, message, send_message_func)
            elif func == "hand_video_frame":
                await self.handle_video_frame(client_id, message, send_message_func)
            else:
                warning(f"未知的消息类型: {func}")
                await self.send_error(client_id, send_message_func, "未知的消息类型")
                
        except Exception as e:
            exception(f"处理消息失败: {e}")
            await self.send_error(client_id, send_message_func, f"处理消息失败: {str(e)}")
    
    async def handle_get_resource(
        self, 
        client_id: str, 
        message: Dict[str, Any], 
        send_message_func: Callable[[str], None]
    ):
        """
        处理获取资源请求
        """
        try:
            # 分配资源
            resource = self.resource_manager.allocate_resource(client_id)
            
            if not resource:
                # 无可用资源
                response = {
                    "function": "hand_noresource",
                    "source": "server",
                    "packType": "response",
                    "timestamp": int(datetime.now().timestamp() * 1000)
                }
                await send_message_func(json.dumps(response))
                return
            
            # 构建资源响应
            response = {
                "function": "hand_resourceinfo",
                "source": "server",
                "packType": "response",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "data": {
                    "room": resource["channel"],
                    "uid": resource["uid"],
                    "token": resource.get("token", ""),
                    "expire": settings.AGORA_TOKEN_EXPIRY
                }
            }
            
            # 发送响应
            await send_message_func(json.dumps(response))
            info(f"已为客户端 {client_id} 分配资源: {resource}")
            
        except Exception as e:
            exception(f"处理获取资源请求失败: {e}")
            await self.send_error(client_id, send_message_func, f"获取资源失败: {str(e)}")
    
    async def handle_heartbeat(
        self, 
        client_id: str, 
        message: Dict[str, Any], 
        send_message_func: Callable[[str], None]
    ):
        """
        处理心跳消息
        """
        try:
            # 更新客户端心跳时间
            if client_id in self.clients:
                self.clients[client_id]["last_heartbeat"] = datetime.now()
            else:
                # 初始化客户端信息，包括句子生成器
                self.clients[client_id] = {
                    "last_heartbeat": datetime.now(),
                    "last_detection": None,
                    "last_result": None,
                    "result_timestamp": None,
                    "sentence_generator": SentenceGenerator(merge_window=self.merge_window)
                }
            
            info(f"收到客户端 {client_id} 的心跳")
            
            # 发送心跳响应，确保客户端收到服务器的回应，避免连接超时
            heartbeat_response = {
                "function": "hand_DHeart",
                "source": "server",
                "packType": "response",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "status": "ok"
            }
            await send_message_func(json.dumps(heartbeat_response))
            
        except Exception as e:
            exception(f"处理心跳消息失败: {e}")
    
    async def handle_video_frame(
        self, 
        client_id: str, 
        message: Dict[str, Any], 
        send_message_func: Callable[[str], None]
    ):
        """
        处理视频帧消息，控制检测频率为每分钟20次
        """
        try:
            # 更新客户端心跳时间
            if client_id in self.clients:
                self.clients[client_id]["last_heartbeat"] = datetime.now()
            else:
                # 初始化客户端信息，包括句子生成器
                self.clients[client_id] = {
                    "last_heartbeat": datetime.now(),
                    "last_detection": None,
                    "last_result": None,
                    "result_timestamp": None,
                    "sentence_generator": SentenceGenerator(merge_window=self.merge_window)
                }
            
            # 获取视频帧数据
            frame_data = message.get("data", {})
            frame_index = frame_data.get("frameIndex", 0)
            
            info(f"收到客户端 {client_id} 的视频帧，索引: {frame_index}")
            
            # 检查是否需要进行检测
            current_time = datetime.now()
            last_detection = self.clients[client_id].get("last_detection")
            
            if last_detection is None or (
                (current_time - last_detection).total_seconds() >= self.detection_interval
            ):
                # 更新检测时间
                self.clients[client_id]["last_detection"] = current_time
                
                # 实际调用模型进行手语识别
                try:
                    # 获取视频帧数据（base64编码）
                    image_base64 = frame_data.get("frame", "")
                    
                    if image_base64:
                        # base64解码和图像转换
                        import base64
                        import numpy as np
                        import cv2
                        
                        # 解码base64图像数据
                        try:
                            # 移除base64前缀
                            if image_base64.startswith('data:image'):
                                image_base64 = image_base64.split(',')[1]
                            
                            # 解码为二进制数据
                            img_bytes = base64.b64decode(image_base64)
                            
                            # 转换为numpy数组
                            np_arr = np.frombuffer(img_bytes, np.uint8)
                            
                            # 转换为OpenCV图像
                            frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                            
                            # 转换为RGB格式
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        except Exception as decode_error:
                            exception(f"图像解码失败: {decode_error}")
                            await self.send_error(client_id, send_message_func, f"图像解码失败: {str(decode_error)}")
                            return
                        
                        # 调用模型进行预测
                        result = self.hand_sign_model.predict(frame_rgb)
                        
                        if result.get("success", False):
                            predicted_text = result.get("predicted_class", "")
                            confidence = result.get("confidence", 0.0)
                            
                            if predicted_text:
                                # 发送识别结果
                                await self.send_translate_result(
                                    client_id=client_id,
                                    send_message_func=send_message_func,
                                    text=predicted_text,
                                    confidence=confidence
                                )
                            else:
                                info("识别结果为空")
                        else:
                            info(f"模型预测失败: {result.get('message', '未知错误')}")
                    else:
                        info("视频帧中没有图像数据")
                        
                except Exception as e:
                    exception(f"调用模型失败: {e}")
                    await self.send_error(client_id, send_message_func, f"模型调用失败: {str(e)}")
            else:
                # 跳过检测，只更新心跳
                info(f"跳过检测，距离上次检测仅 {(current_time - last_detection).total_seconds():.1f} 秒")
            
        except Exception as e:
            exception(f"处理视频帧消息失败: {e}")
            await self.send_error(client_id, send_message_func, f"处理视频帧失败: {str(e)}")
    
    async def handle_release_resource(
        self, 
        client_id: str, 
        message: Dict[str, Any], 
        send_message_func: Callable[[str], None]
    ):
        """
        处理释放资源请求
        """
        try:
            # 释放资源
            self.resource_manager.release_resource(client_id)
            
            # 构建响应
            response = {
                "function": "hand_releaseresource",
                "source": "server",
                "packType": "response",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "code": 0,
                "msg": "资源释放成功"
            }
            
            # 发送响应
            await send_message_func(json.dumps(response))
            info(f"客户端 {client_id} 资源已释放")
            
        except Exception as e:
            exception(f"处理释放资源请求失败: {e}")
            await self.send_error(client_id, send_message_func, f"释放资源失败: {str(e)}")
    
    async def handle_disconnect(self, client_id: str):
        """
        处理客户端断开连接
        
        Args:
            client_id: 客户端ID
        """
        try:
            # 释放资源
            self.resource_manager.release_resource(client_id)
            
            # 移除客户端信息
            if client_id in self.clients:
                del self.clients[client_id]
            
            info(f"客户端 {client_id} 已断开连接，资源已释放")
            
        except Exception as e:
            exception(f"处理客户端断开连接失败: {e}")
    
    async def send_error(
        self, 
        client_id: str, 
        send_message_func: Callable[[str], None], 
        error_message: str
    ):
        """
        发送错误响应
        
        Args:
            client_id: 客户端ID
            send_message_func: 发送消息的函数
            error_message: 错误信息
        """
        error_response = {
            "function": "hand_error",
            "source": "server",
            "packType": "response",
            "timestamp": int(datetime.now().timestamp() * 1000),
            "code": 500,
            "msg": error_message
        }
        await send_message_func(json.dumps(error_response))
    
    async def send_translate_result(
        self, 
        client_id: str, 
        send_message_func: Callable[[str], None], 
        text: str, 
        confidence: float = 1.0
    ):
        """
        发送翻译结果，实现连续相同结果去重，并使用句子生成器生成完整句子
        
        Args:
            client_id: 客户端ID
            send_message_func: 发送消息的函数
            text: 翻译文本
            confidence: 置信度
        """
        # 检查是否需要发送结果（去重）
        current_time = datetime.now()
        last_result = self.clients[client_id].get("last_result")
        result_timestamp = self.clients[client_id].get("result_timestamp")
        
        # 如果结果相同，只在5秒后再次发送
        if last_result == text and result_timestamp is not None:
            if (current_time - result_timestamp).total_seconds() < 5.0:
                info(f"跳过重复结果: {text}")
                return
        
        # 更新最后结果和时间
        self.clients[client_id]["last_result"] = text
        self.clients[client_id]["result_timestamp"] = current_time
        
        # 生成基本结果
        base_result = {
            "text": text,
            "confidence": confidence,
            "timestamp": current_time.timestamp()
        }
        
        # 使用句子生成器生成完整句子
        sentence_generator = self.clients[client_id].get("sentence_generator")
        if sentence_generator:
            # 添加结果到句子生成器
            generated_sentence = sentence_generator.add_result(base_result)
            
            # 发送单词级结果
            word_result = {
                "function": "hand_translate",
                "source": "server",
                "packType": "response",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "data": {
                    "text": text,
                    "confidence": confidence,
                    "type": "word",
                    "current_sentence": sentence_generator.get_current_sentence()
                }
            }
            await send_message_func(json.dumps(word_result))
            
            # 如果生成了完整句子，发送句子级结果
            if generated_sentence:
                sentence_result = {
                    "function": "hand_translate",
                    "source": "server",
                    "packType": "response",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "data": {
                        "text": generated_sentence,
                        "confidence": confidence,
                        "type": "sentence",
                        "words": text
                    }
                }
                await send_message_func(json.dumps(sentence_result))
        else:
            # 如果没有句子生成器，只发送单词级结果
            result = {
                "function": "hand_translate",
                "source": "server",
                "packType": "response",
                "timestamp": int(datetime.now().timestamp() * 1000),
                "data": {
                    "text": text,
                    "confidence": confidence
                }
            }
            await send_message_func(json.dumps(result))
    
    def cleanup_timeout_clients(self):
        """
        清理超时客户端
        """
        current_time = datetime.now()
        timeout_clients = []
        
        for client_id, info in self.clients.items():
            last_heartbeat = info.get("last_heartbeat")
            if last_heartbeat and (
                (current_time - last_heartbeat).total_seconds() > settings.CONNECTION_TIMEOUT
            ):
                timeout_clients.append(client_id)
        
        for client_id in timeout_clients:
            warning(f"客户端 {client_id} 超时，释放资源")
            self.resource_manager.release_resource(client_id)
            del self.clients[client_id]
    
    def get_client_count(self) -> int:
        """
        获取客户端数量
        
        Returns:
            int: 客户端数量
        """
        return len(self.clients)