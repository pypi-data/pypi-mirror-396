#!/usr/bin/env python3
"""
模型管理命令行界面

支持以下子命令：
- list: 列出所有可用模型
- list-available: 列出所有可下载模型
- select: 选择要使用的模型
- download: 下载模型
- info: 显示当前使用的模型信息
"""

import argparse
from bosha.models.model_manager import ModelManager

def main():
    """主函数"""
    # 创建模型管理器
    manager = ModelManager()
    
    # 创建命令行解析器
    parser = argparse.ArgumentParser(description="BOS-HA模型管理工具")
    subparsers = parser.add_subparsers(dest="command", help="子命令帮助")
    
    # list 子命令
    list_parser = subparsers.add_parser("list", help="列出所有可用模型")
    
    # list-available 子命令
    list_available_parser = subparsers.add_parser("list-available", help="列出所有可下载模型")
    
    # select 子命令
    select_parser = subparsers.add_parser("select", help="选择要使用的模型")
    select_parser.add_argument("model_name", help="模型名称")
    
    # download 子命令
    download_parser = subparsers.add_parser("download", help="下载模型")
    download_parser.add_argument("--url", help="模型下载URL，默认为配置中的URL")
    download_parser.add_argument("--name", help="模型名称，用于从可用模型列表中获取URL")
    
    # info 子命令
    info_parser = subparsers.add_parser("info", help="显示当前使用的模型信息")
    info_parser.add_argument("model_name", nargs="?", help="模型名称，默认为当前模型")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 根据命令执行相应操作
    if args.command == "list":
        # 列出所有可用模型
        models = manager.list_models()
        if models:
            print("可用模型：")
            print()
            for model in models:
                print(model["name"])
                print(model["path"])
                print()
        else:
            print("没有可用模型，请先下载或添加模型")
    
    elif args.command == "list-available":
        # 列出所有可下载模型
        available_models = manager.list_available_models()
        if available_models:
            print("可下载模型：")
            print()
            for model_id, model_info in available_models.items():
                print(f"{model_id}:")
                print(f"  名称: {model_info['name']}")
                print(f"  类型: {model_info['type']}")
                print(f"  架构: {model_info['arch']}")
                print(f"  描述: {model_info['description']}")
                print(f"  下载链接: {model_info['url']}")
                print()
        else:
            print("没有可下载模型")
    
    elif args.command == "select":
        # 选择模型
        success = manager.select_model(args.model_name)
        if success:
            print(f"已选择模型: {args.model_name}")
        else:
            print(f"选择模型失败: {args.model_name} 不存在")
            # 显示可用模型
            models = manager.list_models()
            if models:
                print("可用模型：")
                for model in models:
                    print(f"  - {model['name']}")
    
    elif args.command == "download":
        # 下载模型
        model_path = manager.download_model(args.url, args.name)
        if model_path:
            print(f"模型下载成功: {model_path}")
        else:
            print("模型下载失败")
    
    elif args.command == "info":
        # 显示模型信息
        if args.model_name:
            info = manager.get_model_info(args.model_name)
        else:
            info = manager.get_model_info()
        
        if info:
            print(f"模型信息：")
            print(f"  名称: {info['name']}")
            print(f"  路径: {info['path']}")
            print(f"  大小: {info['size']} bytes")
            print(f"  类型: {info['type']}")
        else:
            print("模型不存在")
    
    else:
        # 显示帮助信息
        parser.print_help()

if __name__ == "__main__":
    main()
