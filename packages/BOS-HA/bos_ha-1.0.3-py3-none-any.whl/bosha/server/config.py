class Settings:
    """服务器配置类"""
    
    # 服务器基本配置
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    
    # WebSocket配置
    WEBSOCKET_PATH: str = "/tech/ws/appclient"
    HEARTBEAT_INTERVAL: int = 30  # 心跳间隔，单位：秒
    CONNECTION_TIMEOUT: int = 60  # 连接超时时间，单位：秒
    
    # 资源管理配置
    MAX_CHANNELS: int = 10  # 最大通道数
    MAX_UIDS_PER_CHANNEL: int = 5  # 每个通道最大用户数
    
    # 模型配置
    MODEL_DIR: str = "models"  # 模型目录
    CURRENT_MODEL: str = "hand_sign_model"  # 当前使用的模型名称
    MODEL_TYPE: str = "pytorch"  # 模型类型：pytorch 或 openvino
    MODEL_CONFIDENCE_THRESHOLD: float = 0.7  # 模型置信度阈值
    FRAME_PROCESS_INTERVAL: int = 33  # 帧处理间隔，约30fps
    
    # OpenVINO模型配置
    OPENVINO_MODEL_NAME: str = "hand_sign_model_openvino"  # OpenVINO模型名称
    OPENVINO_CONFIDENCE_THRESHOLD: float = 0.6  # OpenVINO模型置信度阈值
    
    @property
    def MODEL_PATH(self):
        """动态获取当前模型路径"""
        import os
        return os.path.join(os.path.dirname(__file__), f"{self.MODEL_DIR}/{self.CURRENT_MODEL}.pt")
    
    # 声网SDK配置
    AGORA_APP_ID: str = "your_agora_app_id"  # 替换为实际的声网App ID
    AGORA_CHANNEL_PREFIX: str = "hand_sign_"  # 声网频道前缀
    AGORA_TOKEN_EXPIRY: int = 3600  # Token过期时间，单位：秒
    
    # 客户端验证配置
    VALID_CLIENTS: dict = {
        "App_tcl_001": "3mLKJQI6zGOgGTI938iGZLf2lrRQcA",  # 客户端ID: 密钥
        "test_client": "test_secret"  # 测试客户端
    }
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 视频处理配置
    VIDEO_WIDTH: int = 640
    VIDEO_HEIGHT: int = 480
    VIDEO_FPS: int = 30
    
    # 手语识别配置
    RECOGNITION_LANGUAGE: str = "zh"  # 识别语言
    SUPPORTED_GESTURES: list = ["你好", "谢谢", "再见", "我爱你", "是", "否"]  # 支持的手势列表

# 创建全局配置实例
settings = Settings()
