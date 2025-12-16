"""
Moss 日志管理器
"""

import sys
import json
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger
from mosspilot.core.config import settings


class Logger:
    """日志管理器，基于loguru封装"""
    
    def __init__(self, name: Optional[str] = None):
        self.name = name or "mosspilot"
        self._setup_logger()
    
    def _setup_logger(self) -> None:
        """设置日志器"""
        # 移除默认处理器
        logger.remove()
        
        # 控制台输出
        logger.add(
            sys.stdout,
            level=settings.monitoring.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            colorize=True
        )
        
        # 文件输出
        log_file = Path(settings.monitoring.log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logger.add(
            str(log_file),
            level=settings.monitoring.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )
        
        # 错误文件单独记录
        error_file = log_file.parent / "error.log"
        logger.add(
            str(error_file),
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            rotation="5 MB",
            retention="30 days"
        )
    
    def debug(self, message: str, **kwargs) -> None:
        """调试日志"""
        logger.bind(name=self.name).debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """信息日志"""
        logger.bind(name=self.name).info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """警告日志"""
        logger.bind(name=self.name).warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """错误日志"""
        logger.bind(name=self.name).error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """严重错误日志"""
        logger.bind(name=self.name).critical(message, **kwargs)
    
    def log_test_start(self, test_name: str, test_type: str) -> None:
        """记录测试开始"""
        self.info(f"测试开始: {test_name} ({test_type})")
    
    def log_test_end(self, test_name: str, status: str, duration: float) -> None:
        """记录测试结束"""
        self.info(f"测试结束: {test_name} - {status} ({duration:.2f}s)")
    
    def log_api_request(self, method: str, url: str, status_code: int, duration: float) -> None:
        """记录API请求"""
        self.info(f"API请求: {method} {url} - {status_code} ({duration:.2f}s)")
    
    def log_ui_action(self, action: str, element: str, success: bool) -> None:
        """记录UI操作"""
        status = "成功" if success else "失败"
        self.info(f"UI操作: {action} {element} - {status}")
    
    def log_performance_metric(self, metric_name: str, value: float, unit: str) -> None:
        """记录性能指标"""
        self.info(f"性能指标: {metric_name} = {value} {unit}")
    
    def log_structured(self, event: str, data: Dict[str, Any]) -> None:
        """记录结构化日志"""
        structured_data = {
            "event": event,
            "timestamp": logger._core.now().isoformat(),
            "data": data
        }
        self.info(f"结构化日志: {json.dumps(structured_data, ensure_ascii=False)}")