import sys

from playwright.sync_api import Locator
import pytest


class WebElement(Locator):
    def __init__(self, impl_obj, page):
        super(WebElement, self).__init__(impl_obj)
        self._page = page

    def get_element(
            self, locator, state="visible", wait=10, error_message=None
    ):
        try:
            # Wait for element with an appropriate state
            self.page.wait_for_selector(
                selector=locator, timeout=wait * 1000, state=state
            )

            element = self.locator(locator).first

            return WebElement(element._impl_obj, self.page)

        except:
            if not error_message:
                error_message = f'WebElement.get_element()\n  error: {sys.exc_info()[0]}\n  locator: "{locator}"'

            pytest.fail(error_message, False)

    def get_elements(self, locator, state="visible", wait=10):
        try:
            # Wait for element with an appropriate state
            self.page.wait_for_selector(
                selector=locator, timeout=wait * 1000, state=state
            )

            list_of_elements = self.locator(locator)

            return [
                WebElement(list_of_elements.nth(i)._impl_obj, self.page)
                for i in range(list_of_elements.count())
            ]

        except:
            return []

    def click(self, raise_warning=False, retry=2):
        try:
            self._sync(self._impl_obj.click())

        except Exception as e:
            error_message = (
                f"WebElement.click()"
                f"\n  error: {sys.exc_info()[0]}"
                f"\n  exception: {e}"
                f'\n  locator: "{self}"'
            )

            pytest.fail(error_message, False)

    def text(self):
        return self.all_inner_texts()[0]

    def is_checked(self):
        return self._sync(self._impl_obj.is_checked())

    def get_attribute(self, name):
        return self._sync(self._impl_obj.get_attribute(name=name))

    def send_keys(self, value):

        try:
            value = str(value)

            self.fill(value)

        except:
            pytest.fail(f"WebElement.send_keys_quiet():\n  error: {sys.exc_info()[0]}")

