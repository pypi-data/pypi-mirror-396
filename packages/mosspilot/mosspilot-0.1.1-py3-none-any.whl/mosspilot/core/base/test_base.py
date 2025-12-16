"""
Moss 测试基类
"""

import pytest
from typing import Any, Dict, Optional
from mosspilot.core.config import settings
from mosspilot.core.monitoring import Logger


class TestBase:
    """测试基类，提供通用的测试功能"""
    
    def __init__(self):
        self.logger = Logger()
        self.config = settings
        self._test_data: Dict[str, Any] = {}
    
    def setup_method(self, method):
        """测试方法前置处理"""
        self.logger.info(f"开始执行测试: {method.__name__}")
        self._test_data.clear()
    
    def teardown_method(self, method):
        """测试方法后置处理"""
        self.logger.info(f"测试执行完成: {method.__name__}")
    
    def set_test_data(self, key: str, value: Any) -> None:
        """设置测试数据"""
        self._test_data[key] = value
    
    def get_test_data(self, key: str, default: Any = None) -> Any:
        """获取测试数据"""
        return self._test_data.get(key, default)
    
    def assert_response_status(self, response, expected_status: int) -> None:
        """断言响应状态码"""
        assert response.status_code == expected_status, \
            f"期望状态码 {expected_status}, 实际状态码 {response.status_code}"
    
    def assert_response_contains(self, response, expected_text: str) -> None:
        """断言响应包含指定文本"""
        response_text = response.text if hasattr(response, 'text') else str(response)
        assert expected_text in response_text, \
            f"响应中未找到期望文本: {expected_text}"
    
    def assert_element_exists(self, page, selector: str) -> None:
        """断言页面元素存在"""
        element = page.query_selector(selector)
        assert element is not None, f"未找到元素: {selector}"
    
    def assert_element_text(self, page, selector: str, expected_text: str) -> None:
        """断言元素文本内容"""
        element = page.query_selector(selector)
        assert element is not None, f"未找到元素: {selector}"
        actual_text = element.text_content()
        assert expected_text in actual_text, \
            f"元素文本不匹配，期望: {expected_text}, 实际: {actual_text}"