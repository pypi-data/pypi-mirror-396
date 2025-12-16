"""
Moss UI测试操作封装
"""

from typing import Optional, List, Dict, Any
from playwright.sync_api import Page, Locator
from mosspilot.core.monitoring import Logger
from mosspilot.core.base.decorators import retry, log_execution


class UIActions:
    """UI测试操作封装类"""
    
    def __init__(self, page: Page):
        self.page = page
        self.logger = Logger()
    
    @log_execution
    @retry(max_attempts=3)
    def click_button(self, text: str, timeout: Optional[int] = None) -> None:
        """点击按钮（通过文本）"""
        self.logger.info(f"点击按钮: {text}")
        self.page.get_by_role("button", name=text).click(timeout=timeout)
    
    @log_execution
    @retry(max_attempts=3)
    def click_link(self, text: str, timeout: Optional[int] = None) -> None:
        """点击链接（通过文本）"""
        self.logger.info(f"点击链接: {text}")
        self.page.get_by_role("link", name=text).click(timeout=timeout)
    
    @log_execution
    @retry(max_attempts=3)
    def fill_input(self, label: str, value: str, timeout: Optional[int] = None) -> None:
        """填充输入框（通过标签）"""
        self.logger.info(f"填充输入框: {label} = {value}")
        self.page.get_by_label(label).fill(value, timeout=timeout)
    
    @log_execution
    @retry(max_attempts=3)
    def select_dropdown(self, label: str, value: str, timeout: Optional[int] = None) -> None:
        """选择下拉框选项"""
        self.logger.info(f"选择下拉框: {label} = {value}")
        self.page.get_by_label(label).select_option(value, timeout=timeout)
    
    @log_execution
    @retry(max_attempts=3)
    def check_checkbox(self, label: str, timeout: Optional[int] = None) -> None:
        """勾选复选框"""
        self.logger.info(f"勾选复选框: {label}")
        self.page.get_by_label(label).check(timeout=timeout)
    
    @log_execution
    @retry(max_attempts=3)
    def uncheck_checkbox(self, label: str, timeout: Optional[int] = None) -> None:
        """取消勾选复选框"""
        self.logger.info(f"取消勾选复选框: {label}")
        self.page.get_by_label(label).uncheck(timeout=timeout)
    
    @log_execution
    def wait_for_text(self, text: str, timeout: Optional[int] = None) -> None:
        """等待文本出现"""
        self.logger.info(f"等待文本: {text}")
        self.page.get_by_text(text).wait_for(timeout=timeout)
    
    @log_execution
    def wait_for_element_visible(self, selector: str, timeout: Optional[int] = None) -> None:
        """等待元素可见"""
        self.logger.info(f"等待元素可见: {selector}")
        self.page.locator(selector).wait_for(state="visible", timeout=timeout)
    
    @log_execution
    def wait_for_element_hidden(self, selector: str, timeout: Optional[int] = None) -> None:
        """等待元素隐藏"""
        self.logger.info(f"等待元素隐藏: {selector}")
        self.page.locator(selector).wait_for(state="hidden", timeout=timeout)
    
    def get_element_text(self, selector: str) -> str:
        """获取元素文本"""
        element = self.page.locator(selector)
        return element.text_content() or ""
    
    def get_element_count(self, selector: str) -> int:
        """获取元素数量"""
        return self.page.locator(selector).count()
    
    def is_element_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        return self.page.locator(selector).is_visible()
    
    def is_element_enabled(self, selector: str) -> bool:
        """检查元素是否启用"""
        return self.page.locator(selector).is_enabled()
    
    def is_checkbox_checked(self, selector: str) -> bool:
        """检查复选框是否被勾选"""
        return self.page.locator(selector).is_checked()
    
    @log_execution
    def scroll_to_element(self, selector: str) -> None:
        """滚动到元素"""
        self.logger.info(f"滚动到元素: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed()
    
    @log_execution
    def hover_element(self, selector: str) -> None:
        """悬停在元素上"""
        self.logger.info(f"悬停元素: {selector}")
        self.page.locator(selector).hover()
    
    @log_execution
    def double_click(self, selector: str) -> None:
        """双击元素"""
        self.logger.info(f"双击元素: {selector}")
        self.page.locator(selector).dblclick()
    
    @log_execution
    def right_click(self, selector: str) -> None:
        """右键点击元素"""
        self.logger.info(f"右键点击元素: {selector}")
        self.page.locator(selector).click(button="right")
    
    @log_execution
    def drag_and_drop(self, source_selector: str, target_selector: str) -> None:
        """拖拽元素"""
        self.logger.info(f"拖拽元素: {source_selector} -> {target_selector}")
        self.page.locator(source_selector).drag_to(self.page.locator(target_selector))
    
    def take_screenshot(self, path: str, full_page: bool = False) -> None:
        """截图"""
        self.logger.info(f"截图保存到: {path}")
        self.page.screenshot(path=path, full_page=full_page)
    
    def take_element_screenshot(self, selector: str, path: str) -> None:
        """元素截图"""
        self.logger.info(f"元素截图: {selector} -> {path}")
        self.page.locator(selector).screenshot(path=path)
    
    def get_all_text_contents(self, selector: str) -> List[str]:
        """获取所有匹配元素的文本内容"""
        elements = self.page.locator(selector)
        return elements.all_text_contents()
    
    def get_table_data(self, table_selector: str) -> List[Dict[str, str]]:
        """获取表格数据"""
        table = self.page.locator(table_selector)
        headers = table.locator("thead th").all_text_contents()
        rows = table.locator("tbody tr")
        
        data = []
        for i in range(rows.count()):
            row = rows.nth(i)
            cells = row.locator("td").all_text_contents()
            row_data = dict(zip(headers, cells))
            data.append(row_data)
        
        return data
    
    @log_execution
    def upload_file(self, file_input_selector: str, file_path: str) -> None:
        """上传文件"""
        self.logger.info(f"上传文件: {file_path} -> {file_input_selector}")
        self.page.locator(file_input_selector).set_input_files(file_path)
    
    def execute_javascript(self, script: str, *args) -> Any:
        """执行JavaScript代码"""
        self.logger.info(f"执行JavaScript: {script[:50]}...")
        return self.page.evaluate(script, *args)
    
    def wait_for_network_idle(self, timeout: Optional[int] = None) -> None:
        """等待网络空闲"""
        self.logger.info("等待网络空闲")
        self.page.wait_for_load_state("networkidle", timeout=timeout)
    
    def wait_for_dom_content_loaded(self, timeout: Optional[int] = None) -> None:
        """等待DOM内容加载完成"""
        self.logger.info("等待DOM内容加载完成")
        self.page.wait_for_load_state("domcontentloaded", timeout=timeout)