import json
import logging
import os
from datetime import datetime
from typing import Any, Dict

from src.ntchat_bot.settings import LOG_DIR


def get_logger(name: str = "ntchat_bot") -> logging.Logger:
    """获取日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    if not logger.handlers:
        # 创建日志目录
        os.makedirs(LOG_DIR, exist_ok=True)
        
        # 创建格式化器
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        
        # 文件处理器 - 按日期分割
        file_handler = logging.FileHandler(
            os.path.join(LOG_DIR, f"{datetime.now().strftime('%Y-%m-%d')}.log"),
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    return logger


def log_json(data: Any, filename: str, directory: str = None) -> None:
    """将数据以 JSON 格式写入日志文件"""
    if directory is None:
        directory = LOG_DIR
    
    os.makedirs(directory, exist_ok=True)
    
    filepath = os.path.join(directory, f"{filename}.json")
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[日志] JSON 数据已保存到: {filepath}")
    except Exception as e:
        print(f"[错误] 保存 JSON 日志失败: {e}")


def log_group_members(members: Any, room_id: str) -> None:
    """记录群成员列表"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"group_members_{room_id.replace('@', '_')}_{timestamp}"
    log_json(members, filename)


def log_message(message: Dict[str, Any], msg_type: str = "unknown") -> None:
    """记录消息"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"message_{msg_type}_{timestamp}"
    log_json(message, filename)