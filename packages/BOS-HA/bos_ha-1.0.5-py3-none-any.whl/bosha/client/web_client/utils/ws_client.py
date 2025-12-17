#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WebSocket客户端，用于连接手语识别服务器
"""

import asyncio
import websockets
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SignLanguageClient:
    """
    手语识别WebSocket客户端，用于连接服务器并接收识别结果
    """
    
    def __init__(self, server_url: str = "ws://127.0.0.1:8000/tech/ws/appclient"):
        """
        初始化客户端
        
        Args:
            server_url: WebSocket服务器URL
        """
        self.server_url = server_url
        self.websocket = None
        self.connected = False
        self.on_result_callback = None
        self.task = None
        
    def set_on_result_callback(self, callback):
        """
        设置识别结果回调函数
        
        Args:
            callback: 回调函数，接收识别结果作为参数
        """
        self.on_result_callback = callback
    
    async def connect(self):
        """
        连接到WebSocket服务器
        """
        try:
            # 连接到WebSocket服务器
            self.websocket = await websockets.connect(self.server_url)
            self.connected = True
            logger.info(f"成功连接到服务器: {self.server_url}")
            
            # 启动消息接收任务
            self.task = asyncio.create_task(self.receive_messages())
            
            return True
        except Exception as e:
            logger.error(f"连接服务器失败: {e}")
            self.connected = False
            return False
    
    async def disconnect(self):
        """
        断开与WebSocket服务器的连接
        """
        if self.connected:
            try:
                if self.websocket:
                    await self.websocket.close()
                if self.task:
                    self.task.cancel()
                self.connected = False
                logger.info("已断开与服务器的连接")
                return True
            except Exception as e:
                logger.error(f"断开连接失败: {e}")
                return False
        return True
    
    async def send_message(self, message: dict):
        """
        向服务器发送消息
        
        Args:
            message: 要发送的消息，字典格式
        """
        if not self.connected:
            logger.warning("客户端未连接，无法发送消息")
            return False
        
        try:
            # 将消息转换为JSON字符串
            json_message = json.dumps(message)
            # 发送消息
            await self.websocket.send(json_message)
            logger.info(f"已发送消息: {json_message[:50]}...")
            return True
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            return False
    
    async def receive_messages(self):
        """
        接收并处理服务器发送的消息
        """
        try:
            while self.connected:
                # 接收消息
                message = await self.websocket.recv()
                logger.info(f"收到消息: {message[:50]}...")
                
                # 解析消息
                try:
                    data = json.loads(message)
                    
                    # 如果是识别结果，调用回调函数
                    if data.get("function") == "hand_result" and self.on_result_callback:
                        self.on_result_callback(data)
                except json.JSONDecodeError as e:
                    logger.error(f"解析消息失败: {e}")
        except websockets.exceptions.ConnectionClosed as e:
            logger.info(f"连接已关闭: {e}")
            self.connected = False
        except Exception as e:
            logger.error(f"接收消息失败: {e}")
            self.connected = False
    
    def is_connected(self):
        """
        检查客户端是否已连接到服务器
        
        Returns:
            bool: 是否已连接
        """
        return self.connected
    
    def get_server_url(self):
        """
        获取服务器URL
        
        Returns:
            str: 服务器URL
        """
        return self.server_url

if __name__ == "__main__":
    """
    测试客户端
    """
    import asyncio
    
    async def main():
        # 创建客户端实例
        client = SignLanguageClient()
        
        # 定义回调函数
        def on_result(result):
            print(f"收到识别结果: {result}")
        
        # 设置回调函数
        client.set_on_result_callback(on_result)
        
        # 连接到服务器
        connected = await client.connect()
        if connected:
            # 发送测试消息
            await client.send_message({"function": "test", "data": "hello"})
            
            # 保持连接5秒
            await asyncio.sleep(5)
            
            # 断开连接
            await client.disconnect()
    
    asyncio.run(main())
