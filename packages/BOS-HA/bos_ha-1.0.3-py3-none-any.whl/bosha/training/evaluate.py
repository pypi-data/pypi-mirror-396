#!/usr/bin/env python3
"""
手语识别模型评估脚本
"""

import os
import torch
from transformers import AutoImageProcessor
from torch.utils.data import DataLoader
from bosha.training.train import HandSignDataset
import json
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evaluation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def evaluate_model(model_path, data_dir, processor_path, config_path="config.json"):
    """
    评估模型
    
    Args:
        model_path: 模型文件路径
        data_dir: 评估数据集目录
        processor_path: 图像处理器配置路径
        config_path: 配置文件路径
    
    Returns:
        dict: 评估结果
    """
    logger.info(f"加载配置: {config_path}")
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 加载模型和处理器
    logger.info(f"加载模型: {model_path}")
    model = torch.load(model_path)
    model.eval()
    
    logger.info(f"加载处理器配置: {processor_path}")
    processor = AutoImageProcessor.from_pretrained(processor_path)
    
    # 创建评估数据集和数据加载器
    logger.info(f"加载评估数据: {data_dir}")
    dataset = HandSignDataset(
        data_dir=data_dir,
        processor=processor
    )
    
    dataloader = DataLoader(
        dataset,
        batch_size=config['batch_size'],
        shuffle=False,
        num_workers=config['num_workers']
    )
    
    # 设置设备
    device = torch.device(config['device'] if torch.cuda.is_available() else 'cpu')
    model.to(device)
    logger.info(f"使用设备: {device}")
    
    # 开始评估
    logger.info("开始评估...")
    total_correct = 0
    total_samples = 0
    
    with torch.no_grad():
        for batch in dataloader:
            # 移动数据到设备
            for key in batch.keys():
                batch[key] = batch[key].to(device)
            
            # 前向传播
            outputs = model(**batch)
            logits = outputs.logits
            
            # 计算准确率
            _, predicted = torch.max(logits, 1)
            correct = (predicted == batch['labels']).sum().item()
            samples = batch['labels'].size(0)
            
            # 更新统计信息
            total_correct += correct
            total_samples += samples
    
    # 计算准确率
    accuracy = total_correct / total_samples
    logger.info(f"评估完成！准确率: {accuracy:.4f}")
    
    # 返回评估结果
    return {
        "accuracy": accuracy,
        "total_samples": total_samples,
        "correct_samples": total_correct,
        "model_path": model_path,
        "data_dir": data_dir
    }

def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="手语识别模型评估脚本")
    parser.add_argument("--model_path", type=str, help="模型文件路径")
    parser.add_argument("--model_name", type=str, help="模型名称")
    parser.add_argument("--data_dir", type=str, required=True, help="评估数据集目录")
    parser.add_argument("--processor_path", type=str, help="图像处理器配置路径")
    parser.add_argument("--config_path", type=str, default="config.json", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 处理模型参数
    model_path = args.model_path
    if args.model_name and not model_path:
        from bosha.models.model_manager import ModelManager
        manager = ModelManager()
        model_path = manager.get_model_path(args.model_name)
        if not model_path:
            print(f"错误: 模型 {args.model_name} 不存在")
            return
        
        # 如果没有指定处理器路径，使用模型所在目录
        if not args.processor_path:
            args.processor_path = os.path.dirname(model_path)
    
    if not model_path:
        print("错误: 必须指定 --model_path 或 --model_name")
        return
    
    if not args.processor_path:
        print("错误: 必须指定 --processor_path")
        return
    
    # 评估模型
    result = evaluate_model(
        model_path=model_path,
        data_dir=args.data_dir,
        processor_path=args.processor_path,
        config_path=args.config_path
    )
    
    # 保存评估结果
    result_path = f"evaluation_result_{os.path.basename(model_path)}.json"
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"评估结果已保存到: {result_path}")

if __name__ == "__main__":
    main()
