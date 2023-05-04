import os
import pytest
from page.webpage import WebPage
from playwright.sync_api import ViewportSize
from browser import Browser, Browsers
from playwright.sync_api import (
    Browser as PW_Browser,
    BrowserContext,
    Playwright,
    sync_playwright,
)

# pylint: disable=redefined-outer-name


@pytest.fixture(scope="session")
def playwright():
    selenium_remote_url = "http://127.0.0.1:4444/wd/hub"
    os.environ["SELENIUM_REMOTE_URL"] = selenium_remote_url
    pw = sync_playwright().start()
    yield pw
    pw.stop()


@pytest.fixture(scope="session")
def browser(playwright: Playwright):
    browser_config = Browser("chrome")
    browser_name = browser_config.capabilities["browserName"]

    if browser_name == Browsers.CHROME:
        browser = playwright.chromium.launch(headless=False, args=["--remote-allow-origins=*"])
    elif browser_name == Browsers.FIREFOX:
        browser = playwright.firefox.launch()
    elif browser_name == Browsers.SAFARI:
        browser = playwright.webkit.launch()
    else:
        browser = None

    yield browser

    browser.close()


@pytest.fixture(scope="function")
def browser_context(browser: PW_Browser):
    browser_config = Browser("chrome")
    viewport_width = browser_config.screen_width
    viewport_height = browser_config.screen_height

    # Get browser context
    # Should add user agent explicitly cause without defining page cannot be fully loaded in Chrome headless
    browser_context = browser.new_context(
        viewport=ViewportSize(width=viewport_width, height=viewport_height),
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        )

    yield browser_context

    browser_context.close()


@pytest.fixture(scope="function")
def page(browser_context: BrowserContext):
    page = browser_context.new_page()

    playwright_page = WebPage(page._impl_obj)
    playwright_page.navigate("https://www.kiwi.com/en/")

    yield playwright_page


@pytest.fixture(autouse=True)
def test_wrapper(page: WebPage):

    # CALL TEST SCENARIO
    yield




