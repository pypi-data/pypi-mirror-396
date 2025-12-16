"""
Moss 配置管理系统
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class DatabaseConfig(BaseModel):
    """数据库配置"""
    url: str = "sqlite:///mosspilot.db"
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class APIConfig(BaseModel):
    """API测试配置"""
    base_url: str = "https://api.example.com"
    timeout: int = 30
    retry_count: int = 3
    headers: Dict[str, str] = Field(default_factory=lambda: {"User-Agent": "Moss-TestFramework/0.1.0"})


class UIConfig(BaseModel):
    """UI测试配置"""
    browser: str = "chromium"
    headless: bool = True
    viewport: Dict[str, int] = Field(default_factory=lambda: {"width": 1280, "height": 720})
    timeout: int = 30000
    screenshot_on_failure: bool = True


class PerformanceConfig(BaseModel):
    """性能测试配置"""
    users: int = 10
    spawn_rate: int = 2
    run_time: str = "60s"
    host: str = "https://example.com"


class ReportingConfig(BaseModel):
    """报告配置"""
    output_dir: str = "reports"
    html_template: str = "default"
    include_screenshots: bool = True
    include_logs: bool = True


class MonitoringConfig(BaseModel):
    """监控配置"""
    log_level: str = "INFO"
    log_file: str = "logs/mosspilot.log"
    metrics_enabled: bool = True
    webhook_url: Optional[str] = None


class JenkinsConfig(BaseModel):
    """Jenkins集成配置"""
    enabled: bool = False
    callback_url: Optional[str] = None
    auth_token: Optional[str] = None


class Settings(BaseModel):
    """主配置类"""
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    ui: UIConfig = Field(default_factory=UIConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    jenkins: JenkinsConfig = Field(default_factory=JenkinsConfig)

    @classmethod
    def load_from_file(cls, config_path: Optional[str] = None) -> "Settings":
        """从配置文件加载设置"""
        if config_path is None:
            env = os.getenv("MOSS_ENV", "default")
            config_path = f"configs/{env}.yaml"
        
        config_file = Path(config_path)
        if not config_file.exists():
            # 如果配置文件不存在，使用默认配置
            return cls()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        return cls(**config_data)

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值，支持点号分隔的嵌套键"""
        keys = key.split('.')
        value = self
        
        for k in keys:
            if hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
        
        return value

    def update_from_env(self) -> None:
        """从环境变量更新配置"""
        env_mappings = {
            "MOSS_DB_URL": "database.url",
            "MOSS_API_BASE_URL": "api.base_url",
            "MOSS_UI_BROWSER": "ui.browser",
            "MOSS_UI_HEADLESS": "ui.headless",
            "MOSS_LOG_LEVEL": "monitoring.log_level",
            "MOSS_JENKINS_ENABLED": "jenkins.enabled",
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config_key, env_value)

    def _set_nested_value(self, key: str, value: str) -> None:
        """设置嵌套配置值"""
        keys = key.split('.')
        obj = self
        
        for k in keys[:-1]:
            obj = getattr(obj, k)
        
        # 类型转换
        final_key = keys[-1]
        current_value = getattr(obj, final_key)
        
        if isinstance(current_value, bool):
            value = value.lower() in ('true', '1', 'yes', 'on')
        elif isinstance(current_value, int):
            value = int(value)
        elif isinstance(current_value, float):
            value = float(value)
        
        setattr(obj, final_key, value)


# 全局配置实例
settings = Settings.load_from_file()
settings.update_from_env()