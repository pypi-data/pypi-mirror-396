"""
Moss API测试工具函数
"""

import json
import uuid
from typing import Dict, Any, Optional, Union
from urllib.parse import urljoin, urlparse
from mosspilot.core.monitoring import Logger


class APIUtils:
    """API测试工具类"""
    
    def __init__(self):
        self.logger = Logger()
    
    @staticmethod
    def generate_request_id() -> str:
        """生成请求ID"""
        return str(uuid.uuid4())
    
    @staticmethod
    def build_url(base_url: str, endpoint: str) -> str:
        """构建完整URL"""
        return urljoin(base_url.rstrip('/') + '/', endpoint.lstrip('/'))
    
    @staticmethod
    def extract_domain(url: str) -> str:
        """提取域名"""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    @staticmethod
    def format_json(data: Union[Dict, str]) -> str:
        """格式化JSON数据"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return data
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    @staticmethod
    def merge_headers(default_headers: Dict[str, str], 
                     custom_headers: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """合并请求头"""
        headers = default_headers.copy()
        if custom_headers:
            headers.update(custom_headers)
        return headers
    
    @staticmethod
    def extract_json_value(json_data: Dict[str, Any], path: str) -> Any:
        """从JSON中提取指定路径的值"""
        keys = path.split('.')
        current = json_data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise KeyError(f"数组索引超出范围: {index}")
            else:
                raise KeyError(f"JSON路径不存在: {path}")
        
        return current
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], required_fields: list) -> bool:
        """验证JSON数据是否包含必需字段"""
        for field in required_fields:
            if field not in data:
                return False
        return True
    
    @staticmethod
    def create_test_data(template: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """基于模板创建测试数据"""
        test_data = template.copy()
        test_data.update(kwargs)
        return test_data
    
    def log_request(self, method: str, url: str, headers: Dict[str, str] = None, 
                   data: Any = None) -> None:
        """记录请求信息"""
        self.logger.info(f"API请求: {method} {url}")
        if headers:
            self.logger.debug(f"请求头: {headers}")
        if data:
            self.logger.debug(f"请求数据: {self.format_json(data)}")
    
    def log_response(self, response) -> None:
        """记录响应信息"""
        self.logger.info(f"API响应: {response.status_code}")
        self.logger.debug(f"响应头: {dict(response.headers)}")
        try:
            response_data = response.json()
            self.logger.debug(f"响应数据: {self.format_json(response_data)}")
        except:
            self.logger.debug(f"响应文本: {response.text[:500]}...")