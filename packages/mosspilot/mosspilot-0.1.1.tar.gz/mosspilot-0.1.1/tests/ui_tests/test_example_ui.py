"""
UI测试示例
"""

import pytest
from mosspilot.core.base import TestBase
from mosspilot.modules.ui import UIDriver, UIActions


class TestExampleUI(TestBase):
    """UI测试示例类"""
    
    def setup_method(self, method):
        """测试前置处理"""
        super().setup_method(method)
        self.driver = UIDriver()
        self.actions = UIActions(self.driver.page)
    
    def teardown_method(self, method):
        """测试后置处理"""
        self.driver.close()
        super().teardown_method(method)
    
    @pytest.mark.ui
    def test_login_page(self):
        """测试登录页面"""
        # 导航到登录页面
        self.driver.navigate_to("https://example.com/login")
        
        # 验证页面标题
        title = self.driver.get_title()
        assert "登录" in title
        
        # 验证登录表单元素存在
        self.assert_element_exists(self.driver.page, "#username")
        self.assert_element_exists(self.driver.page, "#password")
        self.assert_element_exists(self.driver.page, "#login-btn")
    
    @pytest.mark.ui
    def test_user_login(self):
        """测试用户登录功能"""
        # 导航到登录页面
        self.driver.navigate_to("https://example.com/login")
        
        # 填写登录信息
        self.actions.fill_input("用户名", "testuser")
        self.actions.fill_input("密码", "password123")
        
        # 点击登录按钮
        self.actions.click_button("登录")
        
        # 等待页面跳转
        self.actions.wait_for_url("*/dashboard")
        
        # 验证登录成功
        self.actions.wait_for_text("欢迎")
    
    @pytest.mark.ui
    def test_form_validation(self):
        """测试表单验证"""
        self.driver.navigate_to("https://example.com/register")
        
        # 不填写必填字段直接提交
        self.actions.click_button("注册")
        
        # 验证错误提示
        self.actions.wait_for_text("请填写用户名")
        self.actions.wait_for_text("请填写邮箱")
    
    @pytest.mark.ui
    def test_navigation_menu(self):
        """测试导航菜单"""
        self.driver.navigate_to("https://example.com")
        
        # 点击菜单项
        self.actions.click_link("产品")
        self.actions.wait_for_url("*/products")
        
        # 验证页面内容
        self.actions.wait_for_text("产品列表")
    
    @pytest.mark.ui
    def test_responsive_design(self):
        """测试响应式设计"""
        self.driver.navigate_to("https://example.com")
        
        # 测试桌面视图
        self.driver.page.set_viewport_size({"width": 1280, "height": 720})
        assert self.actions.is_element_visible(".desktop-menu")
        
        # 测试移动视图
        self.driver.page.set_viewport_size({"width": 375, "height": 667})
        assert self.actions.is_element_visible(".mobile-menu-toggle")
    
    @pytest.mark.ui
    def test_search_functionality(self):
        """测试搜索功能"""
        self.driver.navigate_to("https://example.com")
        
        # 输入搜索关键词
        self.actions.fill_input("搜索", "测试关键词")
        self.driver.press_key("Enter")
        
        # 验证搜索结果
        self.actions.wait_for_text("搜索结果")
        
        # 验证结果数量
        results_count = self.actions.get_element_count(".search-result")
        assert results_count > 0
    
    @pytest.mark.ui
    def test_file_upload(self):
        """测试文件上传"""
        self.driver.navigate_to("https://example.com/upload")
        
        # 上传文件
        self.actions.upload_file("#file-input", "data/fixtures/test_file.txt")
        
        # 点击上传按钮
        self.actions.click_button("上传")
        
        # 验证上传成功
        self.actions.wait_for_text("上传成功")
    
    @pytest.mark.ui
    def test_table_operations(self):
        """测试表格操作"""
        self.driver.navigate_to("https://example.com/users")
        
        # 获取表格数据
        table_data = self.actions.get_table_data("#users-table")
        assert len(table_data) > 0
        
        # 点击编辑按钮
        self.actions.click_button("编辑")
        
        # 修改数据
        self.actions.fill_input("姓名", "新姓名")
        self.actions.click_button("保存")
        
        # 验证修改成功
        self.actions.wait_for_text("保存成功")