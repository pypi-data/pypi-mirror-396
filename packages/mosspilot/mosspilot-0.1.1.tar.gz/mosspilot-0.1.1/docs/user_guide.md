# Moss 自动化测试框架用户指南

## 概述

Moss 是一个全功能的自动化测试框架，基于 Python 3.13 和 pytest 构建，支持 API、UI 和性能测试。框架面向企业级使用，提供开箱即用的测试解决方案。

## 核心特性

- 🚀 **全场景覆盖**: API测试(httpx) + UI测试(playwright) + 性能测试(locust)
- 🏗️ **企业级架构**: 模块化设计，支持大规模测试执行
- 📊 **丰富报告**: 自定义HTML报告 + Allure集成
- 🔧 **配置驱动**: 多环境配置，无需修改代码
- 📈 **实时监控**: 企业监控系统集成
- 🔄 **CI/CD集成**: Jenkins原生支持

## 快速开始

### 环境要求

- Python 3.13+
- uv 包管理器

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd mosspilot

# 安装依赖
uv sync

# 安装playwright浏览器
uv run playwright install
```

### 基本使用

```bash
# 显示版本信息
mosspilot --version

# 运行API测试
mosspilot run api

# 运行UI测试
mosspilot run ui

# 运行性能测试
mosspilot run performance

# 运行所有测试
mosspilot run all

# 指定环境运行
mosspilot run api --env prod

# 生成详细报告
mosspilot run api --verbose

# 创建新项目
mosspilot init my-project --template basic

# 创建API测试项目
mosspilot init --project-api my-api-project

# 创建UI测试项目
mosspilot init --project-ui my-ui-project

# 创建性能测试项目
mosspilot init --project-performance my-perf-project
```

## 配置管理

### 环境配置

框架支持多环境配置，配置文件位于 [`configs/`](configs/) 目录：

- [`configs/default.yaml`](configs/default.yaml) - 默认配置
- [`configs/dev.yaml`](configs/dev.yaml) - 开发环境
- [`configs/test.yaml`](configs/test.yaml) - 测试环境
- [`configs/prod.yaml`](configs/prod.yaml) - 生产环境

### 配置示例

```yaml
# API测试配置
api:
  base_url: "https://api.example.com"
  timeout: 30
  retry_count: 3

# UI测试配置
ui:
  browser: "chromium"
  headless: true
  viewport:
    width: 1280
    height: 720

# 性能测试配置
performance:
  users: 10
  spawn_rate: 2
  run_time: "60s"
```

### 环境变量

支持通过环境变量覆盖配置：

```bash
export MOSS_ENV=prod
export MOSS_API_BASE_URL=https://prod-api.example.com
export MOSS_UI_HEADLESS=false
```

## 编写测试用例

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

## 测试标记

使用 pytest 标记来分类和筛选测试：

```python
@pytest.mark.api          # API测试
@pytest.mark.ui           # UI测试
@pytest.mark.performance  # 性能测试
@pytest.mark.slow         # 慢速测试
@pytest.mark.integration  # 集成测试
```

运行特定标记的测试：

```bash
# 只运行API测试
pytest -m api

# 排除慢速测试
pytest -m "not slow"

# 运行API和UI测试
pytest -m "api or ui"
```

## 报告系统

### HTML报告

框架自动生成详细的HTML报告，包含：

- 测试执行摘要
- 测试用例详情
- 错误信息和截图
- 性能指标图表

报告文件保存在 [`reports/`](reports/) 目录。

### Allure报告

支持 Allure 报告集成：

```bash
# 生成Allure报告
pytest --alluredir=reports/allure-results
allure serve reports/allure-results
```

## 数据库集成

框架支持测试数据的数据库存储：

```python
from mosspilot.core.database import db_ops

# 创建测试用例
test_case = db_ops.create_test_case(
    name="用户登录测试",
    test_type="ui",
    description="测试用户登录功能"
)

# 记录测试结果
db_ops.create_test_result(
    execution_id=1,
    step_name="填写用户名",
    step_status="passed"
)
```

## 监控和日志

### 日志配置

框架使用 loguru 进行日志管理：

```python
from mosspilot.core.monitoring import Logger

logger = Logger("my_test")
logger.info("测试开始")
logger.error("测试失败", error="详细错误信息")
```

### 指标收集

```python
from mosspilot.core.monitoring import metrics_collector

# 记录自定义指标
metrics_collector.record_metric("response_time", 150.5, "ms")

# 记录测试执行
metrics_collector.record_test_execution(
    test_name="登录测试",
    status="passed",
    duration=2.5,
    test_type="ui"
)
```

## Jenkins集成

### 配置Jenkins

在 [`configs/default.yaml`](configs/default.yaml) 中配置Jenkins集成：

```yaml
jenkins:
  enabled: true
  callback_url: "http://jenkins.example.com/callback"
  auth_token: "your-auth-token"
```

### 使用Jenkins脚本

```bash
# 通知测试开始
python scripts/jenkins_integration.py --execution-id test_001 --action start

# 通知测试完成
python scripts/jenkins_integration.py --execution-id test_001 --action complete --junit-output reports/junit.xml
```

## 最佳实践

### 测试组织

1. **按功能模块组织测试**：将相关的测试用例放在同一个测试类中
2. **使用描述性的测试名称**：测试方法名应该清楚地描述测试的目的
3. **合理使用标记**：使用pytest标记来分类测试，便于筛选执行

### 数据管理

1. **使用测试数据文件**：将测试数据存储在 [`data/fixtures/`](data/fixtures/) 目录
2. **数据驱动测试**：使用 `@pytest.mark.parametrize` 进行参数化测试
3. **测试数据隔离**：确保测试之间的数据不相互影响

### 错误处理

1. **使用断言方法**：使用框架提供的断言方法，获得更好的错误信息
2. **截图和日志**：在UI测试失败时自动截图，记录详细日志
3. **重试机制**：对不稳定的测试使用重试装饰器

## 故障排除

### 常见问题

1. **浏览器启动失败**
   ```bash
   # 重新安装playwright浏览器
   uv run playwright install
   ```

2. **依赖包冲突**
   ```bash
   # 清理并重新安装依赖
   rm -rf .venv
   uv sync
   ```

3. **数据库连接问题**
   - 检查数据库配置
   - 确认数据库服务正在运行

### 调试技巧

1. **启用详细日志**：设置 `log_level: DEBUG`
2. **使用断点调试**：在测试代码中添加 `import pdb; pdb.set_trace()`
3. **查看浏览器界面**：设置 `headless: false` 观察UI测试执行

## 扩展开发

### 自定义断言

```python
from mosspilot.modules.api import APIAssertions

class CustomAPIAssertions(APIAssertions):
    def assert_custom_format(self, response, expected_format):
        # 自定义断言逻辑
        pass
```

### 自定义报告模板

1. 在 [`core/reporting/templates/`](core/reporting/templates/) 创建新模板
2. 使用Jinja2语法编写HTML模板
3. 在配置中指定模板名称

### 插件开发

框架支持插件扩展，可以开发自定义的测试模块和工具。

## 支持和贡献

- 问题反馈：提交Issue到项目仓库
- 功能建议：通过Pull Request贡献代码
- 文档改进：帮助完善文档和示例

## 许可证

本项目采用 Apache License 2.0 许可证。