# Writing tests
# https://playwright.dev/python/docs/intro
# https://playwright.dev/python/docs/writing-tests

# 这里讲了一些pytest for Playwright常用方法
# async fixture: https://playwright.dev/python/docs/test-runners#async-fixtures
# pytest for playwright: https://playwright.dev/python/docs/test-runners


# Guide： https://playwright.dev/python/docs/input
# 这里面就是具体怎么去使用playwright各种各样的功能了，用到那个看哪个就行了

## Playwright tests are simple, they
# - perform actions, and
# - assert the state against expectations.

# - auto-waiting: There is no need to wait for anything prior to performing an action
# - There is also no need to deal with the race conditions when performing the checks


import re
from playwright.sync_api import Page, expect

def test_has_title(page: Page):
    # Navigation
    # Most of the tests will start with navigating page to the URL. 
    # After that, test will be able to interact with the page elements.
    # Playwright will wait for page to reach the [load state] prior to moving forward
    # [load state] https://developer.mozilla.org/en-US/docs/Web/API/Window/load_event
    page.goto("https://playwright.dev/")

    # Expect a title "to contain" a substring. 
    # https://playwright.dev/python/docs/writing-tests#assertions
    # Performing actions starts with locating the elements, use [locators API] for that
    # Playwright will wait for the element to be [actionable] prior to performing the action, 
    # so there is no need to wait for it to become available.
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")

    # Click the get started link.
    # Basic actions: https://playwright.dev/python/docs/writing-tests#basic-actions
    page.get_by_role("link", name="Get started").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()



# Test isolation
# https://playwright.dev/python/docs/writing-tests#test-isolation

# page fixture: 有点类似dependency injection, 每个test都是isolated，而且包含setup和teardown
# browser context: https://playwright.dev/python/docs/browser-contexts 
#                  https://playwright.dev/python/docs/api/class-browsercontext
from playwright.sync_api import Page

# [Pages are isolated] between tests due to the Browser Context, 
# which is equivalent to a brand new browser profile, where every test gets a fresh environment, 
# even when multiple tests run in a single Browser.

def test_example_test(page: Page):
  pass
  # "page" belongs to an isolated BrowserContext, created for this specific test.

def test_another_test(page: Page):
  pass
  # "page" in this second test is completely isolated from the first test.


  import pytest
from playwright.sync_api import Page, expect

@pytest.fixture(scope="function", autouse=True)
def before_each_after_each(page: Page):
    
    print("before the test runs")

    # Go to the starting url before each test.
    page.goto("https://playwright.dev/")
    yield
    
    print("after the test runs")

def test_main_navigation(page: Page):
    # Assertions use the expect API.
    expect(page).to_have_url("https://playwright.dev/")


