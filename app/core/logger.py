import logging
import sys
from typing import Any

class CustomFormatter(logging.Formatter):
    """自定义日志格式化器"""
    
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[38;5;226m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, fmt: str) -> None:
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record: Any) -> str:
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def setup_logger(name: str) -> logging.Logger:
    """设置并返回一个配置好的日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)

    # 设置格式
    fmt = "%(asctime)s - %(name)s - %(message)s"
    console_handler.setFormatter(CustomFormatter(fmt))

    # 确保没有重复的处理器
    logger.handlers.clear()
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger

# 确保这个模块被导入时能正确导出 setup_logger
__all__ = ['setup_logger'] 