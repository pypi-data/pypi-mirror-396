"""
MossPilot CLI 命令行接口
"""

import typer
import os
import shutil
from typing import Optional
from pathlib import Path
from mosspilot import __version__

app = typer.Typer(help="MossPilot 自动化测试框架")

def version_callback(value: bool):
    """显示版本信息"""
    if value:
        typer.echo(f"MossPilot 自动化测试框架 v{__version__}")
        raise typer.Exit()

@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", callback=version_callback, is_eager=True, help="显示版本信息"
    )
):
    """MossPilot 自动化测试框架"""
    pass

@app.command()
def run(
    test_type: str = typer.Argument(..., help="测试类型: api, ui, performance, all"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="配置文件路径"),
    env: Optional[str] = typer.Option("dev", "--env", "-e", help="环境: dev, test, prod"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="详细输出"),
):
    """运行测试"""
    typer.echo(f"运行 {test_type} 测试，环境: {env}")
    
    # 构建pytest命令
    cmd_parts = ["pytest"]
    
    if test_type == "api":
        cmd_parts.extend(["-m", "api", "tests/api_tests/"])
    elif test_type == "ui":
        cmd_parts.extend(["-m", "ui", "tests/ui_tests/"])
    elif test_type == "performance":
        cmd_parts.extend(["-m", "performance", "tests/performance_tests/"])
    elif test_type == "all":
        cmd_parts.append("tests/")
    else:
        typer.echo(f"不支持的测试类型: {test_type}", err=True)
        raise typer.Exit(1)
    
    if verbose:
        cmd_parts.append("-v")
    
    if config:
        cmd_parts.extend(["--config", config])
    
    # 设置环境变量
    import os
    os.environ["MOSSPILOT_ENV"] = env
    
    # 执行pytest
    import subprocess
    result = subprocess.run(cmd_parts)
    raise typer.Exit(result.returncode)

@app.command()
def init(
    name: str = typer.Argument(..., help="项目名称"),
    template: str = typer.Option("basic", "--template", "-t", help="项目模板: basic, api, ui, performance"),
    project_api: Optional[str] = typer.Option(None, "--project-api", help="创建API自动化测试项目"),
    project_ui: Optional[str] = typer.Option(None, "--project-ui", help="创建UI自动化测试项目"),
    project_performance: Optional[str] = typer.Option(None, "--project-performance", help="创建性能测试项目"),
):
    """初始化新的测试项目"""
    # 确定项目类型
    if project_api:
        project_name = project_api
        project_type = "api"
    elif project_ui:
        project_name = project_ui
        project_type = "ui"
    elif project_performance:
        project_name = project_performance
        project_type = "performance"
    else:
        project_name = name
        project_type = template
    
    typer.echo(f"初始化 {project_type} 测试项目: {project_name}")
    
    # 创建项目目录
    project_path = Path(project_name)
    if project_path.exists():
        typer.echo(f"错误: 目录 {project_name} 已存在", err=True)
        raise typer.Exit(1)
    
    try:
        _create_project_structure(project_path, project_type)
        typer.echo(f"✅ 项目 {project_name} 创建成功!")
        typer.echo(f"📁 项目路径: {project_path.absolute()}")
        typer.echo("\n🚀 快速开始:")
        typer.echo(f"  cd {project_name}")
        typer.echo("  uv sync")
        if project_type in ["ui", "basic"]:
            typer.echo("  uv run playwright install")
        typer.echo("  mosspilot run " + ("all" if project_type == "basic" else project_type))
    except Exception as e:
        typer.echo(f"错误: 创建项目失败 - {e}", err=True)
        raise typer.Exit(1)

def _create_project_structure(project_path: Path, project_type: str):
    """创建项目结构"""
    # 创建基础目录结构
    directories = [
        "tests",
        "data/fixtures",
        "configs",
        "reports",
        "logs"
    ]
    
    # 根据项目类型添加特定目录
    if project_type == "api":
        directories.extend(["tests/api_tests"])
    elif project_type == "ui":
        directories.extend(["tests/ui_tests"])
    elif project_type == "performance":
        directories.extend(["tests/performance_tests"])
    else:  # basic
        directories.extend([
            "tests/api_tests",
            "tests/ui_tests",
            "tests/performance_tests"
        ])
    
    # 创建目录
    for directory in directories:
        (project_path / directory).mkdir(parents=True, exist_ok=True)
    
    # 创建配置文件
    _create_project_files(project_path, project_type)

def _create_project_files(project_path: Path, project_type: str):
    """创建项目文件"""
    # pyproject.toml
    pyproject_content = f'''[project]
name = "{project_path.name}"
version = "0.1.0"
description = "{project_type.upper()} 自动化测试项目"
requires-python = ">=3.13"

dependencies = [
    "mosspilot",
    "pytest>=8.0.0",
    "pytest-html>=4.0.0",
'''
    
    if project_type in ["api", "basic"]:
        pyproject_content += '    "httpx>=0.25.0",\n'
    if project_type in ["ui", "basic"]:
        pyproject_content += '    "playwright>=1.40.0",\n'
    if project_type in ["performance", "basic"]:
        pyproject_content += '    "locust>=2.17.0",\n'
    
    pyproject_content += ''']

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
'''
    
    if project_type in ["api", "basic"]:
        pyproject_content += '    "api: API测试标记",\n'
    if project_type in ["ui", "basic"]:
        pyproject_content += '    "ui: UI测试标记",\n'
    if project_type in ["performance", "basic"]:
        pyproject_content += '    "performance: 性能测试标记",\n'
    
    pyproject_content += ']'
    
    (project_path / "pyproject.toml").write_text(pyproject_content)
    
    # README.md
    readme_content = f'''# {project_path.name}

{project_type.upper()} 自动化测试项目

## 快速开始

```bash
# 安装依赖
uv sync

{"# 安装浏览器驱动" if project_type in ["ui", "basic"] else ""}
{"uv run playwright install" if project_type in ["ui", "basic"] else ""}

# 运行测试
mosspilot run {project_type if project_type != "basic" else "all"}
```

## 项目结构

```
{project_path.name}/
├── tests/          # 测试用例
├── data/           # 测试数据
├── configs/        # 配置文件
├── reports/        # 测试报告
└── logs/           # 日志文件
```
'''
    
    (project_path / "README.md").write_text(readme_content)
    
    # 配置文件
    config_content = '''# 测试配置文件
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
'''
    
    (project_path / "configs" / "default.yaml").write_text(config_content)
    
    # 创建示例测试文件
    _create_sample_tests(project_path, project_type)

def _create_sample_tests(project_path: Path, project_type: str):
    """创建示例测试文件"""
    if project_type in ["api", "basic"]:
        api_test = '''import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.api import APIClient, APIAssertions

class TestAPI(TestBase):
    def setup_method(self, method):
        super().setup_method(method)
        self.client = APIClient()
        self.assertions = APIAssertions()
    
    @pytest.mark.api
    def test_example_api(self):
        """示例API测试"""
        response = self.client.get("/api/health")
        self.assertions.assert_status_code(response, 200)
'''
        (project_path / "tests" / "api_tests" / "test_example.py").write_text(api_test)
    
    if project_type in ["ui", "basic"]:
        ui_test = '''import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.ui import UIDriver, UIActions

class TestUI(TestBase):
    def setup_method(self, method):
        super().setup_method(method)
        self.driver = UIDriver()
        self.actions = UIActions(self.driver.page)
    
    @pytest.mark.ui
    def test_example_ui(self):
        """示例UI测试"""
        self.driver.navigate_to("https://example.com")
        assert "Example" in self.driver.get_title()
'''
        (project_path / "tests" / "ui_tests" / "test_example.py").write_text(ui_test)
    
    if project_type in ["performance", "basic"]:
        perf_test = '''import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.performance import PerformanceRunner

class TestPerformance(TestBase):
    @pytest.mark.performance
    def test_example_performance(self):
        """示例性能测试"""
        runner = PerformanceRunner()
        tasks = [{"name": "健康检查", "method": "GET", "url": "/health"}]
        results = runner.run_test(tasks)
        assert results["summary"]["failure_rate"] < 0.05
'''
        (project_path / "tests" / "performance_tests" / "test_example.py").write_text(perf_test)
    
    # conftest.py
    conftest_content = '''import pytest
from mosspilot.core.config import settings

@pytest.fixture(scope="session")
def test_config():
    return settings
'''
    (project_path / "tests" / "conftest.py").write_text(conftest_content)

@app.command()
def report(
    input_dir: str = typer.Argument("reports", help="报告输入目录"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出文件路径"),
):
    """生成测试报告"""
    typer.echo(f"生成报告，输入目录: {input_dir}")
    # TODO: 实现报告生成逻辑

if __name__ == "__main__":
    app()