"""
Moss 装饰器模块
"""

import functools
import time
from typing import Callable, Any
from mosspilot.core.monitoring import Logger

logger = Logger()


def retry(max_attempts: int = 3, delay: float = 1.0):
    """重试装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"函数 {func.__name__} 重试 {max_attempts} 次后仍然失败: {e}")
                        raise
                    logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}, {delay}秒后重试")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator


def timeout(seconds: float):
    """超时装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import signal
            
            def timeout_handler(signum, frame):
                raise TimeoutError(f"函数 {func.__name__} 执行超时 ({seconds}秒)")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(int(seconds))
            
            try:
                result = func(*args, **kwargs)
                signal.alarm(0)
                return result
            except TimeoutError:
                signal.alarm(0)
                raise
        return wrapper
    return decorator


def log_execution(func: Callable) -> Callable:
    """执行日志装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        logger.info(f"开始执行函数: {func.__name__}")
        
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"函数 {func.__name__} 执行成功，耗时: {execution_time:.2f}秒")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"函数 {func.__name__} 执行失败，耗时: {execution_time:.2f}秒，错误: {e}")
            raise
    return wrapper


def test_case(description: str = "", priority: str = "medium"):
    """测试用例装饰器"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"执行测试用例: {description or func.__name__} (优先级: {priority})")
            return func(*args, **kwargs)
        
        # 添加元数据
        wrapper._test_description = description
        wrapper._test_priority = priority
        return wrapper
    return decorator