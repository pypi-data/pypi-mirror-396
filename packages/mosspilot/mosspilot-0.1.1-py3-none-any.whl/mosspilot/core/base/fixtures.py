"""
Moss 通用fixtures模块
"""

import pytest
from typing import Generator, Any
from mosspilot.core.config import settings
from mosspilot.core.database import DatabaseManager
from mosspilot.core.monitoring import Logger


@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    return settings


@pytest.fixture(scope="session")
def logger():
    """日志器fixture"""
    return Logger()


@pytest.fixture(scope="session")
def db_manager():
    """数据库管理器fixture"""
    manager = DatabaseManager()
    yield manager
    manager.close()


@pytest.fixture(scope="function")
def test_data():
    """测试数据fixture"""
    data = {}
    yield data
    data.clear()


@pytest.fixture(scope="function")
def api_client():
    """API客户端fixture"""
    from mosspilot.modules.api import APIClient
    client = APIClient()
    yield client
    client.close()


@pytest.fixture(scope="function")
def ui_driver():
    """UI驱动器fixture"""
    from mosspilot.modules.ui import UIDriver
    driver = UIDriver()
    yield driver
    driver.close()


@pytest.fixture(scope="function")
def performance_runner():
    """性能测试运行器fixture"""
    from mosspilot.modules.performance import PerformanceRunner
    return PerformanceRunner()


@pytest.fixture(autouse=True)
def setup_test_environment(logger):
    """自动设置测试环境"""
    logger.info("测试环境初始化")
    yield
    logger.info("测试环境清理")


@pytest.fixture(scope="function")
def temp_file(tmp_path):
    """临时文件fixture"""
    temp_file = tmp_path / "test_file.txt"
    temp_file.write_text("test content")
    yield temp_file
    # 文件会在tmp_path清理时自动删除


@pytest.fixture(scope="function")
def mock_response():
    """模拟响应fixture"""
    class MockResponse:
        def __init__(self, status_code=200, text="", json_data=None):
            self.status_code = status_code
            self.text = text
            self._json_data = json_data or {}
        
        def json(self):
            return self._json_data
    
    return MockResponse