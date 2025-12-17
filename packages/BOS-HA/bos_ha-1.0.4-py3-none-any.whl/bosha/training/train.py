#!/usr/bin/env python3
"""
手语识别模型训练脚本
"""

import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from transformers import AutoImageProcessor, AutoModelForImageClassification
from torchvision.transforms import transforms
import json
from tqdm import tqdm
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HandSignDataset(Dataset):
    """手语识别数据集类"""
    
    def __init__(self, data_dir, processor, transform=None):
        """
        初始化数据集
        
        Args:
            data_dir: 数据集目录
            processor: 图像处理器
            transform: 额外的图像变换
        """
        self.data_dir = data_dir
        self.processor = processor
        self.transform = transform
        self.data = []
        self.labels = []
        self.label_to_idx = {}
        
        # 加载数据集
        self._load_dataset()
    
    def _load_dataset(self):
        """加载数据集"""
        logger.info(f"开始加载数据集，路径: {self.data_dir}")
        
        # 检查数据目录是否存在
        if not os.path.exists(self.data_dir):
            logger.error(f"数据目录不存在: {self.data_dir}")
            return
        
        # 遍历数据集目录，每个子目录对应一个类别
        dirs = os.listdir(self.data_dir)
        logger.info(f"数据目录下的子目录: {dirs}")
        
        for label_idx, label in enumerate(sorted(dirs)):
            label_dir = os.path.join(self.data_dir, label)
            logger.info(f"检查子目录: {label_dir}")
            
            if not os.path.isdir(label_dir):
                logger.info(f"跳过非目录项: {label}")
                continue
            
            # 添加标签映射
            self.label_to_idx[label] = label_idx
            
            # 遍历每个类别的图像文件
            try:
                img_files = os.listdir(label_dir)
                logger.info(f"类别 {label} 下的文件数量: {len(img_files)}")
                
                for img_file in img_files:
                    img_path = os.path.join(label_dir, img_file)
                    if img_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        self.data.append(img_path)
                        self.labels.append(label_idx)
                        logger.debug(f"添加样本: {img_path}")
                    else:
                        logger.debug(f"跳过非图像文件: {img_file}")
            except Exception as e:
                logger.error(f"处理类别 {label} 时出错: {e}")
        
        logger.info(f"加载了 {len(self.data)} 个样本，{len(self.label_to_idx)} 个类别")
        logger.info(f"标签映射: {self.label_to_idx}")
        
        # 检查是否有样本被加载
        if len(self.data) == 0:
            logger.error("未加载到任何样本，请检查数据集目录结构和文件格式")
            logger.error(f"期望的目录结构: {self.data_dir}/类别名称/图像文件.jpg")
    
    def __len__(self):
        """返回数据集大小"""
        return len(self.data)
    
    def __getitem__(self, idx):
        """获取单个样本"""
        img_path = self.data[idx]
        label = self.labels[idx]
        
        # 加载图像
        from PIL import Image
        image = Image.open(img_path).convert('RGB')
        
        # 应用变换
        if self.transform:
            image = self.transform(image)
        
        # 使用processor处理图像，processor会处理ToTensor和归一化
        # 注意：image是PIL Image对象，不是张量
        inputs = self.processor(images=image, return_tensors="pt")
        
        # 移除batch维度
        for key in inputs.keys():
            inputs[key] = inputs[key].squeeze()
        
        return {
            **inputs,
            "labels": torch.tensor(label, dtype=torch.long)
        }

def load_config(config_path="config.json"):
    """
    加载训练配置
    
    Args:
        config_path: 配置文件路径
    
    Returns:
        dict: 训练配置
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    return config

def train_model(config):
    """
    训练模型
    
    Args:
        config: 训练配置
    """
    logger.info(f"训练配置: {config}")
    
    # 加载预训练模型和处理器
    logger.info(f"加载预训练模型: {config['model_name']}")
    model = AutoModelForImageClassification.from_pretrained(
        config['model_name'],
        num_labels=config['num_classes'],
        ignore_mismatched_sizes=True
    )
    processor = AutoImageProcessor.from_pretrained(config['model_name'])
    
    # 定义图像变换和数据增强
    # 只保留PIL图像变换，移除ToTensor和Normalize，让processor处理
    transform = transforms.Compose([
        transforms.RandomResizedCrop(config['image_size'], scale=(0.8, 1.0)),  # 随机缩放和裁剪
        transforms.RandomRotation(degrees=15),  # 随机旋转±15度
        transforms.ColorJitter(
            brightness=0.2,  # 随机亮度调整
            contrast=0.2,    # 随机对比度调整
            saturation=0.2,  # 随机饱和度调整
            hue=0.1          # 随机色调调整
        ),
        transforms.RandomHorizontalFlip(p=0.5),  # 随机水平翻转
        transforms.RandomVerticalFlip(p=0.1),    # 随机垂直翻转（较少使用）
        transforms.RandomPerspective(distortion_scale=0.2, p=0.3),  # 随机透视变换
        transforms.GaussianBlur(kernel_size=(5, 9), sigma=(0.1, 2.0)),  # 随机高斯模糊
        # 移除ToTensor和Normalize，让processor处理
    ])
    
    # 创建数据集和数据加载器
    logger.info(f"加载训练数据: {config['train_data_dir']}")
    train_dataset = HandSignDataset(
        data_dir=config['train_data_dir'],
        processor=processor,
        transform=transform
    )
    
    train_dataloader = DataLoader(
        train_dataset,
        batch_size=config['batch_size'],
        shuffle=True,
        num_workers=config['num_workers']
    )
    
    # 创建验证数据集和数据加载器（如果提供）
    val_dataloader = None
    if 'val_data_dir' in config and config['val_data_dir']:
        logger.info(f"加载验证数据: {config['val_data_dir']}")
        val_dataset = HandSignDataset(
            data_dir=config['val_data_dir'],
            processor=processor
        )
        val_dataloader = DataLoader(
            val_dataset,
            batch_size=config['batch_size'],
            shuffle=False,
            num_workers=config['num_workers']
        )
    
    # 设置设备
    device = torch.device(config['device'] if torch.cuda.is_available() else 'cpu')
    model.to(device)
    logger.info(f"使用设备: {device}")
    
    # 定义损失函数和优化器
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(
        model.parameters(),
        lr=config['learning_rate'],
        weight_decay=config['weight_decay']
    )
    
    # 学习率调度器
    scheduler = optim.lr_scheduler.StepLR(
        optimizer,
        step_size=config['lr_step_size'],
        gamma=config['lr_gamma']
    )
    
    # 开始训练
    logger.info("开始训练...")
    best_val_accuracy = 0.0
    
    for epoch in range(config['num_epochs']):
        model.train()
        total_loss = 0.0
        total_correct = 0
        total_samples = 0
        
        progress_bar = tqdm(train_dataloader, desc=f"Epoch {epoch+1}/{config['num_epochs']}")
        
        for batch in progress_bar:
            # 移动数据到设备
            for key in batch.keys():
                batch[key] = batch[key].to(device)
            
            # 前向传播
            outputs = model(**batch)
            loss = outputs.loss
            logits = outputs.logits
            
            # 计算准确率
            _, predicted = torch.max(logits, 1)
            correct = (predicted == batch['labels']).sum().item()
            samples = batch['labels'].size(0)
            
            # 反向传播和优化
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            # 更新统计信息
            total_loss += loss.item() * samples
            total_correct += correct
            total_samples += samples
            
            # 更新进度条
            progress_bar.set_postfix({
                'loss': total_loss / total_samples,
                'accuracy': total_correct / total_samples
            })
        
        # 更新学习率
        scheduler.step()
        
        # 计算训练指标
        train_loss = total_loss / total_samples
        train_accuracy = total_correct / total_samples
        
        logger.info(f"Epoch {epoch+1}/{config['num_epochs']} - "
                   f"Train Loss: {train_loss:.4f}, "
                   f"Train Accuracy: {train_accuracy:.4f}")
        
        # 验证模型
        if val_dataloader:
            model.eval()
            val_loss = 0.0
            val_correct = 0
            val_samples = 0
            
            with torch.no_grad():
                for batch in val_dataloader:
                    # 移动数据到设备
                    for key in batch.keys():
                        batch[key] = batch[key].to(device)
                    
                    # 前向传播
                    outputs = model(**batch)
                    loss = outputs.loss
                    logits = outputs.logits
                    
                    # 计算准确率
                    _, predicted = torch.max(logits, 1)
                    correct = (predicted == batch['labels']).sum().item()
                    samples = batch['labels'].size(0)
                    
                    # 更新统计信息
                    val_loss += loss.item() * samples
                    val_correct += correct
                    val_samples += samples
            
            # 计算验证指标
            val_loss = val_loss / val_samples
            val_accuracy = val_correct / val_samples
            
            logger.info(f"Epoch {epoch+1}/{config['num_epochs']} - "
                       f"Val Loss: {val_loss:.4f}, "
                       f"Val Accuracy: {val_accuracy:.4f}")
            
            # 保存最佳模型
            if val_accuracy > best_val_accuracy:
                best_val_accuracy = val_accuracy
                save_path = os.path.join(config['output_dir'], f"best_model_epoch_{epoch+1}.pt")
                torch.save(model, save_path)
                logger.info(f"保存最佳模型到: {save_path}")
        
        # 保存每个epoch的模型
        if (epoch + 1) % config['save_every'] == 0:
            save_path = os.path.join(config['output_dir'], f"model_epoch_{epoch+1}.pt")
            torch.save(model, save_path)
            logger.info(f"保存模型到: {save_path}")
    
    # 保存最终模型
    final_model_path = os.path.join(config['output_dir'], "final_model.pt")
    torch.save(model, final_model_path)
    logger.info(f"保存最终模型到: {final_model_path}")
    
    # 保存处理器配置
    processor.save_pretrained(config['output_dir'])
    logger.info(f"保存处理器配置到: {config['output_dir']}")
    
    logger.info("训练完成！")

def main():
    """
    主函数
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="手语识别模型训练脚本")
    parser.add_argument("--model_name", help="模型名称")
    parser.add_argument("--config_path", type=str, default="config.json", help="配置文件路径")
    
    args = parser.parse_args()
    
    # 加载配置
    config = load_config(args.config_path)
    
    # 如果指定了模型名称，更新配置
    if args.model_name:
        from bosha.models.model_manager import ModelManager
        manager = ModelManager()
        model_path = manager.get_model_path(args.model_name)
        if model_path:
            print(f"使用模型: {args.model_name} ({model_path})")
    
    # 创建输出目录
    os.makedirs(config['output_dir'], exist_ok=True)
    
    # 开始训练
    train_model(config)

if __name__ == "__main__":
    main()
