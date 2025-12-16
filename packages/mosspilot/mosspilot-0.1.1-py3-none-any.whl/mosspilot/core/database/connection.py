"""
Moss 数据库连接管理器
"""

from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from mosspilot.core.config import settings
from mosspilot.core.database.models import Base


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.database.url
        self.engine: Optional[Engine] = None
        self.SessionLocal: Optional[sessionmaker] = None
        self._initialize_engine()
    
    def _initialize_engine(self) -> None:
        """初始化数据库引擎"""
        engine_kwargs = {
            "echo": settings.database.echo,
        }
        
        # SQLite特殊配置
        if self.database_url.startswith("sqlite"):
            engine_kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False}
            })
        else:
            engine_kwargs.update({
                "pool_size": settings.database.pool_size,
                "max_overflow": settings.database.max_overflow
            })
        
        self.engine = create_engine(self.database_url, **engine_kwargs)
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
    
    def create_tables(self) -> None:
        """创建所有表"""
        if self.engine:
            Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self) -> None:
        """删除所有表"""
        if self.engine:
            Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        if not self.SessionLocal:
            raise RuntimeError("数据库未初始化")
        return self.SessionLocal()
    
    def close(self) -> None:
        """关闭数据库连接"""
        if self.engine:
            self.engine.dispose()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()