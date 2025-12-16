# Moss 自动化测试框架 API 参考

## 核心模块

### mosspilot.core.base

#### TestBase

测试基类，提供通用的测试功能。

```python
from mosspilot.core.base import TestBase

class MyTest(TestBase):
    def test_example(self):
        # 测试逻辑
        pass
```

**方法:**

- `setup_method(method)` - 测试方法前置处理
- `teardown_method(method)` - 测试方法后置处理
- `set_test_data(key, value)` - 设置测试数据
- `get_test_data(key, default=None)` - 获取测试数据
- `assert_response_status(response, expected_status)` - 断言响应状态码
- `assert_response_contains(response, expected_text)` - 断言响应包含文本
- `assert_element_exists(page, selector)` - 断言页面元素存在
- `assert_element_text(page, selector, expected_text)` - 断言元素文本

### mosspilot.core.config

#### Settings

配置管理类，支持多环境配置。

```python
from mosspilot.core.config import settings

# 获取配置值
api_url = settings.api.base_url
ui_browser = settings.ui.browser

# 使用点号分隔的键获取配置
timeout = settings.get("api.timeout", 30)
```

**配置项:**

- `database` - 数据库配置
- `api` - API测试配置
- `ui` - UI测试配置
- `performance` - 性能测试配置
- `reporting` - 报告配置
- `monitoring` - 监控配置
- `jenkins` - Jenkins集成配置

### mosspilot.core.database

#### DatabaseManager

数据库连接管理器。

```python
from mosspilot.core.database import DatabaseManager

db_manager = DatabaseManager()
db_manager.create_tables()  # 创建表
session = db_manager.get_session()  # 获取会话
```

**方法:**

- `create_tables()` - 创建所有表
- `drop_tables()` - 删除所有表
- `get_session()` - 获取数据库会话
- `close()` - 关闭数据库连接

#### DatabaseOperations

数据库操作类。

```python
from mosspilot.core.database import db_ops

# 创建测试用例
test_case = db_ops.create_test_case(
    name="API测试",
    test_type="api",
    description="测试API功能"
)

# 获取执行摘要
summary = db_ops.get_execution_summary("exec_001")
```

**方法:**

- `create_test_case(name, test_type, description, priority, tags)` - 创建测试用例
- `get_test_case(test_case_id)` - 获取测试用例
- `create_test_execution(test_case_id, execution_id, status, start_time)` - 创建执行记录
- `create_test_result(execution_id, step_name, step_status)` - 创建测试结果
- `get_execution_summary(execution_id)` - 获取执行摘要

## API测试模块

### mosspilot.modules.api.APIClient

HTTP客户端封装，基于httpx。

```python
from mosspilot.modules.api import APIClient

client = APIClient(base_url="https://api.example.com")
response = client.get("/users")
client.close()
```

**方法:**

- `get(url, params, headers)` - 发送GET请求
- `post(url, data, json, headers)` - 发送POST请求
- `put(url, data, json, headers)` - 发送PUT请求
- `delete(url, headers)` - 发送DELETE请求
- `patch(url, data, json, headers)` - 发送PATCH请求
- `set_auth(auth)` - 设置认证信息
- `set_headers(headers)` - 设置请求头
- `close()` - 关闭客户端

### mosspilot.modules.api.APIAssertions

API测试断言类。

```python
from mosspilot.modules.api import APIAssertions

assertions = APIAssertions()
assertions.assert_status_code(response, 200)
assertions.assert_json_contains(response, {"id": 1})
```

**方法:**

- `assert_status_code(response, expected)` - 断言状态码
- `assert_response_time(response, max_time)` - 断言响应时间
- `assert_json_contains(response, expected)` - 断言JSON包含字段
- `assert_json_schema(response, schema)` - 断言JSON模式
- `assert_header_exists(response, header_name)` - 断言响应头存在
- `assert_header_value(response, header_name, expected_value)` - 断言响应头值
- `assert_text_contains(response, expected_text)` - 断言文本包含
- `assert_json_path_value(response, json_path, expected_value)` - 断言JSON路径值
- `assert_json_array_length(response, json_path, expected_length)` - 断言数组长度

## UI测试模块

### mosspilot.modules.ui.UIDriver

浏览器驱动器，基于playwright。

```python
from mosspilot.modules.ui import UIDriver

driver = UIDriver(browser_type="chromium", headless=True)
driver.navigate_to("https://example.com")
driver.click("#login-btn")
driver.close()
```

**方法:**

- `navigate_to(url)` - 导航到URL
- `click(selector, timeout)` - 点击元素
- `fill(selector, value, timeout)` - 填充输入框
- `type_text(selector, text, delay)` - 逐字符输入
- `press_key(key)` - 按键
- `wait_for_element(selector, timeout)` - 等待元素出现
- `wait_for_url(url_pattern, timeout)` - 等待URL匹配
- `get_text(selector)` - 获取元素文本
- `get_attribute(selector, attribute)` - 获取元素属性
- `is_visible(selector)` - 检查元素可见性
- `screenshot(path, full_page)` - 截图
- `close()` - 关闭浏览器

### mosspilot.modules.ui.UIActions

UI操作封装类。

```python
from mosspilot.modules.ui import UIActions

actions = UIActions(page)
actions.click_button("登录")
actions.fill_input("用户名", "testuser")
```

**方法:**

- `click_button(text, timeout)` - 点击按钮
- `click_link(text, timeout)` - 点击链接
- `fill_input(label, value, timeout)` - 填充输入框
- `select_dropdown(label, value, timeout)` - 选择下拉框
- `check_checkbox(label, timeout)` - 勾选复选框
- `wait_for_text(text, timeout)` - 等待文本出现
- `get_table_data(table_selector)` - 获取表格数据
- `upload_file(file_input_selector, file_path)` - 上传文件
- `take_screenshot(path, full_page)` - 截图

## 性能测试模块

### mosspilot.modules.performance.PerformanceRunner

性能测试运行器，基于locust。

```python
from mosspilot.modules.performance import PerformanceRunner

runner = PerformanceRunner(
    host="https://api.example.com",
    users=10,
    spawn_rate=2,
    run_time="60s"
)

tasks = [
    {
        "name": "获取用户",
        "method": "GET",
        "url": "/api/users",
        "weight": 3
    }
]

results = runner.run_test(tasks, "perf_001")
```

**方法:**

- `run_test(tasks, execution_id)` - 运行性能测试
- `generate_report(output_path)` - 生成性能报告

**任务配置:**

- `name` - 任务名称
- `method` - HTTP方法
- `url` - 请求URL
- `weight` - 任务权重
- `headers` - 请求头
- `data` - 请求数据
- `json` - JSON数据
- `expected_status` - 期望状态码

### mosspilot.modules.performance.PerformanceMetrics

性能指标收集器。

```python
from mosspilot.modules.performance import metrics_collector

metrics_collector.record_metric("response_time", 150.5, "ms")
summary = metrics_collector.get_metrics_summary()
```

**方法:**

- `record_metric(name, value, unit, tags)` - 记录指标
- `record_test_execution(test_name, status, duration, test_type)` - 记录测试执行
- `get_metrics_summary()` - 获取指标摘要
- `export_metrics(format_type)` - 导出指标数据
- `flush_metrics()` - 刷新指标到外部系统

## 报告系统

### mosspilot.core.reporting.HTMLReporter

HTML报告生成器。

```python
from mosspilot.core.reporting import HTMLReporter

reporter = HTMLReporter()
report_path = reporter.generate_report("exec_001", "default")
```

**方法:**

- `generate_report(execution_id, template_name)` - 生成HTML报告

## 监控系统

### mosspilot.core.monitoring.Logger

日志管理器，基于loguru。

```python
from mosspilot.core.monitoring import Logger

logger = Logger("my_module")
logger.info("测试开始")
logger.error("测试失败", error="详细信息")
```

**方法:**

- `debug(message, **kwargs)` - 调试日志
- `info(message, **kwargs)` - 信息日志
- `warning(message, **kwargs)` - 警告日志
- `error(message, **kwargs)` - 错误日志
- `critical(message, **kwargs)` - 严重错误日志
- `log_test_start(test_name, test_type)` - 记录测试开始
- `log_test_end(test_name, status, duration)` - 记录测试结束
- `log_api_request(method, url, status_code, duration)` - 记录API请求
- `log_ui_action(action, element, success)` - 记录UI操作

### mosspilot.core.monitoring.MetricsCollector

指标收集器。

```python
from mosspilot.core.monitoring import metrics_collector

metrics_collector.record_metric("test_count", 1, "count")
metrics_collector.flush_metrics()
```

**方法:**

- `record_metric(name, value, unit, tags)` - 记录指标
- `record_test_execution(test_name, status, duration, test_type)` - 记录测试执行
- `record_api_request(method, endpoint, status_code, duration)` - 记录API请求
- `get_metrics_summary()` - 获取指标摘要
- `send_to_webhook(data)` - 发送到webhook
- `flush_metrics()` - 刷新指标

## 装饰器

### mosspilot.core.base.decorators

测试装饰器模块。

```python
from mosspilot.core.base.decorators import retry, timeout, log_execution, test_case

@retry(max_attempts=3, delay=1.0)
@timeout(30)
@log_execution
@test_case(description="用户登录测试", priority="high")
def test_user_login():
    # 测试逻辑
    pass
```

**装饰器:**

- `@retry(max_attempts, delay)` - 重试装饰器
- `@timeout(seconds)` - 超时装饰器
- `@log_execution` - 执行日志装饰器
- `@test_case(description, priority)` - 测试用例装饰器

## Jenkins集成

### scripts.jenkins_integration.JenkinsIntegration

Jenkins集成类。

```python
from scripts.jenkins_integration import JenkinsIntegration

jenkins = JenkinsIntegration()
jenkins.notify_test_start("exec_001", "build_123")
jenkins.notify_test_complete("exec_001", summary)
```

**方法:**

- `notify_test_start(execution_id, build_number)` - 通知测试开始
- `notify_test_complete(execution_id, summary)` - 通知测试完成
- `notify_test_failure(execution_id, error_message)` - 通知测试失败
- `generate_junit_xml(execution_id, output_path)` - 生成JUnit XML报告

## 命令行接口

### mosspilot.cli

命令行工具。

```bash
# 显示版本信息
mosspilot --version

# 运行测试
mosspilot run api --env prod --verbose
mosspilot run ui --config custom.yaml
mosspilot run performance
mosspilot run all

# 初始化项目
mosspilot init my_project --template basic

# 创建专门的测试项目
mosspilot init --project-api my-api-project
mosspilot init --project-ui my-ui-project
mosspilot init --project-performance my-perf-project

# 生成报告
mosspilot report reports/ --output final_report.html
```

**全局选项:**

- `--version` - 显示版本信息

**命令:**

- `run <test_type>` - 运行测试
  - `--env` - 指定环境
  - `--config` - 指定配置文件
  - `--verbose` - 详细输出
- `init <name>` - 初始化项目
  - `--template` - 项目模板 (basic, api, ui, performance)
  - `--project-api` - 创建API自动化测试项目
  - `--project-ui` - 创建UI自动化测试项目
  - `--project-performance` - 创建性能测试项目
- `report <input_dir>` - 生成报告
  - `--output` - 输出文件

## 数据模型

### 测试用例模型 (TestCase)

```python
test_case = TestCase(
    name="用户登录测试",
    description="测试用户登录功能",
    test_type="ui",
    priority="high",
    tags="login,authentication"
)
```

**字段:**

- `id` - 主键ID
- `name` - 测试用例名称
- `description` - 描述
- `test_type` - 测试类型 (api/ui/performance)
- `priority` - 优先级 (low/medium/high)
- `tags` - 标签
- `created_at` - 创建时间
- `updated_at` - 更新时间
- `is_active` - 是否激活

### 测试执行模型 (TestExecution)

```python
execution = TestExecution(
    test_case_id=1,
    execution_id="exec_001",
    status="passed",
    start_time=datetime.now(),
    duration=2.5,
    environment="test"
)
```

**字段:**

- `id` - 主键ID
- `test_case_id` - 测试用例ID
- `execution_id` - 执行批次ID
- `status` - 执行状态 (passed/failed/skipped/error)
- `start_time` - 开始时间
- `end_time` - 结束时间
- `duration` - 执行时长
- `environment` - 执行环境

## 配置参考

### 默认配置结构

```yaml
# 数据库配置
database:
  url: "sqlite:///mosspilot.db"
  echo: false
  pool_size: 5
  max_overflow: 10

# API测试配置
api:
  base_url: "https://api.example.com"
  timeout: 30
  retry_count: 3
  headers:
    User-Agent: "Moss-TestFramework/0.1.0"

# UI测试配置
ui:
  browser: "chromium"  # chromium/firefox/webkit
  headless: true
  viewport:
    width: 1280
    height: 720
  timeout: 30000
  screenshot_on_failure: true

# 性能测试配置
performance:
  users: 10
  spawn_rate: 2
  run_time: "60s"
  host: "https://example.com"

# 报告配置
reporting:
  output_dir: "reports"
  html_template: "default"
  include_screenshots: true
  include_logs: true

# 监控配置
monitoring:
  log_level: "INFO"  # DEBUG/INFO/WARNING/ERROR/CRITICAL
  log_file: "logs/mosspilot.log"
  metrics_enabled: true
  webhook_url: null

# Jenkins集成配置
jenkins:
  enabled: false
  callback_url: null
  auth_token: null
```

## 环境变量

支持的环境变量：

- `MOSS_ENV` - 当前环境 (dev/test/prod)
- `MOSS_DB_URL` - 数据库连接URL
- `MOSS_API_BASE_URL` - API基础URL
- `MOSS_UI_BROWSER` - UI测试浏览器
- `MOSS_UI_HEADLESS` - 是否无头模式
- `MOSS_LOG_LEVEL` - 日志级别
- `MOSS_JENKINS_ENABLED` - 是否启用Jenkins集成

## 错误处理

### 常见异常

- `AssertionError` - 断言失败
- `TimeoutError` - 超时错误
- `ConnectionError` - 连接错误
- `FileNotFoundError` - 文件未找到
- `ConfigurationError` - 配置错误

### 错误处理最佳实践

```python
try:
    response = client.get("/api/users")
    assertions.assert_status_code(response, 200)
except AssertionError as e:
    logger.error(f"断言失败: {e}")
    raise
except Exception as e:
    logger.error(f"未知错误: {e}")
    raise
```

## 扩展开发

### 自定义断言

```python
from mosspilot.modules.api import APIAssertions

class CustomAssertions(APIAssertions):
    def assert_custom_format(self, response, expected_format):
        """自定义格式断言"""
        actual_format = self._detect_format(response)
        assert actual_format == expected_format, \
            f"格式不匹配: 期望 {expected_format}, 实际 {actual_format}"
```

### 自定义报告模板

1. 在 [`core/reporting/templates/`](core/reporting/templates/) 创建模板文件
2. 使用Jinja2语法编写HTML模板
3. 在配置中指定模板名称

```yaml
reporting:
  html_template: "custom_template"
```

### 插件开发

框架支持插件扩展，可以开发自定义的测试模块：

```python
# 自定义测试模块
class CustomTestModule:
    def __init__(self):
        self.logger = Logger("custom")
    
    def run_custom_test(self):
        # 自定义测试逻辑
        pass
```

## 版本信息

- 当前版本: 0.1.0
- Python要求: 3.13+
- 主要依赖: pytest, httpx, playwright, locust
- 许可证: Apache License 2.0