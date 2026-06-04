# study playwright

playwright远远大于selenium！

## installation

1. https://playwright.dev/docs/intro#installing-playwright
2. 脚手架：The command below either initializes a new project or adds Playwright to an existing one.
3. 手动安装：
   1. 安装依赖：sudo npx playwright install-deps
   2. 安装playwright：npx playwright install
   3. 测试：npx playwright test [--headed]
4. https://playwright.dev/docs/test-reporters#html-reporter
   1. 一个测试跑完之后，还会生成一份测试报告！
5. 还有实时观察模式，UI Mode，跑测试的时候更方便了 https://playwright.dev/docs/test-ui-mode
6. 相当不错呀，看起来编程比selenium方便，功能也多
7. https://playwright.dev/python/docs/intro 原来有python版
8. 竟然还可以生成测试：https://playwright.dev/python/docs/codegen-intro
9. running and debugging: https://playwright.dev/python/docs/running-tests
10. 卧槽！trace！如果线上任务失败了，就可以把trace调出来，看看到底是哪里错了！我靠！！！https://playwright.dev/python/docs/trace-viewer-intro
11. CI: https://playwright.dev/python/docs/ci-intro
    1.  https://playwright.dev/python/docs/ci
12. docker: https://playwright.dev/python/docs/docker
13. Playwright's API is not thread-safe.


## API call

1. 做E2E的时候用pytest或者nodejstest确实合适，但是我们要操控浏览器，还是API call更合适，接下来学习这一部分