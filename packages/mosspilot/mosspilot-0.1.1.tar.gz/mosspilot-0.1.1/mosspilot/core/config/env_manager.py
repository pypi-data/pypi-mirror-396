"""
MossPilot 环境管理器
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path


class EnvironmentManager:
    """环境管理器，处理环境变量和配置文件"""
    
    def __init__(self):
        self.current_env = os.getenv("MOSSPILOT_ENV", "default")
        self.config_dir = Path("configs")
    
    def get_current_env(self) -> str:
        """获取当前环境"""
        return self.current_env
    
    def set_env(self, env: str) -> None:
        """设置当前环境"""
        self.current_env = env
        os.environ["MOSSPILOT_ENV"] = env
    
    def get_config_file_path(self, env: Optional[str] = None) -> Path:
        """获取配置文件路径"""
        env = env or self.current_env
        return self.config_dir / f"{env}.yaml"
    
    def list_available_envs(self) -> list[str]:
        """列出可用的环境"""
        if not self.config_dir.exists():
            return ["default"]
        
        envs = []
        for config_file in self.config_dir.glob("*.yaml"):
            env_name = config_file.stem
            envs.append(env_name)
        
        return envs if envs else ["default"]
    
    def create_env_config(self, env: str, config_data: Dict[str, Any]) -> None:
        """创建新的环境配置文件"""
        import yaml
        
        config_file = self.get_config_file_path(env)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
    
    def get_env_variables(self) -> Dict[str, str]:
        """获取所有MOSSPILOT相关的环境变量"""
        mosspilot_vars = {}
        for key, value in os.environ.items():
            if key.startswith("MOSSPILOT_"):
                mosspilot_vars[key] = value
        return mosspilot_vars
    
    def validate_env(self, env: str) -> bool:
        """验证环境是否有效"""
        return env in self.list_available_envs()


# 全局环境管理器实例
env_manager = EnvironmentManager()