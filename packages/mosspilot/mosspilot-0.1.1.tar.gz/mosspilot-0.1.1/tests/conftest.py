"""
Moss 测试配置文件
"""

import pytest
from mosspilot.core.config import settings
from mosspilot.core.database import DatabaseManager


@pytest.fixture(scope="session")
def test_config():
    """测试配置fixture"""
    return settings


@pytest.fixture(scope="session")
def db_manager():
    """数据库管理器fixture"""
    return DatabaseManager()


@pytest.fixture(scope="function")
def api_client():
    """API客户端fixture"""
    from mosspilot.modules.api import APIClient
    return APIClient()


@pytest.fixture(scope="function")
def ui_driver():
    """UI驱动器fixture"""
    from mosspilot.modules.ui import UIDriver
    return UIDriver()


@pytest.fixture(scope="function")
def performance_runner():
    """性能测试运行器fixture"""
    from mosspilot.modules.performance import PerformanceRunner
    return PerformanceRunner()