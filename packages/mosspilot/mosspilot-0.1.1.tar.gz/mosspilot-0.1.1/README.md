# MossPilot Test Framework

[![PyPI version](https://badge.fury.io/py/mosspilot.svg)](https://badge.fury.io/py/mosspilot)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

全功能自动化测试框架，支持API、UI和性能测试，基于pytest构建，面向企业级使用。

## 核心特性

- 🚀 **全场景覆盖**: API测试(httpx) + UI测试(playwright) + 性能测试(locust)
- 🏗️ **企业级架构**: 模块化设计，支持大规模测试执行
- 📊 **丰富报告**: 自定义HTML报告 + Allure集成
- 🔧 **配置驱动**: 多环境配置，无需修改代码
- 📈 **实时监控**: 企业监控系统集成
- 🔄 **CI/CD集成**: Jenkins原生支持

## 安装

```bash
pip install mosspilot
```

## 快速开始

### 创建新项目

```bash
# 显示版本信息
mosspilot --version

# 创建API测试项目
mosspilot init --project-api my-api-project

# 创建UI测试项目
mosspilot init --project-ui my-ui-project

# 创建性能测试项目
mosspilot init --project-performance my-perf-project

# 创建全功能项目
mosspilot init my-project --template basic
```

### 运行测试

```bash
# API测试
mosspilot run api

# UI测试
mosspilot run ui

# 性能测试
mosspilot run performance

# 全部测试
mosspilot run all

# 指定环境运行
mosspilot run api --env prod
```

## 测试示例

### API测试

```python
import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.api import APIClient, APIAssertions

class TestUserAPI(TestBase):
    def setup_method(self, method):
        super().setup_method(method)
        self.client = APIClient()
        self.assertions = APIAssertions()
    
    @pytest.mark.api
    def test_get_users(self):
        response = self.client.get("/api/users")
        self.assertions.assert_status_code(response, 200)
        self.assertions.assert_json_contains(response, {"users": []})
```

### UI测试

```python
import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.ui import UIDriver, UIActions

class TestLoginPage(TestBase):
    def setup_method(self, method):
        super().setup_method(method)
        self.driver = UIDriver()
        self.actions = UIActions(self.driver.page)
    
    @pytest.mark.ui
    def test_user_login(self):
        self.driver.navigate_to("https://example.com/login")
        self.actions.fill_input("用户名", "testuser")
        self.actions.fill_input("密码", "password123")
        self.actions.click_button("登录")
        self.actions.wait_for_url("*/dashboard")
```

### 性能测试

```python
import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.performance import PerformanceRunner

class TestAPIPerformance(TestBase):
    @pytest.mark.performance
    def test_api_load(self):
        runner = PerformanceRunner()
        tasks = [
            {
                "name": "获取用户列表",
                "method": "GET",
                "url": "/api/users",
                "weight": 3
            }
        ]
        results = runner.run_test(tasks)
        assert results["summary"]["failure_rate"] < 0.05
```

## 配置管理

支持多环境配置，配置文件使用YAML格式：

```yaml
# configs/default.yaml
api:
  base_url: "https://api.example.com"
  timeout: 30

ui:
  browser: "chromium"
  headless: true

performance:
  users: 10
  spawn_rate: 2
  run_time: "60s"
```

## 技术栈

- **Python**: 3.11+
- **测试框架**: pytest
- **HTTP客户端**: httpx
- **浏览器自动化**: playwright
- **性能测试**: locust
- **数据库**: SQLAlchemy
- **模板引擎**: Jinja2
- **CLI工具**: typer

## 文档

- [用户指南](https://github.com/mosspilot-team/mosspilot/blob/main/docs/user_guide.md)
- [API参考](https://github.com/mosspilot-team/mosspilot/blob/main/docs/api_reference.md)

## 贡献

欢迎贡献代码！请查看我们的[贡献指南](https://github.com/mosspilot-team/mosspilot/blob/main/CONTRIBUTING.md)。

## 许可证

本项目采用 [Apache License 2.0](https://github.com/mosspilot-team/mosspilot/blob/main/LICENSE) 许可证。