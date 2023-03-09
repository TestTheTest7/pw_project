import pytest
from page.webpage import WebPage, get_page
from playwright.sync_api import sync_playwright
# pylint: disable=redefined-outer-name


@pytest.fixture(scope="function")
def page():

    with sync_playwright() as pw_context:

        browser_context, browser, playwright_page = get_page(pw_context)
        playwright_page.navigate("https://www.kiwi.com/en/")

        yield playwright_page

        browser_context.close()
        browser.close()


@pytest.fixture(autouse=True)
def test_wrapper(page: WebPage):

    # CALL TEST SCENARIO
    yield




