"""
Moss UI测试浏览器驱动
"""

from typing import Optional, Dict, Any, List
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from mosspilot.core.config import settings
from mosspilot.core.monitoring import Logger
from mosspilot.core.base.decorators import retry, log_execution


class UIDriver:
    """UI测试驱动器，基于playwright封装"""
    
    def __init__(self, browser_type: Optional[str] = None, headless: Optional[bool] = None):
        self.browser_type = browser_type or settings.ui.browser
        self.headless = headless if headless is not None else settings.ui.headless
        self.logger = Logger()
        
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        self._initialize_browser()
    
    def _initialize_browser(self) -> None:
        """初始化浏览器"""
        self.playwright = sync_playwright().start()
        
        if self.browser_type == "chromium":
            self.browser = self.playwright.chromium.launch(headless=self.headless)
        elif self.browser_type == "firefox":
            self.browser = self.playwright.firefox.launch(headless=self.headless)
        elif self.browser_type == "webkit":
            self.browser = self.playwright.webkit.launch(headless=self.headless)
        else:
            raise ValueError(f"不支持的浏览器类型: {self.browser_type}")
        
        self.context = self.browser.new_context(
            viewport=settings.ui.viewport
        )
        self.page = self.context.new_page()
        
        # 设置默认超时
        self.page.set_default_timeout(settings.ui.timeout)
        
        self.logger.info(f"浏览器初始化完成: {self.browser_type}")
    
    @log_execution
    def navigate_to(self, url: str) -> None:
        """导航到指定URL"""
        self.logger.info(f"导航到: {url}")
        self.page.goto(url)
    
    @log_execution
    @retry(max_attempts=3)
    def click(self, selector: str, timeout: Optional[int] = None) -> None:
        """点击元素"""
        self.logger.info(f"点击元素: {selector}")
        self.page.click(selector, timeout=timeout)
    
    @log_execution
    @retry(max_attempts=3)
    def fill(self, selector: str, value: str, timeout: Optional[int] = None) -> None:
        """填充输入框"""
        self.logger.info(f"填充输入框: {selector} = {value}")
        self.page.fill(selector, value, timeout=timeout)
    
    @log_execution
    def type_text(self, selector: str, text: str, delay: int = 0) -> None:
        """逐字符输入文本"""
        self.logger.info(f"输入文本: {selector} = {text}")
        self.page.type(selector, text, delay=delay)
    
    @log_execution
    def press_key(self, key: str) -> None:
        """按键"""
        self.logger.info(f"按键: {key}")
        self.page.keyboard.press(key)
    
    @log_execution
    def wait_for_element(self, selector: str, timeout: Optional[int] = None) -> None:
        """等待元素出现"""
        self.logger.info(f"等待元素: {selector}")
        self.page.wait_for_selector(selector, timeout=timeout)
    
    @log_execution
    def wait_for_url(self, url_pattern: str, timeout: Optional[int] = None) -> None:
        """等待URL匹配"""
        self.logger.info(f"等待URL: {url_pattern}")
        self.page.wait_for_url(url_pattern, timeout=timeout)
    
    def get_text(self, selector: str) -> str:
        """获取元素文本"""
        element = self.page.query_selector(selector)
        if element:
            return element.text_content() or ""
        return ""
    
    def get_attribute(self, selector: str, attribute: str) -> Optional[str]:
        """获取元素属性"""
        element = self.page.query_selector(selector)
        if element:
            return element.get_attribute(attribute)
        return None
    
    def is_visible(self, selector: str) -> bool:
        """检查元素是否可见"""
        return self.page.is_visible(selector)
    
    def is_enabled(self, selector: str) -> bool:
        """检查元素是否启用"""
        return self.page.is_enabled(selector)
    
    def screenshot(self, path: str, full_page: bool = False) -> None:
        """截图"""
        self.logger.info(f"截图保存到: {path}")
        self.page.screenshot(path=path, full_page=full_page)
    
    def scroll_to(self, selector: str) -> None:
        """滚动到元素"""
        self.logger.info(f"滚动到元素: {selector}")
        self.page.locator(selector).scroll_into_view_if_needed()
    
    def hover(self, selector: str) -> None:
        """悬停在元素上"""
        self.logger.info(f"悬停元素: {selector}")
        self.page.hover(selector)
    
    def select_option(self, selector: str, value: str) -> None:
        """选择下拉选项"""
        self.logger.info(f"选择选项: {selector} = {value}")
        self.page.select_option(selector, value)
    
    def get_current_url(self) -> str:
        """获取当前URL"""
        return self.page.url
    
    def get_title(self) -> str:
        """获取页面标题"""
        return self.page.title()
    
    def execute_script(self, script: str) -> Any:
        """执行JavaScript"""
        self.logger.info(f"执行脚本: {script[:50]}...")
        return self.page.evaluate(script)
    
    def new_page(self) -> Page:
        """创建新页面"""
        new_page = self.context.new_page()
        new_page.set_default_timeout(settings.ui.timeout)
        return new_page
    
    def close_page(self, page: Optional[Page] = None) -> None:
        """关闭页面"""
        target_page = page or self.page
        if target_page:
            target_page.close()
    
    def close(self) -> None:
        """关闭浏览器"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        
        self.logger.info("浏览器已关闭")
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()