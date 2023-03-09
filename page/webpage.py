import sys

from page.webelement import WebElement
from playwright.sync_api import TimeoutError as TimeoutException
from playwright.sync_api import Page
from playwright.sync_api import ViewportSize
import pytest
from browser import Browser, Browsers


class WebPage(Page):
    def __init__(self, impl_obj):
        super(WebPage, self).__init__(impl_obj)
        self.browser_config = "chrome"

    def navigate(self, url):
        self.goto(url)

    def page_pause(self):
        self.pause()

    def get_element(
            self, locator, state="visible", wait=10, use_highlight=True, error_message=None
    ):
        try:
            # Wait for element with an appropriate state
            self.wait_for_selector(
                selector=locator, timeout=wait * 1000, state=state
            )

            # Get element
            element = self.locator(locator).first

            if use_highlight:
                self.highlight(element)

            return WebElement(element._impl_obj, self)

        except:
            if not error_message:
                error_message = f'WebPage.get_element():\n  error: {sys.exc_info()[0]}\n  locator: "{locator}"'

            pytest.fail(error_message, False)

    def highlight(self, element, locator=""):
        """
        Used for debugging purposes in local environment.
        """
        try:
            if element is None and locator:
                element = self.locator(locator).first

            if element:
                style = "background: yellow; border: 0.2px solid red;"
                self.evaluate(f"(element, style) => element.setAttribute('style', style);", style)

        except:
            pass

    def get_elements(self, locator, state="visible", wait=10):
        try:
            # Wait for element with an appropriate state
            self.wait_for_selector(
                selector=locator, timeout=wait * 1000, state=state
            )
            # Get elements
            list_of_elements = self.locator(locator)

            return [
                WebElement(list_of_elements.nth(i)._impl_obj, self)
                for i in range(list_of_elements.count())
            ]

        except:
            return []

    def get_element_with_scroll(
            self,
            locator="",
            element=None,
            state="attached",
            wait=10,
    ):
        try:
            element = element if element else self.get_element(locator, state=state, wait=wait)

            # Get element and scroll if needed
            element.scroll_into_view_if_needed()

            return element

        except:
            pytest.fail(f"WebPage.get_element_with_scroll():\n  error: {sys.exc_info()[0]}", False)

    def wait_loading(self, locator, time_to_appear=0, time_to_disappear=10):
        try:
            if time_to_appear:
                self.wait_for_selector(
                    selector=locator, timeout=time_to_appear * 1000, state="attached"
                )
        except:
            pass

        self.highlight(locator)

        self.wait_for_selector(
            selector=locator, timeout=time_to_disappear * 1000, state="hidden"
        )

    def if_exists(self, locator, time_to_wait=0):
        try:
            if time_to_wait:
                self.wait_for_selector(
                    selector=locator, timeout=time_to_wait * 1000, state="attached"
                )

            else:
                return bool(self.locator(locator).count())

        except TimeoutException:
            return False

        except:
            pytest.fail(f"WebPage.check_if_exists():\n  error: {sys.exc_info()[0]}")

        return True

    # def evaluate(self, expression, arg):


def get_page(pw_context):
    browser_config = Browser("chrome")
    browser_name = browser_config.capabilities["browserName"]

    viewport_width = browser_config.screen_width
    viewport_height = browser_config.screen_height

    if browser_name == Browsers.CHROME:
        browser = pw_context.chromium.launch(headless=False)
    elif browser_name == Browsers.FIREFOX:
        browser = pw_context.firefox.launch()
    elif browser_name == Browsers.SAFARI:
        browser = pw_context.webkit.launch()
    else:
        browser = None

    # Get browser context
    # Should add user agent explicitly cause without defining page cannot be fully loaded in Chrome headless
    browser_context = browser.new_context(
        viewport=ViewportSize(width=viewport_width, height=viewport_height),
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
    )

    page = browser_context.new_page()

    web_page = WebPage(page._impl_obj)

    return browser_context, browser, web_page