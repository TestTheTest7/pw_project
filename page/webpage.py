import sys

from page.webelement import WebElement
from playwright.sync_api import TimeoutError as TimeoutException
from playwright.sync_api import Page
import pytest


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
