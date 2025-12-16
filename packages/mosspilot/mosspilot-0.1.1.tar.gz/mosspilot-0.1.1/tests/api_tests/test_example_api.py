"""
API测试示例
"""

import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.api import APIClient, APIAssertions


class TestExampleAPI(TestBase):
    """API测试示例类"""
    
    def setup_method(self, method):
        """测试前置处理"""
        super().setup_method(method)
        self.client = APIClient()
        self.assertions = APIAssertions()
    
    def teardown_method(self, method):
        """测试后置处理"""
        self.client.close()
        super().teardown_method(method)
    
    @pytest.mark.api
    def test_get_users(self):
        """测试获取用户列表"""
        response = self.client.get("/api/users")
        
        # 断言状态码
        self.assertions.assert_status_code(response, 200)
        
        # 断言响应时间
        self.assertions.assert_response_time(response, 2.0)
        
        # 断言JSON结构
        self.assertions.assert_json_contains(response, {"users": []})
    
    @pytest.mark.api
    def test_create_user(self):
        """测试创建用户"""
        user_data = {
            "name": "测试用户",
            "email": "test@example.com",
            "age": 25
        }
        
        response = self.client.post("/api/users", json=user_data)
        
        # 断言创建成功
        self.assertions.assert_status_code(response, 201)
        
        # 断言返回数据包含ID
        self.assertions.assert_json_contains(response, {"id": 1})
    
    @pytest.mark.api
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        user_id = 1
        response = self.client.get(f"/api/users/{user_id}")
        
        self.assertions.assert_status_code(response, 200)
        self.assertions.assert_json_path_value(response, "id", user_id)
        self.assertions.assert_json_path_value(response, "name", "测试用户")
    
    @pytest.mark.api
    def test_update_user(self):
        """测试更新用户信息"""
        user_id = 1
        update_data = {"name": "更新后的用户名"}
        
        response = self.client.put(f"/api/users/{user_id}", json=update_data)
        
        self.assertions.assert_status_code(response, 200)
        self.assertions.assert_json_path_value(response, "name", "更新后的用户名")
    
    @pytest.mark.api
    def test_delete_user(self):
        """测试删除用户"""
        user_id = 1
        response = self.client.delete(f"/api/users/{user_id}")
        
        self.assertions.assert_status_code(response, 204)
    
    @pytest.mark.api
    def test_user_not_found(self):
        """测试用户不存在的情况"""
        response = self.client.get("/api/users/999")
        
        self.assertions.assert_status_code(response, 404)
        self.assertions.assert_json_contains(response, {"error": "User not found"})