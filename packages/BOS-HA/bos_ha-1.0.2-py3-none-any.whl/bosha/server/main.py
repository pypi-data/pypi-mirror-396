from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
import json
import logging
from datetime import datetime
import asyncio
from typing import Dict, List, Optional

# 导入服务模块
from bosha.server.services.websocket_service import WebSocketService
from bosha.server.services.resource_manager import ResourceManager
from bosha.server.models.hand_sign_model import HandSignModel
from bosha.server.config import settings

# 配置日志
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="手语识别服务端",
              description="基于WebSocket的手语识别模型服务",
              version="1.0.0")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化服务
resource_manager = ResourceManager()

# 初始化手语识别模型
import os
from bosha.server.models import HandSignModel, OpenVinoHandSignModel

# 根据配置选择模型类型
if settings.MODEL_TYPE == "openvino":
    # 加载OpenVINO模型
    model_path = os.path.join(os.path.dirname(__file__), f"../models/{settings.OPENVINO_MODEL_NAME}.xml")
    print(f"正在加载OpenVINO模型: {model_path}")
    hand_sign_model = OpenVinoHandSignModel(
        model_path,
        confidence_threshold=settings.OPENVINO_CONFIDENCE_THRESHOLD
    )
else:
    # 加载PyTorch模型
    model_path = os.path.join(os.path.dirname(__file__), f"../models/{settings.CURRENT_MODEL}.pt")
    print(f"正在加载PyTorch模型: {model_path}")
    hand_sign_model = HandSignModel(
        model_path,
        confidence_threshold=settings.MODEL_CONFIDENCE_THRESHOLD
    )

# 初始化WebSocket服务
websocket_service = WebSocketService(resource_manager, hand_sign_model)

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"客户端 {client_id} 已连接")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"客户端 {client_id} 已断开连接")
    
    async def send_personal_message(self, message: str, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/tech/ws/appclient")
async def websocket_endpoint(
    websocket: WebSocket,
    secret: str = Query(...),
    clientid: str = Query(...),
    passwd: str = Query(...)
):
    """WebSocket端点，处理客户端连接"""
    
    # 验证客户端
    if not websocket_service.validate_client(secret, clientid, passwd):
        logger.warning(f"客户端 {clientid} 验证失败")
        await websocket.close(code=4001, reason="Authentication failed")
        return
    
    # 接受连接
    await manager.connect(websocket, clientid)
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            logger.info(f"收到客户端 {clientid} 的消息: {data[:50]}...")
            
            # 处理消息
            try:
                message = json.loads(data)
                await websocket_service.handle_message(
                    client_id=clientid,
                    message=message,
                    send_message_func=lambda msg: manager.send_personal_message(msg, clientid)
                )
            except json.JSONDecodeError as e:
                logger.error(f"JSON解析失败: {e}")
                # 发送错误响应
                error_msg = {
                    "function": "hand_error",
                    "source": "server",
                    "packType": "response",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "code": 400,
                    "msg": "Invalid JSON format"
                }
                await manager.send_personal_message(json.dumps(error_msg), clientid)
            except Exception as e:
                logger.error(f"处理消息失败: {e}")
                # 发送错误响应
                error_msg = {
                    "function": "hand_error",
                    "source": "server",
                    "packType": "response",
                    "timestamp": int(datetime.now().timestamp() * 1000),
                    "code": 500,
                    "msg": "Internal server error"
                }
                await manager.send_personal_message(json.dumps(error_msg), clientid)
    
    except WebSocketDisconnect:
        # 客户端断开连接
        manager.disconnect(clientid)
        await websocket_service.handle_disconnect(client_id=clientid)
    except Exception as e:
        logger.error(f"WebSocket异常: {e}")
        manager.disconnect(clientid)
        await websocket_service.handle_disconnect(client_id=clientid)

@app.get("/")
async def root():
    """健康检查端点"""
    return {
        "status": "ok",
        "message": "手语识别服务端运行正常",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/status")
async def get_status():
    """获取服务状态"""
    return {
        "status": "ok",
        "active_connections": len(manager.active_connections),
        "available_resources": resource_manager.available_resources,
        "current_model": settings.CURRENT_MODEL,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/models")
async def get_models():
    """获取可用的模型列表"""
    import os
    
    # 获取模型目录
    model_dir = os.path.join(os.path.dirname(__file__), settings.MODEL_DIR)
    
    # 列出所有.pt和.xml文件作为可用模型
    available_models = {}
    if os.path.exists(model_dir):
        for file in os.listdir(model_dir):
            # 检查PyTorch模型
            if file.endswith(".pt"):
                model_name = os.path.splitext(file)[0]
                if "pytorch" not in available_models:
                    available_models["pytorch"] = []
                available_models["pytorch"].append(model_name)
            # 检查OpenVINO模型
            elif file.endswith(".xml"):
                model_name = os.path.splitext(file)[0]
                if "openvino" not in available_models:
                    available_models["openvino"] = []
                available_models["openvino"].append(model_name)
    
    return {
        "status": "ok",
        "current_model": settings.CURRENT_MODEL,
        "current_model_type": settings.MODEL_TYPE,
        "available_models": available_models,
        "model_dir": model_dir
    }

@app.post("/models/switch")
async def switch_model(model_name: str, model_type: str = "pytorch"):
    """切换模型
    
    Args:
        model_name: 要切换到的模型名称
        model_type: 模型类型 (pytorch 或 openvino)
    """
    import os
    
    # 检查模型类型是否有效
    if model_type not in ["pytorch", "openvino"]:
        return {
            "status": "error",
            "message": f"不支持的模型类型 {model_type}",
            "current_model": settings.CURRENT_MODEL,
            "current_model_type": settings.MODEL_TYPE
        }
    
    # 根据模型类型检查不同的模型文件
    if model_type == "openvino":
        # OpenVINO模型使用.xml文件
        model_extension = ".xml"
    else:
        # PyTorch模型使用.pt文件
        model_extension = ".pt"
    
    # 检查模型是否存在
    model_path = os.path.join(os.path.dirname(__file__), settings.MODEL_DIR, f"{model_name}{model_extension}")
    if not os.path.exists(model_path):
        return {
            "status": "error",
            "message": f"模型 {model_name}{model_extension} 不存在",
            "current_model": settings.CURRENT_MODEL,
            "current_model_type": settings.MODEL_TYPE
        }
    
    # 更新当前模型设置
    settings.CURRENT_MODEL = model_name
    settings.MODEL_TYPE = model_type
    
    # 重新加载模型
    global hand_sign_model
    if model_type == "openvino":
        from bosha.server.models import OpenVinoHandSignModel
        hand_sign_model = OpenVinoHandSignModel(
            model_path,
            confidence_threshold=settings.OPENVINO_CONFIDENCE_THRESHOLD
        )
    else:
        from bosha.server.models import HandSignModel
        hand_sign_model = HandSignModel(
            model_path,
            confidence_threshold=settings.MODEL_CONFIDENCE_THRESHOLD
        )
    
    return {
        "status": "ok",
        "message": f"成功切换到{model_type}模型 {model_name}",
        "current_model": settings.CURRENT_MODEL,
        "current_model_type": settings.MODEL_TYPE,
        "model_path": model_path
    }

def start_server(host: str = None, port: int = None, log_level: str = "info", model_name: str = None, model_type: str = None):
    """
    启动FastAPI服务器
    
    Args:
        host: 服务器主机地址，默认使用配置文件中的设置
        port: 服务器端口，默认使用配置文件中的设置
        log_level: 日志级别，默认info
        model_name: 要使用的模型名称
        model_type: 模型类型 (pytorch 或 openvino)
    """
    import uvicorn
    
    # 如果指定了模型名称，更新设置
    if model_name:
        settings.CURRENT_MODEL = model_name
    
    if model_type:
        settings.MODEL_TYPE = model_type
    
    uvicorn.run(
        app,
        host=host or settings.SERVER_HOST,
        port=port or settings.SERVER_PORT,
        log_level=log_level
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="手语识别服务端")
    parser.add_argument("--host", type=str, help="服务器主机地址")
    parser.add_argument("--port", type=int, help="服务器端口")
    parser.add_argument("--log-level", type=str, default="info", help="日志级别")
    parser.add_argument("--model-name", type=str, help="要使用的模型名称")
    parser.add_argument("--model-type", type=str, choices=["pytorch", "openvino"], help="模型类型")
    
    args = parser.parse_args()
    
    start_server(
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        model_name=args.model_name,
        model_type=args.model_type
    )
