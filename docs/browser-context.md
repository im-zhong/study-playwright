In Playwright, a **Browser Context** is an isolated browser session inside a browser instance.

A good mental model is:

```text
Browser
 ├── Context A
 │     ├── Page 1
 │     └── Page 2
 │
 ├── Context B
 │     └── Page 3
 │
 └── Context C
       └── Page 4
```

---

## Why does it exist?

Imagine you open Chrome and create two separate profiles:

```text
Chrome Profile A
Chrome Profile B
```

Each profile has its own:

* Cookies
* Local Storage
* Session Storage
* Authentication state
* Cache

Browser Context is essentially a lightweight version of a browser profile.

---

## Browser vs Browser Context vs Page

### Browser

The actual browser process.

```python
browser = playwright.chromium.launch()
```

Think:

```text
Chrome.exe
```

---

### Browser Context

An isolated session.

```python
context = browser.new_context()
```

Think:

```text
Chrome Profile
```

---

### Page

A tab.

```python
page = context.new_page()
```

Think:

```text
Browser Tab
```

Hierarchy:

```text
Browser
    ↓
Context
    ↓
Page
```

---

## Example

```python
browser = playwright.chromium.launch()

context1 = browser.new_context()
context2 = browser.new_context()

page1 = context1.new_page()
page2 = context2.new_page()
```

Now:

```python
page1.goto("https://example.com")
page2.goto("https://example.com")
```

If you log in on `page1`:

```python
page1.fill(...)
page1.click(...)
```

The login cookie is stored only in:

```text
context1
```

`page2` remains logged out.

---

## Why Playwright uses contexts heavily

Launching a browser is expensive.

```python
browser = chromium.launch()
```

may take hundreds of milliseconds or more.

Creating a context is much cheaper:

```python
context = browser.new_context()
```

So Playwright recommends:

```text
1 Browser
Many Contexts
```

instead of:

```text
Many Browsers
```

---

## Common Test Structure

A very common pytest + Playwright setup is:

```python
@pytest.fixture(scope="session")
def browser():
    ...
```

```text
Create Browser Once
```

Then for each test:

```python
@pytest.fixture
def context(browser):
    ...
```

```text
Create New Context
```

Then:

```python
@pytest.fixture
def page(context):
    ...
```

```text
Create New Page
```

Execution:

```text
Browser
    ↓
Test 1 Context
       ↓
       Page

    ↓
Test 2 Context
       ↓
       Page

    ↓
Test 3 Context
       ↓
       Page
```

This gives:

* Fast execution (browser reused)
* Test isolation (fresh context per test)

---

## Context Storage

Everything below is isolated per context:

```text
Cookies
Local Storage
Session Storage
IndexedDB
Permissions
Cache
Authentication State
```

For example:

```python
page.evaluate(
    "localStorage.setItem('token', 'abc')"
)
```

Only pages in the same context can see it.

---

## Multiple Users Example

Very useful for testing chat apps.

```python
browser = playwright.chromium.launch()

alice = browser.new_context()
bob = browser.new_context()

alice_page = alice.new_page()
bob_page = bob.new_page()
```

Now:

```text
Alice logged in
Bob logged in
```

in the same browser process but completely isolated.

---

## Incognito Analogy

The closest Chrome analogy is:

```text
Browser Context ≈ Incognito Window
```

Each new context behaves like a fresh incognito session:

```python
context = browser.new_context()
```

No cookies, no previous login, no storage.

When the context is closed:

```python
context.close()
```

everything disappears.

---

## In Playwright Test

If you're using Playwright Test (Node.js):

```javascript
test('example', async ({ page }) => {
  ...
});
```

Under the hood, Playwright roughly does:

```text
Browser
   ↓
New Context
   ↓
New Page
   ↓
Run Test
   ↓
Destroy Context
```

for every test.

That's one of the major reasons Playwright tests are isolated and less flaky: each test gets a fresh browser context instead of sharing cookies and state with previous tests.
