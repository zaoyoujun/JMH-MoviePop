import logging
import os
from pathlib import Path
from typing import Optional


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 日志记录器名称，默认为 None（根记录器）
    
    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.DEBUG)
    
    # 创建日志目录
    log_dir = Path(__file__).parent.parent.parent / "data" / "log"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建格式化器
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(
        log_dir / "app.log",
        encoding="utf-8",
        mode="a"
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger