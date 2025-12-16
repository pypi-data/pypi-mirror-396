"""
Moss 数据库操作层
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from mosspilot.core.database.models import TestCase, TestExecution, TestResult, Configuration, Report
from mosspilot.core.database.connection import db_manager


class DatabaseOperations:
    """数据库操作类"""
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session or db_manager.get_session()
    
    # 测试用例操作
    def create_test_case(self, name: str, test_type: str, description: str = None, 
                        priority: str = "medium", tags: str = None) -> TestCase:
        """创建测试用例"""
        test_case = TestCase(
            name=name,
            description=description,
            test_type=test_type,
            priority=priority,
            tags=tags
        )
        self.session.add(test_case)
        self.session.commit()
        return test_case
    
    def get_test_case(self, test_case_id: int) -> Optional[TestCase]:
        """获取测试用例"""
        return self.session.query(TestCase).filter(TestCase.id == test_case_id).first()
    
    def get_test_cases_by_type(self, test_type: str) -> List[TestCase]:
        """根据类型获取测试用例"""
        return self.session.query(TestCase).filter(
            TestCase.test_type == test_type,
            TestCase.is_active == True
        ).all()
    
    # 测试执行操作
    def create_test_execution(self, test_case_id: int, execution_id: str, 
                            status: str, start_time, end_time=None, 
                            duration: float = None, environment: str = None) -> TestExecution:
        """创建测试执行记录"""
        execution = TestExecution(
            test_case_id=test_case_id,
            execution_id=execution_id,
            status=status,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            environment=environment
        )
        self.session.add(execution)
        self.session.commit()
        return execution
    
    def update_execution_status(self, execution_id: int, status: str, 
                              end_time=None, duration: float = None) -> None:
        """更新执行状态"""
        execution = self.session.query(TestExecution).filter(
            TestExecution.id == execution_id
        ).first()
        if execution:
            execution.status = status
            if end_time:
                execution.end_time = end_time
            if duration:
                execution.duration = duration
            self.session.commit()
    
    # 测试结果操作
    def create_test_result(self, execution_id: int, step_name: str, step_status: str,
                          expected_result: str = None, actual_result: str = None,
                          error_message: str = None, screenshot_path: str = None,
                          log_data: str = None) -> TestResult:
        """创建测试结果"""
        result = TestResult(
            execution_id=execution_id,
            step_name=step_name,
            step_status=step_status,
            expected_result=expected_result,
            actual_result=actual_result,
            error_message=error_message,
            screenshot_path=screenshot_path,
            log_data=log_data
        )
        self.session.add(result)
        self.session.commit()
        return result
    
    # 配置操作
    def get_config(self, key: str) -> Optional[str]:
        """获取配置值"""
        config = self.session.query(Configuration).filter(
            Configuration.key == key
        ).first()
        return config.value if config else None
    
    def set_config(self, key: str, value: str, description: str = None, 
                   category: str = None) -> Configuration:
        """设置配置值"""
        config = self.session.query(Configuration).filter(
            Configuration.key == key
        ).first()
        
        if config:
            config.value = value
            if description:
                config.description = description
            if category:
                config.category = category
        else:
            config = Configuration(
                key=key,
                value=value,
                description=description,
                category=category
            )
            self.session.add(config)
        
        self.session.commit()
        return config
    
    # 报告操作
    def create_report(self, execution_id: str, report_type: str, file_path: str,
                     total_cases: int = 0, passed_cases: int = 0, 
                     failed_cases: int = 0, skipped_cases: int = 0,
                     execution_time: float = None) -> Report:
        """创建报告记录"""
        report = Report(
            execution_id=execution_id,
            report_type=report_type,
            file_path=file_path,
            total_cases=total_cases,
            passed_cases=passed_cases,
            failed_cases=failed_cases,
            skipped_cases=skipped_cases,
            execution_time=execution_time
        )
        self.session.add(report)
        self.session.commit()
        return report
    
    def get_execution_summary(self, execution_id: str) -> Dict[str, Any]:
        """获取执行摘要"""
        executions = self.session.query(TestExecution).filter(
            TestExecution.execution_id == execution_id
        ).all()
        
        if not executions:
            return {}
        
        total = len(executions)
        passed = sum(1 for e in executions if e.status == "passed")
        failed = sum(1 for e in executions if e.status == "failed")
        skipped = sum(1 for e in executions if e.status == "skipped")
        
        return {
            "execution_id": execution_id,
            "total_cases": total,
            "passed_cases": passed,
            "failed_cases": failed,
            "skipped_cases": skipped,
            "success_rate": (passed / total * 100) if total > 0 else 0
        }
    
    def close(self) -> None:
        """关闭会话"""
        if self.session:
            self.session.close()


# 全局数据库操作实例
db_ops = DatabaseOperations()