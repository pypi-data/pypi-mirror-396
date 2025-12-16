"""
Moss 数据库模型
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TestCase(Base):
    """测试用例模型"""
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, comment="测试用例名称")
    description = Column(Text, comment="测试用例描述")
    test_type = Column(String(50), nullable=False, comment="测试类型: api, ui, performance")
    priority = Column(String(20), default="medium", comment="优先级: low, medium, high")
    tags = Column(String(500), comment="标签，逗号分隔")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    is_active = Column(Boolean, default=True, comment="是否激活")
    
    # 关联关系
    executions = relationship("TestExecution", back_populates="test_case")


class TestExecution(Base):
    """测试执行记录模型"""
    __tablename__ = "test_executions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    execution_id = Column(String(100), nullable=False, comment="执行批次ID")
    status = Column(String(20), nullable=False, comment="执行状态: passed, failed, skipped, error")
    start_time = Column(DateTime, nullable=False, comment="开始时间")
    end_time = Column(DateTime, comment="结束时间")
    duration = Column(Float, comment="执行时长(秒)")
    environment = Column(String(50), comment="执行环境")
    
    # 关联关系
    test_case = relationship("TestCase", back_populates="executions")
    results = relationship("TestResult", back_populates="execution")


class TestResult(Base):
    """测试结果详情模型"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=False)
    step_name = Column(String(255), comment="测试步骤名称")
    step_status = Column(String(20), nullable=False, comment="步骤状态")
    expected_result = Column(Text, comment="期望结果")
    actual_result = Column(Text, comment="实际结果")
    error_message = Column(Text, comment="错误信息")
    screenshot_path = Column(String(500), comment="截图路径")
    log_data = Column(Text, comment="日志数据")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    
    # 关联关系
    execution = relationship("TestExecution", back_populates="results")


class Configuration(Base):
    """配置参数模型"""
    __tablename__ = "configurations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, comment="配置键")
    value = Column(Text, comment="配置值")
    description = Column(String(500), comment="配置描述")
    category = Column(String(50), comment="配置分类")
    is_encrypted = Column(Boolean, default=False, comment="是否加密")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")


class Report(Base):
    """报告元数据模型"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    execution_id = Column(String(100), nullable=False, comment="执行批次ID")
    report_type = Column(String(50), nullable=False, comment="报告类型: html, json, xml")
    file_path = Column(String(500), nullable=False, comment="报告文件路径")
    total_cases = Column(Integer, default=0, comment="总用例数")
    passed_cases = Column(Integer, default=0, comment="通过用例数")
    failed_cases = Column(Integer, default=0, comment="失败用例数")
    skipped_cases = Column(Integer, default=0, comment="跳过用例数")
    execution_time = Column(Float, comment="总执行时间")
    generated_at = Column(DateTime, default=datetime.utcnow, comment="生成时间")