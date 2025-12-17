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
    list_parser.add_argument("--type", help="按类型过滤模型，可选值：pytorch, onnx, openvino")
    list_parser.add_argument("--all", action="store_true", help="列出所有模型，包括已下载和未下载的")
    
    # list-available 子命令
    list_available_parser = subparsers.add_parser("list-available", help="列出所有可下载模型")
    
    # select 子命令
    select_parser = subparsers.add_parser("select", help="选择要使用的模型")
    select_parser.add_argument("model_name", help="模型名称")
    
    # download 子命令
    download_parser = subparsers.add_parser("download", help="下载模型")
    download_parser.add_argument("model_names", nargs="*", help="要下载的模型名称列表")
    download_parser.add_argument("--url", help="模型下载URL，默认为配置中的URL")
    download_parser.add_argument("--all", action="store_true", help="下载所有可下载模型")
    download_parser.add_argument("--force", action="store_true", help="强制重新下载已存在的模型")
    download_parser.add_argument("--max-workers", type=int, default=3, help="并发下载的最大工作线程数")
    
    # info 子命令
    info_parser = subparsers.add_parser("info", help="显示当前使用的模型信息")
    info_parser.add_argument("model_name", nargs="?", help="模型名称，默认为当前模型")
    
    # validate 子命令
    validate_parser = subparsers.add_parser("validate", help="验证模型是否有效")
    validate_parser.add_argument("model_name", nargs="?", help="要验证的模型名称，默认为所有已下载模型")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 根据命令执行相应操作
    if args.command == "list":
        # 列出所有可用模型
        if args.all:
            models = manager.list_all_models()
            print("所有模型：")
            print()
            for model in models:
                print(f"{model['name']}:")
                print(f"  状态: {model['status']}")
                if model['status'] == "已下载":
                    print(f"  路径: {model['path']}")
                    print(f"  大小: {model['size_human']}")
                    print(f"  类型: {model['type']}")
                print(f"  架构: {model['arch']}")
                print(f"  描述: {model['description'][:50]}...")
                print()
        else:
            models = manager.list_models(model_type=args.type)
            if models:
                print("可用模型：")
                print()
                for model in models:
                    print(f"{model['name']}:")
                    print(f"  路径: {model['path']}")
                    print(f"  大小: {model['size_human']}")
                    print(f"  类型: {model['type']}")
                    print(f"  架构: {model['arch']}")
                    print(f"  描述: {model['description'][:50]}...")
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
                print(f"  描述: {model_info['description'][:50]}...")
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
        if args.all:
            # 下载所有模型（使用并发下载）
            model_paths = manager.download_all(force=args.force, max_workers=args.max_workers)
            print(f"\n=== 下载完成 ===")
            print(f"成功下载 {len(model_paths)} 个模型")
        elif args.model_names:
            # 下载多个指定模型（使用并发下载）
            model_paths = manager.download_models(args.model_names, force=args.force, max_workers=args.max_workers)
            print(f"\n=== 下载完成 ===")
            print(f"成功下载 {len(model_paths)} 个模型")
        else:
            # 下载单个模型
            model_path = manager.download_model(args.url, force=args.force)
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
            print(f"  状态: {info['status']}")
            if "path" in info:
                print(f"  路径: {info['path']}")
            if "size_human" in info:
                print(f"  大小: {info['size_human']}")
            if "type" in info:
                print(f"  类型: {info['type']}")
            if "arch" in info:
                print(f"  架构: {info['arch']}")
            if "description" in info:
                print(f"  描述: {info['description']}")
            if "download_time" in info:
                print(f"  下载时间: {info['download_time']}")
            if "url" in info:
                print(f"  下载链接: {info['url']}")
        else:
            print("模型不存在")
    
    elif args.command == "validate":
        # 验证模型
        if args.model_name:
            # 验证单个模型
            model_info = manager.get_model_info(args.model_name)
            if model_info and "path" in model_info:
                print(f"=== 验证模型: {args.model_name} ===")
                result = manager.validate_model(model_info["path"])
                print(f"验证结果: {'成功' if result else '失败'}")
            else:
                print(f"模型 {args.model_name} 不存在或未下载")
        else:
            # 验证所有已下载模型
            print("=== 验证所有已下载模型 ===")
            results = manager.validate_all_models()
            
            success_count = sum(1 for r in results if r["valid"])
            total_count = len(results)
            
            print(f"\n=== 验证结果汇总 ===")
            print(f"总模型数: {total_count}")
            print(f"成功: {success_count}")
            print(f"失败: {total_count - success_count}")
            
            if success_count != total_count:
                print("\n失败的模型:")
                for result in results:
                    if not result["valid"]:
                        print(f"  - {result['name']} ({result['type']})")
    
    else:
        # 显示帮助信息
        parser.print_help()

if __name__ == "__main__":
    main()
