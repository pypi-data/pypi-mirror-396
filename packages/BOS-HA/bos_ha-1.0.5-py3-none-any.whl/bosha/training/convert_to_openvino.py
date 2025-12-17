#!/usr/bin/env python3
"""
PyTorch模型转换为OpenVINO格式工具
"""

import os
import sys
import argparse
import torch
from pathlib import Path

def convert_model_to_openvino(
    model_path: str, 
    output_dir: str, 
    input_shape: tuple = (1, 3, 224, 224),
    model_name: str = None
):
    """
    将PyTorch模型转换为OpenVINO格式
    
    Args:
        model_path: PyTorch模型路径（.pt文件）
        output_dir: 输出目录
        input_shape: 输入形状，格式为 (batch, channels, height, width)
        model_name: 输出模型名称（可选）
    
    Returns:
        str: OpenVINO模型路径
    """
    print(f"开始转换PyTorch模型到OpenVINO格式")
    print(f"输入模型: {model_path}")
    print(f"输出目录: {output_dir}")
    print(f"输入形状: {input_shape}")
    
    # 检查模型文件是否存在
    if not os.path.exists(model_path):
        print(f"错误: 模型文件不存在: {model_path}")
        return None
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成模型名称
    if model_name is None:
        model_name = os.path.splitext(os.path.basename(model_path))[0] + "_openvino"
    
    # 检查是否已安装OpenVINO
    try:
        import openvino
        from openvino.runtime import Core
        from openvino.tools import mo
        print("OpenVINO已安装，可以进行转换")
    except ImportError as e:
        print(f"错误: 未安装OpenVINO: {e}")
        print("请安装OpenVINO: pip install openvino openvino-dev")
        return None
    
    try:
        # 加载PyTorch模型
        print("正在加载PyTorch模型...")
        # 添加weights_only=False参数以支持完整模型加载
        model = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
        model.eval()
        print("PyTorch模型加载成功")
        
        # 创建示例输入
        example_input = torch.randn(input_shape)
        print(f"创建示例输入，形状: {example_input.shape}")
        
        # 测试模型推理
        with torch.no_grad():
            example_output = model(example_input)
        # 处理Hugging Face模型返回的ImageClassifierOutputWithNoAttention对象
        output_tensor = example_output.logits
        print(f"模型推理测试成功，输出形状: {output_tensor.shape}")
        
        # 定义一个nn.Module包装类，确保返回的是张量而不是模型输出对象
        class ModelWrapper(torch.nn.Module):
            def __init__(self, model):
                super().__init__()
                self.model = model
            
            def forward(self, input_tensor):
                outputs = self.model(input_tensor)
                return outputs.logits
        
        # 创建包装模型实例
        wrapped_model = ModelWrapper(model)
        
        # 导出为ONNX格式
        onnx_path = os.path.join(output_dir, f"{model_name}.onnx")
        print(f"正在导出为ONNX格式，路径: {onnx_path}")
        torch.onnx.export(
            wrapped_model,
            example_input,
            onnx_path,
            export_params=True,
            opset_version=18,  # 使用更高的opset版本以支持最新特性
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}},
            verbose=False
        )
        print(f"ONNX导出成功: {onnx_path}")
        
        # 转换为OpenVINO格式
        print("正在转换为OpenVINO格式...")
        openvino_output_dir = os.path.join(output_dir, model_name)
        os.makedirs(openvino_output_dir, exist_ok=True)
        
        # 使用推荐的openvino.convert_model API转换ONNX到OpenVINO IR
        # 移除data_type参数，使用默认精度
        converted_model = openvino.convert_model(
            onnx_path,
            input=[('input', input_shape)]
        )
        
        # 保存转换后的模型
        openvino.save_model(
            converted_model,
            os.path.join(openvino_output_dir, model_name),
            compress=False
        )
        
        # 复制生成的.xml和.bin文件到output_dir根目录
        for file in os.listdir(openvino_output_dir):
            if file.endswith('.xml') or file.endswith('.bin'):
                src_path = os.path.join(openvino_output_dir, file)
                dst_path = os.path.join(output_dir, f"{model_name}.{file.split('.')[-1]}")
                import shutil
                shutil.copy(src_path, dst_path)
                print(f"复制文件: {src_path} -> {dst_path}")
        
        # 清理临时ONNX文件和目录
        os.remove(onnx_path)
        import shutil
        shutil.rmtree(openvino_output_dir)
        
        # 返回OpenVINO模型路径
        openvino_model_path = os.path.join(output_dir, f"{model_name}.xml")
        print(f"OpenVINO模型转换成功！")
        print(f"模型路径: {openvino_model_path}")
        print(f"权重路径: {os.path.join(output_dir, f'{model_name}.bin')}")
        
        return openvino_model_path
        
    except Exception as e:
        print(f"转换失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """
    主函数
    """
    parser = argparse.ArgumentParser(description="PyTorch模型转换为OpenVINO格式工具")
    parser.add_argument("--model_path", type=str, help="PyTorch模型路径（.pt文件）")
    parser.add_argument("--model_name", type=str, help="模型名称，用于从模型管理器获取模型路径")
    parser.add_argument("--output_dir", type=str, default="./output", help="输出目录")
    parser.add_argument("--input_shape", type=str, default="1,3,224,224", help="输入形状，格式为 batch,channels,height,width")
    parser.add_argument("--output_model_name", type=str, help="输出模型名称（可选）")
    
    args = parser.parse_args()
    
    # 处理模型参数
    model_path = args.model_path
    if args.model_name and not model_path:
        from bosha.models.model_manager import ModelManager
        manager = ModelManager()
        model_path = manager.get_model_path(args.model_name)
        if not model_path:
            print(f"错误: 模型 {args.model_name} 不存在")
            return 1
    
    if not model_path:
        print("错误: 必须指定 --model_path 或 --model_name")
        return 1
    
    # 解析输入形状
    try:
        input_shape = tuple(map(int, args.input_shape.split(',')))
        if len(input_shape) != 4:
            raise ValueError("输入形状必须包含4个值: batch,channels,height,width")
    except ValueError as e:
        print(f"错误: 无效的输入形状: {e}")
        print("请使用正确的格式，例如: --input_shape 1,3,224,224")
        return 1
    
    # 执行转换
    openvino_model_path = convert_model_to_openvino(
        model_path=model_path,
        output_dir=args.output_dir,
        input_shape=input_shape,
        model_name=args.output_model_name
    )
    
    if openvino_model_path:
        print(f"转换完成！OpenVINO模型已保存到: {openvino_model_path}")
        return 0
    else:
        print("转换失败！")
        return 1

if __name__ == "__main__":
    sys.exit(main())
