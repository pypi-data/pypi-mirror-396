"""
Moss 性能测试任务模块
"""

from typing import Dict, Any, Optional, List
from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import time
import json
from mosspilot.core.config import settings
from mosspilot.core.monitoring import Logger
from mosspilot.core.database import db_ops


class PerformanceRunner:
    """性能测试运行器"""
    
    def __init__(self, host: Optional[str] = None, users: Optional[int] = None, 
                 spawn_rate: Optional[int] = None, run_time: Optional[str] = None):
        self.host = host or settings.performance.host
        self.users = users or settings.performance.users
        self.spawn_rate = spawn_rate or settings.performance.spawn_rate
        self.run_time = run_time or settings.performance.run_time
        self.logger = Logger()
        self.env: Optional[Environment] = None
        self.results: Dict[str, Any] = {}
    
    def create_user_class(self, tasks: List[Dict[str, Any]]) -> type:
        """动态创建用户类"""
        
        class DynamicUser(HttpUser):
            wait_time = between(1, 3)
            host = self.host
            
            def on_start(self):
                """用户启动时执行"""
                self.logger = Logger()
                self.logger.info("性能测试用户启动")
            
            def on_stop(self):
                """用户停止时执行"""
                self.logger.info("性能测试用户停止")
        
        # 动态添加任务方法
        for i, task_config in enumerate(tasks):
            method_name = f"task_{i}"
            weight = task_config.get('weight', 1)
            
            def create_task_method(config):
                def task_method(self):
                    self._execute_task(config)
                return task_method
            
            task_method = create_task_method(task_config)
            task_method = task(weight)(task_method)
            setattr(DynamicUser, method_name, task_method)
        
        # 添加任务执行方法
        def _execute_task(self, config: Dict[str, Any]):
            """执行具体任务"""
            method = config.get('method', 'GET').upper()
            url = config.get('url', '/')
            headers = config.get('headers', {})
            data = config.get('data')
            json_data = config.get('json')
            name = config.get('name', f"{method} {url}")
            
            try:
                if method == 'GET':
                    response = self.client.get(url, headers=headers, name=name)
                elif method == 'POST':
                    response = self.client.post(url, headers=headers, data=data, json=json_data, name=name)
                elif method == 'PUT':
                    response = self.client.put(url, headers=headers, data=data, json=json_data, name=name)
                elif method == 'DELETE':
                    response = self.client.delete(url, headers=headers, name=name)
                else:
                    self.logger.warning(f"不支持的HTTP方法: {method}")
                    return
                
                # 验证响应
                expected_status = config.get('expected_status', 200)
                if response.status_code != expected_status:
                    self.logger.warning(f"响应状态码不匹配: 期望 {expected_status}, 实际 {response.status_code}")
                
            except Exception as e:
                self.logger.error(f"任务执行失败: {e}")
        
        setattr(DynamicUser, '_execute_task', _execute_task)
        return DynamicUser
    
    def run_test(self, tasks: List[Dict[str, Any]], execution_id: Optional[str] = None) -> Dict[str, Any]:
        """运行性能测试"""
        self.logger.info(f"开始性能测试: 用户数={self.users}, 生成速率={self.spawn_rate}, 运行时间={self.run_time}")
        
        # 创建用户类
        user_class = self.create_user_class(tasks)
        
        # 创建环境
        self.env = Environment(user_classes=[user_class])
        
        # 设置事件监听器
        self._setup_event_listeners(execution_id)
        
        # 启动测试
        self.env.create_local_runner()
        self.env.runner.start(self.users, spawn_rate=self.spawn_rate)
        
        # 运行指定时间
        if self.run_time.endswith('s'):
            run_seconds = int(self.run_time[:-1])
        elif self.run_time.endswith('m'):
            run_seconds = int(self.run_time[:-1]) * 60
        else:
            run_seconds = int(self.run_time)
        
        time.sleep(run_seconds)
        
        # 停止测试
        self.env.runner.stop()
        
        # 收集结果
        self.results = self._collect_results()
        
        self.logger.info("性能测试完成")
        return self.results
    
    def _setup_event_listeners(self, execution_id: Optional[str] = None):
        """设置事件监听器"""
        
        @events.request.add_listener
        def on_request(request_type, name, response_time, response_length, exception, context, **kwargs):
            """请求事件监听器"""
            if execution_id:
                # 记录到数据库
                status = "failed" if exception else "passed"
                try:
                    db_ops.create_test_result(
                        execution_id=1,  # 临时ID，实际应该从execution记录获取
                        step_name=f"{request_type} {name}",
                        step_status=status,
                        actual_result=f"响应时间: {response_time}ms, 响应长度: {response_length}",
                        error_message=str(exception) if exception else None
                    )
                except Exception as e:
                    self.logger.error(f"记录测试结果失败: {e}")
        
        @events.test_start.add_listener
        def on_test_start(environment, **kwargs):
            """测试开始事件"""
            self.logger.info("性能测试开始")
        
        @events.test_stop.add_listener
        def on_test_stop(environment, **kwargs):
            """测试停止事件"""
            self.logger.info("性能测试停止")
    
    def _collect_results(self) -> Dict[str, Any]:
        """收集测试结果"""
        if not self.env or not self.env.runner:
            return {}
        
        stats = self.env.runner.stats
        
        results = {
            "summary": {
                "total_requests": stats.total.num_requests,
                "total_failures": stats.total.num_failures,
                "average_response_time": stats.total.avg_response_time,
                "min_response_time": stats.total.min_response_time,
                "max_response_time": stats.total.max_response_time,
                "requests_per_second": stats.total.current_rps,
                "failure_rate": stats.total.fail_ratio
            },
            "details": []
        }
        
        # 收集每个请求的详细统计
        for name, entry in stats.entries.items():
            if name != "Aggregated":
                results["details"].append({
                    "name": name,
                    "method": entry.method,
                    "num_requests": entry.num_requests,
                    "num_failures": entry.num_failures,
                    "avg_response_time": entry.avg_response_time,
                    "min_response_time": entry.min_response_time,
                    "max_response_time": entry.max_response_time,
                    "requests_per_second": entry.current_rps,
                    "failure_rate": entry.fail_ratio
                })
        
        return results
    
    def generate_report(self, output_path: str) -> None:
        """生成性能测试报告"""
        if not self.results:
            self.logger.warning("没有测试结果可生成报告")
            return
        
        report_data = {
            "test_config": {
                "host": self.host,
                "users": self.users,
                "spawn_rate": self.spawn_rate,
                "run_time": self.run_time
            },
            "results": self.results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"性能测试报告已生成: {output_path}")


class BasePerformanceUser(HttpUser):
    """基础性能测试用户类"""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """用户启动时执行"""
        self.logger = Logger()
        self.logger.info("性能测试用户启动")
    
    def on_stop(self):
        """用户停止时执行"""
        self.logger.info("性能测试用户停止")
    
    @task(3)
    def get_homepage(self):
        """访问首页"""
        self.client.get("/", name="首页")
    
    @task(2)
    def get_api_data(self):
        """获取API数据"""
        self.client.get("/api/data", name="API数据")
    
    @task(1)
    def post_data(self):
        """提交数据"""
        data = {"test": "data", "timestamp": time.time()}
        self.client.post("/api/submit", json=data, name="提交数据")