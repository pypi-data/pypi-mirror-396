"""
Moss API断言模块
"""

import json
from typing import Any, Dict, List, Union, Optional
import httpx
from mosspilot.core.monitoring import Logger


class APIAssertions:
    """API测试断言类"""
    
    def __init__(self):
        self.logger = Logger()
    
    def assert_status_code(self, response: httpx.Response, expected: int) -> None:
        """断言状态码"""
        actual = response.status_code
        assert actual == expected, f"状态码不匹配: 期望 {expected}, 实际 {actual}"
        self.logger.info(f"状态码断言通过: {actual}")
    
    def assert_response_time(self, response: httpx.Response, max_time: float) -> None:
        """断言响应时间"""
        elapsed = response.elapsed.total_seconds()
        assert elapsed <= max_time, f"响应时间超时: {elapsed}s > {max_time}s"
        self.logger.info(f"响应时间断言通过: {elapsed}s")
    
    def assert_json_contains(self, response: httpx.Response, expected: Dict[str, Any]) -> None:
        """断言JSON响应包含指定字段"""
        try:
            actual = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        for key, value in expected.items():
            assert key in actual, f"JSON中缺少字段: {key}"
            assert actual[key] == value, f"字段值不匹配: {key}, 期望 {value}, 实际 {actual[key]}"
        
        self.logger.info(f"JSON字段断言通过: {list(expected.keys())}")
    
    def assert_json_schema(self, response: httpx.Response, schema: Dict[str, Any]) -> None:
        """断言JSON响应符合指定模式"""
        try:
            actual = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        self._validate_schema(actual, schema)
        self.logger.info("JSON模式断言通过")
    
    def assert_header_exists(self, response: httpx.Response, header_name: str) -> None:
        """断言响应头存在"""
        assert header_name in response.headers, f"响应头不存在: {header_name}"
        self.logger.info(f"响应头断言通过: {header_name}")
    
    def assert_header_value(self, response: httpx.Response, header_name: str, expected_value: str) -> None:
        """断言响应头值"""
        actual_value = response.headers.get(header_name)
        assert actual_value == expected_value, \
            f"响应头值不匹配: {header_name}, 期望 {expected_value}, 实际 {actual_value}"
        self.logger.info(f"响应头值断言通过: {header_name}={expected_value}")
    
    def assert_text_contains(self, response: httpx.Response, expected_text: str) -> None:
        """断言响应文本包含指定内容"""
        actual_text = response.text
        assert expected_text in actual_text, f"响应文本不包含: {expected_text}"
        self.logger.info(f"文本包含断言通过: {expected_text}")
    
    def assert_json_path_value(self, response: httpx.Response, json_path: str, expected_value: Any) -> None:
        """断言JSON路径值"""
        try:
            actual = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        value = self._get_json_path_value(actual, json_path)
        assert value == expected_value, \
            f"JSON路径值不匹配: {json_path}, 期望 {expected_value}, 实际 {value}"
        self.logger.info(f"JSON路径断言通过: {json_path}={expected_value}")
    
    def assert_json_array_length(self, response: httpx.Response, json_path: str, expected_length: int) -> None:
        """断言JSON数组长度"""
        try:
            actual = response.json()
        except json.JSONDecodeError:
            raise AssertionError("响应不是有效的JSON格式")
        
        array = self._get_json_path_value(actual, json_path)
        assert isinstance(array, list), f"JSON路径不是数组: {json_path}"
        actual_length = len(array)
        assert actual_length == expected_length, \
            f"数组长度不匹配: {json_path}, 期望 {expected_length}, 实际 {actual_length}"
        self.logger.info(f"数组长度断言通过: {json_path} length={expected_length}")
    
    def _validate_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """验证数据模式"""
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "object" and not isinstance(data, dict):
                raise AssertionError(f"类型不匹配: 期望 object, 实际 {type(data).__name__}")
            elif expected_type == "array" and not isinstance(data, list):
                raise AssertionError(f"类型不匹配: 期望 array, 实际 {type(data).__name__}")
            elif expected_type == "string" and not isinstance(data, str):
                raise AssertionError(f"类型不匹配: 期望 string, 实际 {type(data).__name__}")
            elif expected_type == "number" and not isinstance(data, (int, float)):
                raise AssertionError(f"类型不匹配: 期望 number, 实际 {type(data).__name__}")
        
        if "properties" in schema and isinstance(data, dict):
            for prop, prop_schema in schema["properties"].items():
                if prop in data:
                    self._validate_schema(data[prop], prop_schema)
    
    def _get_json_path_value(self, data: Any, path: str) -> Any:
        """获取JSON路径值"""
        keys = path.split('.')
        current = data
        
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and key.isdigit():
                index = int(key)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    raise AssertionError(f"数组索引超出范围: {index}")
            else:
                raise AssertionError(f"JSON路径不存在: {path}")
        
        return current