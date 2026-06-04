Yes. **Pytest is completely optional.** Playwright is fundamentally a browser automation library, just like Selenium. The pytest integration is merely a testing convenience layer.

For automation scripts, agents, crawlers, RPA, etc., you can use Playwright directly.

---

# What is `async_playwright()`?

`async_playwright()` is a context manager that:

1. Starts the Playwright driver process
2. Connects Python to it
3. Exposes browser engines
4. Cleans everything up when done

When you write:

```python
async with async_playwright() as p:
    ...
```

it's roughly equivalent to:

```python
p = await async_playwright().start()

try:
    ...
finally:
    await p.stop()
```

---

# What is `Playwright`?

The type annotation:

```python
from playwright.async_api import Playwright

async def run(playwright: Playwright):
```

is just a Python type hint.

It tells your IDE:

```python
playwright.chromium
playwright.firefox
playwright.webkit
```

exist.

You could remove it entirely:

```python
async def run(playwright):
    ...
```

and the code would still work.

---

# Object hierarchy

Playwright's architecture is:

```text
Playwright
    ↓
BrowserType
    ↓
Browser
    ↓
BrowserContext
    ↓
Page
```

Example:

```python
playwright
    .chromium
    .launch()
        ↓
browser
    .new_context()
        ↓
context
    .new_page()
        ↓
page
```

---

# Equivalent to Selenium

### Selenium

```python
from selenium import webdriver

driver = webdriver.Chrome()

driver.get("https://google.com")
```

Object hierarchy:

```text
ChromeDriver
      ↓
Window
      ↓
Tab
```

---

### Playwright

```python
browser = await playwright.chromium.launch()

context = await browser.new_context()

page = await context.new_page()

await page.goto("https://google.com")
```

Object hierarchy:

```text
Browser
      ↓
Context
      ↓
Page
```

---

# Minimal automation example

No pytest involved:

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=False
        )

        context = await browser.new_context()

        page = await context.new_page()

        await page.goto("https://google.com")

        await page.locator("textarea").fill(
            "Playwright"
        )

        await page.keyboard.press("Enter")

        await page.wait_for_timeout(5000)

        await browser.close()

asyncio.run(main())
```

This is pure automation.

---

# Multiple pages

Equivalent to opening tabs in Selenium:

```python
page1 = await context.new_page()
page2 = await context.new_page()

await page1.goto("https://google.com")
await page2.goto("https://github.com")
```

Hierarchy:

```text
Browser
   ↓
Context
   ├── Page1
   └── Page2
```

Cookies are shared because they're in the same context.

---

# Multiple contexts

Equivalent to different Chrome profiles:

```python
user_context = await browser.new_context()
admin_context = await browser.new_context()
```

Then:

```python
user_page = await user_context.new_page()
admin_page = await admin_context.new_page()
```

Hierarchy:

```text
Browser
   ├── User Context
   │      └── Page
   │
   └── Admin Context
          └── Page
```

Cookies are NOT shared.

This is extremely useful for:

* chat applications
* admin/user workflows
* multi-account automation
* agent simulations

---

# Sync version (feels closer to Selenium)

If you don't like asyncio:

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    context = browser.new_context()

    page = context.new_page()

    page.goto("https://google.com")

    page.fill("textarea", "hello")

    browser.close()
```

Many Selenium users start with the sync API because it feels more familiar.

---

# Typical automation architecture

For AI agents, crawlers, RPA, browser automation, etc.:

```python
async with async_playwright() as p:

    browser = await p.chromium.launch()

    context = await browser.new_context()

    page = await context.new_page()

    # navigate
    await page.goto(...)

    # interact
    await page.click(...)
    await page.fill(...)

    # extract
    text = await page.text_content(...)

    await browser.close()
```

No pytest, fixtures, or tests required.

In fact, most browser agents (including many LLM-based browser agents) use Playwright this way rather than through pytest. Pytest is primarily for test suites; direct Playwright usage is the standard approach for automation applications.


在 Playwright 里，“从一个 page 跳到另一个 page”其实有几种不同含义，你需要先分清你想要的是哪一种场景。

---

# 1. **同一个 page 内跳转（最常见）**

这是网页之间的正常跳转，比如：

* 点击链接
* 提交表单
* `window.location = ...`

Playwright 直接这样写：

```python
await page.click("a#next")
```

或者：

```python
await page.goto("https://example.com/next")
```

### 本质

还是**同一个 page 对象，只是 URL 变了**

```text
page1 (URL A)
   ↓ navigate
page1 (URL B)
```

👉 这是最标准的“页面跳转”

---

# 2. 等待跳转（很重要）

如果是点击触发跳转：

```python
await page.click("a#next")
await page.wait_for_url("**/next")
```

或者更推荐：

```python
async with page.expect_navigation():
    await page.click("a#next")
```

👉 Playwright 会自动处理 race condition

---

# 3. “新开一个 page”（类似新标签页）

如果你的意思是：

> 当前 page 里打开一个新 tab / 新窗口

例如：

```html
<a target="_blank" href="...">
```

Playwright 要这样处理：

```python
async with context.expect_page() as p:
    await page.click("a#open")

new_page = await p.value
await new_page.wait_for_load_state()
```

结果：

```text
context
  ├── page1
  └── page2 (new tab)
```

---

# 4. 在 JS 里 window.open（新 page）

```python
async with context.expect_page() as p:
    await page.evaluate("window.open('https://example.com')")
new_page = await p.value
```

---

# 5. “我想从 page A 切换到 page B（自己创建的）”

你也可以完全手动创建：

```python
page_a = await context.new_page()
page_b = await context.new_page()
```

然后切换操作：

```python
page_a.goto("https://a.com")
page_b.goto("https://b.com")
```

👉 Playwright 没有“active page”概念，你只是操作不同对象

---

# 6. 很多人误解的点（重点）

### ❌ Playwright 没有“页面栈 / forward/back manager”

不像 GUI 自动化工具：

```text
Appium / Selenium thinking:
当前页面 → 切换页面
```

Playwright 是：

```text
你自己管理 page 对象
```

---

# 7. 典型模式总结

## 场景 A：页面跳转（SPA / 普通导航）

```python
await page.click("a")
await page.wait_for_url("**/next")
```

---

## 场景 B：跳转 + 新页面打开

```python
async with context.expect_page() as p:
    await page.click("a[target=_blank]")

new_page = await p.value
```

---

## 场景 C：直接访问新 page

```python
new_page = await context.new_page()
await new_page.goto("https://example.com")
```

---

# 8. 一句话理解

Playwright 的核心思想是：

> **page 不会“切换”，你只是“创建 + 操作多个 page 对象”**

---

如果你愿意，我可以帮你画一张 **browser / context / page / navigation / tab 的完整结构图**，或者讲一下 Playwright 在底层是怎么跟 Chrome DevTools Protocol 通信的，这样你会更彻底理解它为什么不像 Selenium。


## playwright context manager

Good question—this touches the boundary between **Playwright’s API design** and **what actually happens at OS/process level**.

---

# 1. Do `browser` / `page` support Python context managers?

## Yes—but only partially and in specific APIs

Playwright provides a context manager at the **Playwright driver level**, not for every object.

### Correct usage:

```python
from playwright.async_api import async_playwright

async with async_playwright() as p:
    browser = await p.chromium.launch()
    context = await browser.new_context()
    page = await context.new_page()
```

Here:

* `async_playwright()` → **YES, context manager**
* `browser` → ❌ not a context manager
* `context` → ❌ not a context manager
* `page` → ❌ not a context manager

So cleanup is NOT automatically handled per object.

---

# 2. How are resources actually cleaned up?

You are expected to explicitly close:

```python
await page.close()
await context.close()
await browser.close()
```

However…

👉 In practice, Playwright is more robust than it looks.

---

# 3. What happens if Python crashes?

If your Python process crashes (or is killed):

### Case A: normal crash (exception, exit)

* Playwright driver process exits
* Browser process is terminated (or orphaned and then cleaned up by OS)
* OS eventually cleans up sockets / processes

### Case B: hard kill (SIGKILL / power off)

* No cleanup runs
* Chromium processes may remain temporarily
* OS process reaper eventually cleans them

So:

> ❗ There is no “guaranteed graceful cleanup” in crash scenarios.

But also:

> ✅ You do NOT leak system resources permanently in normal conditions

---

# 4. Why Playwright doesn’t rely on Python context managers per page

Because Playwright architecture is:

```text
Python → Playwright Driver (Node process) → Browser (Chromium)
```

Even if Python dies:

* The **Playwright driver process is still the owner of cleanup logic**
* It detects disconnection and shuts down browser processes

So the real lifecycle is NOT Python-managed.

---

# 5. What *is* safely auto-managed?

When using:

```python
async with async_playwright() as p:
```

Playwright guarantees:

* Driver process is started
* Communication channel is opened
* On exit → driver is stopped
* Browsers launched by this session are cleaned up

So this is the **only guaranteed RAII-style cleanup boundary**

---

# 6. What about contexts/pages?

They are:

* lightweight objects
* remote handles to browser-side resources

They are cleaned up:

### Normal case:

```python
await context.close()
```

### Or implicitly when browser closes:

```python
await browser.close()
```

which destroys everything under it.

---

# 7. Important mental model (very important)

Think of Playwright like this:

```text
Python code (client)
   ↓ websocket / pipe
Playwright driver (Node process)
   ↓ CDP / browser protocol
Chromium browser process
```

So:

* Python objects are just **proxies**
* Real cleanup happens in the **driver + browser layer**

---

# 8. Best practice (recommended pattern)

If you want safe automation:

```python
async with async_playwright() as p:
    browser = await p.chromium.launch()

    context = await browser.new_context()
    page = await context.new_page()

    try:
        await page.goto("https://example.com")
    finally:
        await browser.close()
```

---

# 9. If you want “Selenium-like automatic cleanup”

You can wrap it yourself:

```python
class BrowserSession:
    def __init__(self, browser):
        self.browser = browser

    async def __aenter__(self):
        return self.browser

    async def __aexit__(self, exc_type, exc, tb):
        await self.browser.close()
```

But normally unnecessary.

---

# 10. Key takeaway

* ❌ `page`, `context`, `browser` are NOT Python context managers
* ✅ Only `async_playwright()` is
* ✅ Cleanup is handled at driver/browser process level
* ⚠️ On hard crash, cleanup is best-effort (OS + driver responsibility)
* ✅ In normal usage, resource leakage is not a problem

---

If you want, I can also explain:

* why Playwright uses a separate Node driver process (this design is key to stability)
* or how context isolation is implemented at Chromium protocol level (CDP sessions)
