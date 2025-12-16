#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BOS-HA包的setup.py文件，用于配置PIP包信息
"""

from setuptools import setup, find_packages
import os

# 获取当前目录
here = os.path.abspath(os.path.dirname(__file__))

# 从README.md文件中读取项目描述
with open(os.path.join(here, 'README.md'), 'r', encoding='utf-8') as f:
    long_description = f.read()

# 从__init__.py文件中读取版本信息
with open(os.path.join(here, 'bosha', '__init__.py'), 'r', encoding='utf-8') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.split('=')[1].strip().strip('"')
            break

# 配置包信息
setup(
    # 包的基本信息
    name="BOS-HA",
    version=version,
    author="BOS-HA Team",
    author_email="contact@bos-ha.com",
    description="基于深度学习的手语识别系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bos-ha/BOS-HA",
    license="MIT",
    
    # 包的分类信息
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Multimedia :: Sound/Audio :: Speech",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    
    # 包的关键字
    keywords="sign-language-recognition, deep-learning, computer-vision, openvino",
    
    # 包的安装要求
    python_requires=">=3.7",
    
    # 包的依赖关系
    install_requires=[
        "torch>=2.0.0",
        "torchvision>=0.15.0",
        "transformers>=4.30.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.22.0",
        "websockets>=11.0.0",
        "flask>=2.3.0",
        "flask-socketio>=5.3.0",
        "opencv-python>=4.8.0",
        "numpy>=1.24.0",
        "tqdm>=4.65.0",
        "pillow>=10.0.0",
        "requests>=2.31.0",
        "openvino>=2024.0.0",
        "openvino-dev>=2024.0.0",
        "onnx>=1.14.0",
        "onnxscript>=0.5.0",
    ],
    
    # 包的额外依赖关系
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.3.0",
            "flake8>=6.0.0",
            "mypy>=1.3.0",
            "pytest-cov>=4.1.0",
        ],
    },
    
    # 包的入口点
    entry_points={
        "console_scripts": [
            "bosha-train=bosha.training.train:main",
            "bosha-evaluate=bosha.training.evaluate:main",
            "bosha-convert=bosha.training.convert_to_openvino:main",
            "bosha-server=bosha.server.main:main",
            "bosha-client=bosha.client.web_client.app:main",
            "bosha-model=bosha.models.cli:main",
        ],
    },
    
    # 包的数据文件
    include_package_data=True,
    package_data={
        "bosha": [
            "client/web_client/templates/*",
            "client/web_client/static/*/*",
            "training/config.json",
        ],
    },
    
    # 包的目录结构
    packages=find_packages(exclude=[
        "tests",
        "*.tests",
        "*.tests.*",
        "tests.*",
    ]),
)
