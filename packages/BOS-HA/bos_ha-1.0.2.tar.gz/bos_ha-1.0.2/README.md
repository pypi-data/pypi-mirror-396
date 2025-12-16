# BOS-HA - 基于深度学习的手语识别系统

BOS-HA是一个完整的手语识别系统，包括模型训练、实时识别、模型管理和Web客户端界面等功能。

## 功能特点

- **实时手语识别**: 支持通过摄像头进行实时手语识别
- **多种模型支持**: 支持PyTorch和OpenVINO模型
- **模型训练与转换**: 内置训练模块，支持模型转换为OpenVINO格式
- **Web客户端界面**: 提供直观的Web界面，支持实时显示和历史记录
- **WebSocket通信**: 基于WebSocket的实时通信架构
- **可扩展的模型库**: 支持多种模型的添加和切换

## 安装

```bash
pip install BOS-HA
```

## 快速开始

### 启动服务器

```bash
bosha-server
```

### 启动Web客户端

```bash
bosha-client
```

### 训练模型

```bash
bosha-train --config config.json
```

## 模型管理

### 列出可用模型

```bash
# 通过API获取
curl http://localhost:8000/models
```

### 切换模型

```bash
# 通过API切换
curl -X POST "http://localhost:8000/models/switch?model_name=hand_sign_model&model_type=pytorch"
```

## 技术架构

- **后端**: FastAPI + WebSocket
- **前端**: Flask + SocketIO + HTML/CSS/JavaScript
- **模型**: PyTorch + OpenVINO
- **视频处理**: OpenCV

## 目录结构

```
bosha/
├── server/         # 后端服务
│   ├── models/     # 模型文件
│   ├── services/   # 服务模块
│   └── main.py     # 主入口
├── client/         # 客户端
│   └── web_client/ # Web客户端
└── training/       # 训练模块
```

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

- 项目主页: https://github.com/bos-ha/BOS-HA
- 联系邮箱: contact@bos-ha.com
