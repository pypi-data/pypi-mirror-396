from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import os
import sys
import threading
import time
import asyncio

# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# 导入自定义模块
from bosha.server.services.video_processor import VideoProcessor
from bosha.client.web_client.utils.ws_client import SignLanguageClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_for_hand_sign'
app.config['DEBUG'] = True

# 初始化SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# 全局状态
camera_status = {
    'running': False,
    'fps': 30,
    'detection_interval': 3,  # 每3秒检测一次
    'merge_window': 5  # 结果合并窗口（秒）
}

# 初始化视频处理器和手语识别客户端
video_processor = None
sign_language_client = None

# 添加用于处理视频的工具
import subprocess
import tempfile
import os
import cv2
import time
import numpy as np

# 路由定义
@app.route('/')
def index():
    """主页面"""
    return render_template('index.html', **camera_status)

@app.route('/api/status')
def get_status():
    """获取当前状态"""
    global camera_status
    # 更新视频处理器状态
    if video_processor:
        video_status = video_processor.get_status()
        camera_status['running'] = video_status['running']
    return jsonify(camera_status)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """更新设置"""
    global camera_status
    data = request.json
    
    if 'fps' in data:
        camera_status['fps'] = data['fps']
        if video_processor:
            video_processor.set_fps(data['fps'])
    if 'detection_interval' in data:
        camera_status['detection_interval'] = data['detection_interval']
        if video_processor:
            video_processor.set_detection_interval(data['detection_interval'])
    if 'merge_window' in data:
        camera_status['merge_window'] = data['merge_window']
    
    # 广播设置更新
    socketio.emit('settings_updated', camera_status)
    return jsonify({'success': True, 'status': camera_status})

@app.route('/api/upload_video', methods=['POST'])
def upload_video():
    """上传视频并进行识别"""
    try:
        if 'video' not in request.files:
            return jsonify({'success': False, 'message': '没有视频文件'})
        
        file = request.files['video']
        if file.filename == '':
            return jsonify({'success': False, 'message': '没有选择视频文件'})
        
        # 保存上传的视频到临时文件
        with tempfile.NamedTemporaryFile(suffix='.' + file.filename.split('.')[-1], delete=False) as temp_video:
            temp_video.write(file.read())
            video_path = temp_video.name
        
        # 处理视频
        result = process_video(video_path)
        
        # 删除临时文件
        os.unlink(video_path)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

def check_ffmpeg():
    """检查FFmpeg是否已安装"""
    try:
        subprocess.run(['ffmpeg', '-version'], check=True, capture_output=True, text=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def process_video(video_path):
    """处理视频，使用OpenCV直接提取帧并识别"""
    start_time = time.time()
    
    try:
        # 3. 初始化手语识别模型
        from bosha.server.models.hand_sign_model import HandSignModel
        model_path = os.path.join(os.path.dirname(__file__), '../../models/hand_sign_model.pt')
        sign_model = HandSignModel(model_path)
        
        # 1. 使用OpenCV直接读取视频
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return {'success': False, 'message': '无法打开视频文件'}
        
        # 4. 对每一帧进行识别
        results = []
        frame_count = 0
        
        # 获取视频帧率
        fps = cap.get(cv2.CAP_PROP_FPS)
        if fps <= 0:
            fps = 24  # 默认帧率
        
        # 计算采样间隔（每秒1帧）
        sample_interval = int(fps)
        
        # 读取视频帧
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame_count += 1
            
            # 只处理每秒1帧
            if frame_count % sample_interval != 0:
                continue
            
            try:
                # 转换为RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # 识别
                result = sign_model.predict(frame_rgb)
                if result['success'] and result['predicted_class']:
                    results.append({
                        'text': result['predicted_class'],
                        'confidence': result['confidence']
                    })
            except Exception as e:
                print(f"处理帧失败: {e}")
                continue
        
        # 释放视频捕获对象
        cap.release()
        
        if frame_count == 0:
            return {'success': False, 'message': '无法从视频中提取帧'}
        
        # 5. 合并识别结果
        # 优化合并逻辑：考虑置信度和相邻重复
        merged_results = []
        for res in results:
            if not merged_results:
                merged_results.append(res)
            else:
                # 如果与上一个结果相同，则跳过
                if res['text'] == merged_results[-1]['text']:
                    # 如果当前置信度更高，则更新置信度
                    if res['confidence'] > merged_results[-1]['confidence']:
                        merged_results[-1] = res
                else:
                    merged_results.append(res)
        
        # 6. 生成最终结果文本
        final_text = ''.join([res['text'] for res in merged_results])
        
        # 7. 计算平均置信度
        if merged_results:
            avg_confidence = sum(res['confidence'] for res in merged_results) / len(merged_results)
        else:
            avg_confidence = 0.0
        
        process_time = round(time.time() - start_time, 2)
        
        return {
            'success': True,
            'filename': os.path.basename(video_path),
            'result': final_text,
            'frame_count': frame_count,
            'processed_frames': len(results),
            'process_time': process_time,
            'average_confidence': round(avg_confidence, 2),
            'raw_results': [res['text'] for res in merged_results]
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'处理视频失败: {str(e)}'
        }

# 识别结果回调函数
def on_recognition_result(result):
    """处理手语识别结果"""
    # 发送识别结果到前端
    socketio.emit('recognition_result', result)

# SocketIO事件处理
@socketio.on('connect')
def handle_connect():
    """客户端连接事件"""
    global video_processor, sign_language_client
    print(f"客户端 {request.sid} 已连接")
    
    # 初始化视频处理器（如果尚未初始化）
    if not video_processor:
        video_processor = VideoProcessor(socketio)
        
    # 初始化手语识别客户端（如果尚未初始化）
    if not sign_language_client:
        sign_language_client = SignLanguageClient()
        sign_language_client.set_on_result_callback(on_recognition_result)
        
        # 连接到原有WebSocket服务器
        asyncio.run(sign_language_client.connect())
        
        # 将手语识别客户端设置到视频处理器
        video_processor.set_sign_language_client(sign_language_client)
    
    # 发送当前状态
    emit('status_update', camera_status)

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接事件"""
    print(f"客户端 {request.sid} 已断开连接")
    
    # 如果没有活跃客户端，关闭视频和连接
    if len(socketio.server.manager.rooms['/']) <= 1:  # 只保留服务器自己
        global camera_status
        camera_status['running'] = False
        if video_processor:
            video_processor.stop()
        if sign_language_client:
            asyncio.run(sign_language_client.disconnect())

@socketio.on('toggle_camera')
def handle_toggle_camera():
    """切换摄像头状态"""
    global camera_status, video_processor
    
    success = False
    if camera_status['running']:
        # 停止视频采集
        if video_processor:
            success = video_processor.stop()
        if success:
            camera_status['running'] = False
    else:
        # 启动视频采集
        if video_processor:
            success = video_processor.start()
        if success:
            camera_status['running'] = True
    
    print(f"摄像头状态: {'开启' if camera_status['running'] else '关闭'}")
    
    # 广播状态更新
    socketio.emit('status_update', camera_status)
    return {'success': success, 'running': camera_status['running']}

@socketio.on('update_settings')
def handle_update_settings(data):
    """更新设置（通过SocketIO）"""
    global camera_status
    
    if 'fps' in data:
        camera_status['fps'] = data['fps']
        if video_processor:
            video_processor.set_fps(data['fps'])
    if 'detection_interval' in data:
        camera_status['detection_interval'] = data['detection_interval']
        if video_processor:
            video_processor.set_detection_interval(data['detection_interval'])
    if 'merge_window' in data:
        camera_status['merge_window'] = data['merge_window']
    
    # 广播设置更新
    socketio.emit('settings_updated', camera_status)
    return {'success': True, 'status': camera_status}

@socketio.on('request_video_stream')
def handle_request_video_stream():
    """请求视频流"""
    print("收到视频流请求")
    emit('video_stream_started', {'status': 'started'})

def start_client(host: str = '127.0.0.1', port: int = 5000, debug: bool = True):
    """
    启动Flask客户端应用
    
    Args:
        host: 客户端主机地址，默认127.0.0.1
        port: 客户端端口，默认5000
        debug: 是否开启调试模式，默认True
    """
    print(f"启动Flask应用，访问地址: http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=debug)

if __name__ == '__main__':
    start_client()