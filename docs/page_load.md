These are different **milestones in the browser page loading lifecycle**. Understanding them is important because Playwright's `goto()`, `waitForURL()`, and navigation-related APIs can stop waiting at different points.

Let's use a typical page load as an example:

```text
User clicks link
    ↓
Browser sends HTTP request
    ↓
Server returns HTML
    ↓
Browser starts parsing HTML
    ↓
DOMContentLoaded
    ↓
Browser downloads CSS / JS / Images
    ↓
load
    ↓
Ajax / Fetch requests continue
    ↓
networkidle (maybe)
```

---

# 1. commit

The earliest stage.

```javascript
await page.goto(url, {
  waitUntil: 'commit'
});
```

Meaning:

> "The server has responded, and the browser has started loading the new document."

Timeline:

```text
Request sent
    ↓
Response headers received
    ↓
✓ commit
    ↓
HTML parsing starts
```

At this point:

* HTML not fully parsed
* DOM may not exist yet
* JS not executed
* Images not loaded

Think:

> "The navigation succeeded and the new page has begun."

Useful when:

* You only care that navigation happened
* You want the fastest possible return

---

# 2. domcontentloaded

Corresponds to the browser event:

```javascript
window.addEventListener('DOMContentLoaded', ...)
```

Timeline:

```text
HTML downloaded
    ↓
Browser parses HTML
    ↓
DOM tree built
    ↓
✓ DOMContentLoaded
```

At this point:

✅ DOM exists

```javascript
document.querySelector(...)
```

works.

But:

❌ Images may still be loading

❌ Stylesheets may still be loading

❌ Some async scripts may still be running

Example:

```html
<body>
  <button>Submit</button>
  <img src="huge-image.jpg">
</body>
```

The button exists when DOMContentLoaded fires, even if the image is still downloading.

---

# 3. load

Corresponds to:

```javascript
window.addEventListener('load', ...)
```

Timeline:

```text
HTML parsed
    ↓
CSS loaded
    ↓
Images loaded
    ↓
iframes loaded
    ↓
✓ load
```

At this point:

✅ DOM ready

✅ Images ready

✅ CSS ready

✅ Most static resources ready

Historically this was considered:

> "The page is fully loaded."

This is Playwright's default:

```javascript
await page.goto(url);
```

is equivalent to:

```javascript
await page.goto(url, {
  waitUntil: 'load'
});
```

---

# 4. networkidle

Timeline:

```text
load
    ↓
Ajax requests
    ↓
WebSocket traffic
    ↓
Background API calls
    ↓
No network requests for 500ms
    ↓
✓ networkidle
```

Playwright definition:

> No active network connections for at least 500ms.

Example:

```text
load
 ↓
GET /user
 ↓
GET /notifications
 ↓
GET /settings
 ↓
(all finished)
 ↓
500ms silence
 ↓
networkidle
```

---

## Why Playwright discourages it

Modern websites often never become truly idle.

Examples:

### Analytics

```javascript
setInterval(() => {
  sendAnalytics();
}, 1000);
```

Every second:

```text
Request
Request
Request
Request
```

Network never becomes idle.

---

### Live updates

```javascript
pollServerEvery2Seconds();
```

or

```javascript
WebSocket connection
```

Again:

```text
Request
Request
Request
```

No network idle.

---

### React / Vue / Next.js apps

A page may become visually usable long before network activity stops.

```text
User can click button
      ↓
Background requests continue
```

Waiting for networkidle only slows tests.

---

Therefore Playwright recommends:

```javascript
await page.goto(url);

await expect(page.locator('h1'))
  .toHaveText('Dashboard');
```

instead of:

```javascript
await page.goto(url, {
  waitUntil: 'networkidle'
});
```

The assertion directly checks what you actually care about.

---

# Real-world timeline

```text
Navigation starts
    │
    ├─ commit
    │
    ├─ HTML parsing
    │
    ├─ DOMContentLoaded
    │
    ├─ CSS/images download
    │
    ├─ load
    │
    ├─ API requests
    │
    └─ networkidle
```

Speed comparison:

```text
commit              fastest
↓
domcontentloaded
↓
load                default
↓
networkidle         slowest
```

# What Playwright users typically choose

### Most common

```javascript
await page.goto(url);
```

Uses:

```javascript
waitUntil: 'load'
```

---

### SPA applications (React/Vue)

Often:

```javascript
await page.goto(url);

await expect(page.getByRole('heading'))
  .toBeVisible();
```

Rely on assertions rather than `networkidle`.

---

### Scraping / performance-sensitive

Sometimes:

```javascript
await page.goto(url, {
  waitUntil: 'domcontentloaded'
});
```

because you only need the DOM and don't care about images.

---

### Rarely used

```javascript
waitUntil: 'networkidle'
```

Playwright's own documentation now explicitly discourages it for testing because it often makes tests slower and less reliable than waiting for the actual UI state you expect.
