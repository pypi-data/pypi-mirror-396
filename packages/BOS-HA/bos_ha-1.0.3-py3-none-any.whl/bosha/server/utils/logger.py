import logging
import os
from datetime import datetime
from typing import Optional

class Logger:
    """日志工具类，提供统一的日志记录功能"""
    
    def __init__(self, name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        初始化日志器
        
        Args:
            name: 日志器名称
            log_level: 日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
            log_file: 日志文件路径，None表示只输出到控制台
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.upper())
        
        # 避免重复添加处理器
        if not self.logger.handlers:
            # 创建格式器
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            
            # 创建控制台处理器
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # 创建文件处理器（如果指定了日志文件）
            if log_file:
                # 确保日志目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir)
                
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        """记录DEBUG级别的日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录INFO级别的日志"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """记录WARNING级别的日志"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """记录ERROR级别的日志"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """记录CRITICAL级别的日志"""
        self.logger.critical(message)
    
    def exception(self, message: str, exc_info: bool = True):
        """记录异常日志"""
        self.logger.exception(message, exc_info=exc_info)
    
    def set_level(self, log_level: str):
        """设置日志级别"""
        self.logger.setLevel(log_level.upper())
    
    @staticmethod
    def get_logger(name: str, log_level: str = "INFO", log_file: Optional[str] = None):
        """
        获取日志器实例
        
        Args:
            name: 日志器名称
            log_level: 日志级别
            log_file: 日志文件路径
            
        Returns:
            Logger: 日志器实例
        """
        return Logger(name, log_level, log_file)
    
    @staticmethod
    def get_default_logger():
        """
        获取默认日志器实例
        
        Returns:
            Logger: 默认日志器实例
        """
        return Logger.get_logger("hand_sign_server")

# 创建默认日志器实例
default_logger = Logger.get_default_logger()

# 导出常用的日志方法
debug = default_logger.debug
info = default_logger.info
warning = default_logger.warning
error = default_logger.error
critical = default_logger.critical
exception = default_logger.exception
set_level = default_logger.set_level
