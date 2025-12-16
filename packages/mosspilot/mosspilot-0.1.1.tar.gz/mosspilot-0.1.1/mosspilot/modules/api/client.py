"""
Moss API测试客户端
"""

import httpx
from typing import Dict, Any, Optional, Union
from mosspilot.core.config import settings
from mosspilot.core.monitoring import Logger
from mosspilot.core.base.decorators import retry, log_execution


class APIClient:
    """API测试客户端，基于httpx封装"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = None):
        self.base_url = base_url or settings.api.base_url
        self.timeout = timeout or settings.api.timeout
        self.logger = Logger()
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=settings.api.headers
        )
    
    @log_execution
    @retry(max_attempts=3)
    def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """发送GET请求"""
        self.logger.info(f"发送GET请求: {url}")
        return self.client.get(url, params=params, headers=headers)
    
    @log_execution
    @retry(max_attempts=3)
    def post(self, url: str, data: Optional[Dict[str, Any]] = None,
             json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """发送POST请求"""
        self.logger.info(f"发送POST请求: {url}")
        return self.client.post(url, data=data, json=json, headers=headers)
    
    @log_execution
    @retry(max_attempts=3)
    def put(self, url: str, data: Optional[Dict[str, Any]] = None,
            json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """发送PUT请求"""
        self.logger.info(f"发送PUT请求: {url}")
        return self.client.put(url, data=data, json=json, headers=headers)
    
    @log_execution
    @retry(max_attempts=3)
    def delete(self, url: str, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """发送DELETE请求"""
        self.logger.info(f"发送DELETE请求: {url}")
        return self.client.delete(url, headers=headers)
    
    @log_execution
    @retry(max_attempts=3)
    def patch(self, url: str, data: Optional[Dict[str, Any]] = None,
              json: Optional[Dict[str, Any]] = None,
              headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """发送PATCH请求"""
        self.logger.info(f"发送PATCH请求: {url}")
        return self.client.patch(url, data=data, json=json, headers=headers)
    
    def set_auth(self, auth: Union[httpx.Auth, tuple]) -> None:
        """设置认证信息"""
        self.client.auth = auth
    
    def set_headers(self, headers: Dict[str, str]) -> None:
        """设置请求头"""
        self.client.headers.update(headers)
    
    def set_cookies(self, cookies: Dict[str, str]) -> None:
        """设置Cookie"""
        self.client.cookies.update(cookies)
    
    def close(self) -> None:
        """关闭客户端"""
        if self.client:
            self.client.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()