[Playwright 官方网站](https://playwright.dev?utm_source=chatgpt.com)

Playwright 是一个现代浏览器自动化框架，最初由微软团队开发，核心目标是：**用统一 API 控制真实浏览器，实现自动测试、网页操作和自动化任务**。它最常见的用途是 Web 自动化测试，但也经常被用在爬虫、RPA、Agent 浏览器操作和端到端工作流中。

它可以理解成：

> “像人在操作浏览器一样，让程序控制 Chrome、Firefox、Safari 等浏览器完成点击、输入、滚动、登录等动作。”

主要功能可以分成几类：

**1. 端到端（E2E）测试**

这是 Playwright 最核心的能力。

例如测试一个网站：

* 打开网页
* 输入用户名密码
* 点击登录
* 验证页面跳转
* 检查结果是否正确

示例：

```javascript
import { test, expect } from '@playwright/test';

test('login test', async ({ page }) => {
    await page.goto('https://example.com');

    await page.fill('#username', 'admin');
    await page.fill('#password', '123456');

    await page.click('button');

    await expect(page.locator('.welcome'))
        .toContainText('Welcome');
});
```

相比传统 Selenium，Playwright 更关注“用户真实行为”和稳定性。

---

**2. 浏览器自动化**

可以控制浏览器完成各种任务：

* 自动登录
* 自动下载文件
* 自动填写表单
* 自动截图
* 自动点击按钮
* 自动上传文件
* 自动滚动页面

例如：

```javascript
await page.goto("https://google.com");
await page.fill("textarea","Playwright");
await page.press("textarea","Enter");
```

这部分能力经常用于：

* 自动办公（RPA）
* 数据采集
* 自动提交系统
* 批量网页操作

---

**3. 多浏览器支持**

Playwright 可以统一控制：

* Google Chrome
* Chromium
* Mozilla Firefox
* Safari
* Microsoft Edge

一个测试通常无需修改代码：

```javascript
projects:[
   {name:'chromium'},
   {name:'firefox'},
   {name:'webkit'}
]
```

这样能避免：

> Chrome 能运行，但 Safari 崩掉

这种跨浏览器问题。

---

**4. 自动等待（Auto Waiting）**

这是 Playwright 最受欢迎的特性之一。

以前 Selenium 常写：

```python
time.sleep(5)
```

因为：

* 页面加载没完成
* 按钮没出现
* Ajax没返回

Playwright 会自动：

* 等元素出现
* 等元素可点击
* 等动画结束
* 等页面稳定

所以通常直接：

```javascript
await page.click('#submit')
```

不用：

```javascript
await page.waitForTimeout(3000)
```

能显著降低测试不稳定（flaky test）问题。

---

**5. 强大的元素定位（Locator）**

Playwright 提供很多定位方式：

```javascript
page.locator()

page.getByText()

page.getByRole()

page.getByLabel()

page.getByTestId()
```

例如：

```javascript
await page.getByRole(
    'button',
    {name:'Submit'}
).click();
```

相比：

```javascript
'#app > div > div > button'
```

这种脆弱的 CSS 路径，更稳定、更接近用户视角。

---

**6. 网络拦截与 Mock**

Playwright 可以拦截请求：

```javascript
await page.route(
    '/api/user',
    route => route.fulfill({
        json:{
            name:'test'
        }
    })
);
```

用途：

* Mock API
* 模拟后端异常
* 测试离线场景
* 修改请求内容

这对前后端分离开发特别有用。

---

**7. 截图、录屏、追踪（Tracing）**

Playwright 可以自动：

* 页面截图
* 视频录制
* 执行过程记录
* 生成调试报告

例如：

```javascript
await page.screenshot({
    path:'page.png'
});
```

出错后可以查看完整回放：

```bash
npx playwright show-trace trace.zip
```

能看到：

* 点击了什么
* 页面长什么样
* 请求发送了什么
* 哪一步失败

对于排查 CI 问题非常好用。

---

**8. 多标签页和多用户会话**

支持同时控制多个页面：

```javascript
const page1=await context.newPage();
const page2=await context.newPage();
```

支持模拟多个用户：

```javascript
const admin=await browser.newContext();
const user=await browser.newContext();
```

适合：

* 聊天应用测试
* 协同编辑
* 多角色系统

---

**9. Headless / Headed 模式**

无界面运行（CI环境）：

```javascript
browser.launch({
   headless:true
})
```

有界面运行（调试）：

```javascript
browser.launch({
   headless:false
})
```

通常：

* 开发阶段 → 可视化
* CI/CD → Headless

---

**10. Codegen 自动生成代码**

Playwright 能记录你的操作：

```bash
npx playwright codegen
```

然后：

* 打开浏览器
* 你手动点击
* 自动生成脚本

非常适合快速入门。

---

Playwright 的几个核心特点可以总结为：

| 特点         |              优势 |
| ---------- | --------------: |
| 自动等待       |      减少大量 sleep |
| 多浏览器统一 API |      一套代码跑多个浏览器 |
| 定位能力强      |           测试更稳定 |
| 网络 Mock    |           前后端解耦 |
| 调试能力强      |    Trace + 视频回放 |
| 并发执行       |           测试速度快 |
| 原生支持现代网页   | SPA、React、Vue友好 |

如果从近几年趋势看，Playwright 已经逐渐替代很多新项目里的 Selenium，尤其是在：

* React/Vue/Next.js 项目测试
* AI Agent 操作浏览器
* 自动化工作流
* Web RPA
* Browser-use 类 Agent 框架

尤其在 AI Agent 领域，现在很多浏览器 Agent（如 Claude Code 的 browser 工具、browser-use、一些 Computer Use Agent）底层都会使用 Playwright 来操作浏览器。因为它不仅“能点网页”，还提供 DOM、网络、状态等结构化能力，比纯视觉控制更稳定。
