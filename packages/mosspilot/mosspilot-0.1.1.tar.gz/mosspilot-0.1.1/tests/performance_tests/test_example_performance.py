"""
性能测试示例
"""

import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.performance import PerformanceRunner


class TestExamplePerformance(TestBase):
    """性能测试示例类"""
    
    def setup_method(self, method):
        """测试前置处理"""
        super().setup_method(method)
        self.runner = PerformanceRunner()
    
    @pytest.mark.performance
    def test_api_load_performance(self):
        """测试API负载性能"""
        # 定义性能测试任务
        tasks = [
            {
                "name": "获取用户列表",
                "method": "GET",
                "url": "/api/users",
                "weight": 3,
                "expected_status": 200
            },
            {
                "name": "创建用户",
                "method": "POST",
                "url": "/api/users",
                "json": {
                    "name": "性能测试用户",
                    "email": "perf@test.com"
                },
                "weight": 1,
                "expected_status": 201
            }
        ]
        
        # 运行性能测试
        results = self.runner.run_test(
            tasks=tasks,
            execution_id="perf_test_001"
        )
        
        # 验证性能指标
        summary = results["summary"]
        assert summary["total_requests"] > 0
        assert summary["failure_rate"] < 0.05  # 失败率小于5%
        assert summary["average_response_time"] < 1000  # 平均响应时间小于1秒
        assert summary["requests_per_second"] > 10  # RPS大于10
    
    @pytest.mark.performance
    def test_concurrent_user_simulation(self):
        """测试并发用户模拟"""
        tasks = [
            {
                "name": "用户登录",
                "method": "POST",
                "url": "/api/login",
                "json": {
                    "username": "testuser",
                    "password": "password123"
                },
                "weight": 1
            },
            {
                "name": "浏览商品",
                "method": "GET",
                "url": "/api/products",
                "weight": 5
            },
            {
                "name": "添加到购物车",
                "method": "POST",
                "url": "/api/cart/add",
                "json": {
                    "product_id": 1,
                    "quantity": 1
                },
                "weight": 2
            }
        ]
        
        # 配置高并发测试
        self.runner.users = 50
        self.runner.spawn_rate = 5
        self.runner.run_time = "30s"
        
        results = self.runner.run_test(tasks, "concurrent_test_001")
        
        # 验证并发性能
        summary = results["summary"]
        assert summary["requests_per_second"] > 50
        assert summary["max_response_time"] < 5000  # 最大响应时间小于5秒
    
    @pytest.mark.performance
    def test_stress_testing(self):
        """测试压力测试"""
        tasks = [
            {
                "name": "高负载API调用",
                "method": "GET",
                "url": "/api/heavy-operation",
                "weight": 1
            }
        ]
        
        # 配置压力测试
        self.runner.users = 100
        self.runner.spawn_rate = 10
        self.runner.run_time = "60s"
        
        results = self.runner.run_test(tasks, "stress_test_001")
        
        # 验证系统在高压力下的表现
        summary = results["summary"]
        assert summary["failure_rate"] < 0.1  # 失败率小于10%
        
        # 生成性能报告
        self.runner.generate_report("reports/stress_test_report.json")
    
    @pytest.mark.performance
    def test_endurance_testing(self):
        """测试耐久性测试"""
        tasks = [
            {
                "name": "持续API调用",
                "method": "GET",
                "url": "/api/status",
                "weight": 1
            }
        ]
        
        # 配置长时间运行测试
        self.runner.users = 20
        self.runner.spawn_rate = 2
        self.runner.run_time = "300s"  # 5分钟
        
        results = self.runner.run_test(tasks, "endurance_test_001")
        
        # 验证长时间运行的稳定性
        summary = results["summary"]
        assert summary["failure_rate"] < 0.02  # 失败率小于2%
        
        # 检查响应时间是否稳定
        details = results["details"]
        for detail in details:
            # 响应时间不应该随时间显著增长
            assert detail["avg_response_time"] < detail["max_response_time"] * 0.8