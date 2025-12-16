import platform

from playwright.async_api import Page


class ChromeConfig:
    headless = False
    args = ['--no-sandbox']
    timeout = 10000


class FirefoxConfig:
    headless = False
    args = ['--no-sandbox']
    timeout = 10000


class EdgeConfig:
    headless = False
    args = ['--no-sandbox']
    timeout = 10000


class MobileConfig:
    headless = False
    args = ['--no-sandbox']
    timeout = 10000


def init_browser_headless():
    if platform.system() == 'Windows':
        headless = ChromeConfig.headless
    else:
        headless = True
    return headless


class BasePage:

    def __new__(cls, playwright, name: str = None):

        if (name is None) or (name in ["chrome", "google chrome", "gc"]):
            return cls.chrome(playwright)
        if name in ["firefox", "ff"]:
            return cls.firefox(playwright)
        if name == "webkit":
            return cls.webkit(playwright)
        if name == "iphone":
            return cls.iphone(playwright)
        if name == "android":
            return cls.android(playwright)

    @staticmethod
    def chrome(playwright):
        browser = playwright.chromium.launch(headless=init_browser_headless(), args=ChromeConfig.args)
        context = browser.new_context(no_viewport=True)
        context.set_default_timeout(ChromeConfig.timeout)
        page = context.new_page()
        return page

    @staticmethod
    def firefox(playwright):
        browser = playwright.firefox.launch(headless=init_browser_headless(), args=ChromeConfig.args)
        context = browser.new_context(no_viewport=True)
        context.set_default_timeout(FirefoxConfig.timeout)
        page = context.new_page()
        return page

    @staticmethod
    def webkit(playwright):
        browser = playwright.webkit.launch(headless=init_browser_headless(), args=ChromeConfig.args)
        context = browser.new_context(no_viewport=True)
        context.set_default_timeout(EdgeConfig.timeout)
        page = context.new_page()
        return page

    @staticmethod
    def iphone(playwright):
        browser = playwright.chromium.launch(headless=init_browser_headless(), args=MobileConfig.args)
        iphone_12 = playwright.devices['iPhone 12 Pro']
        context_app = browser.new_context(
            **iphone_12,
        )
        context_app.set_default_timeout(MobileConfig.timeout)
        page_app = context_app.new_page()
        return page_app

    @staticmethod
    def ipad(playwright):
        browser = playwright.chromium.launch(headless=init_browser_headless(), args=MobileConfig.args)
        ipad = playwright.devices['iPad Air']
        context_app = browser.new_context(
            **ipad,
        )
        context_app.set_default_timeout(MobileConfig.timeout)
        page_app = context_app.new_page()
        return page_app

    @staticmethod
    def android(playwright):
        browser = playwright.chromium.launch(headless=init_browser_headless(), args=MobileConfig.args)
        Samsung = playwright.devices['Samsung Galaxy S20 Ultra']
        context_app = browser.new_context(
            **Samsung,
        )
        context_app.set_default_timeout(MobileConfig.timeout)
        page_app = context_app.new_page()
        return page_app


class CustomerPage:

    def select(self, page: Page, text_list: list, length=None):
        length = len(text_list) if length is None else length
        for index, value in enumerate(text_list):
            print('当前选中的值为：', value)
            page.get_by_role("listitem").filter(has_text=value).scroll_into_view_if_needed()
            page.get_by_role("listitem").filter(has_text=value).click()
            # 元素存在时，才执行下一步
            if index + 1 < len(text_list):  # 判断是否是最后一个元素
                print('下一个选中的值为：', text_list[index + 1])
                if page.get_by_role("listitem").filter(has_text=text_list[index + 1]).count() == 0:
                    page.get_by_role("listitem").filter(has_text=value).click()
        if len(text_list) < length:  # 下拉列表的长度大于传入的列表长度时，双击最后一个元素
            page.get_by_role("listitem").filter(has_text=text_list[-1]).dblclick()

    def file_upload(self, page, locator, file_path: str):
        with page.expect_file_chooser(timeout=20000) as fc_info:
            page.get_by_text(locator).click()
        file_chooser = fc_info.value
        file_chooser.set_files(file_path)
        # self.page.wait_for_selector('text=上传成功', timeout=20000)
        # self.page.wait_for_selector('text=上传成功', state='hidden', timeout=20000)
        # self.page.wait_for_load_state('load')
        # self.page.wait_for_load_state("domcontentloaded")
