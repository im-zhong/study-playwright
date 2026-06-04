`fixture` is one of the most important features in **pytest**. It provides a way to **set up**, **share**, and **clean up** resources that your tests need.

You can think of a fixture as:

> A reusable dependency that pytest automatically creates and injects into test functions.

---

## Why fixtures exist

Suppose every test needs a database connection.

Without fixtures:

```python
def test_user_creation():
    db = Database()
    db.connect()

    # test logic

    db.close()


def test_user_deletion():
    db = Database()
    db.connect()

    # test logic

    db.close()
```

Lots of duplicated setup and cleanup code.

With fixtures:

```python
import pytest

@pytest.fixture
def db():
    connection = Database()
    connection.connect()

    yield connection

    connection.close()
```

Tests become:

```python
def test_user_creation(db):
    # use db

def test_user_deletion(db):
    # use db
```

Pytest automatically:

1. Creates the fixture
2. Passes it into the test
3. Cleans it up afterward

---

# Basic Fixture

```python
import pytest

@pytest.fixture
def sample_data():
    return [1, 2, 3]
```

Use it:

```python
def test_length(sample_data):
    assert len(sample_data) == 3
```

Pytest sees the parameter name:

```python
sample_data
```

and automatically calls the fixture.

---

# Fixture Dependency Injection

Fixtures can depend on other fixtures.

```python
@pytest.fixture
def db():
    return Database()

@pytest.fixture
def user(db):
    return db.create_user("Alice")
```

Test:

```python
def test_user(user):
    assert user.name == "Alice"
```

Dependency graph:

```text
test_user
    ↓
user fixture
    ↓
db fixture
```

Pytest resolves everything automatically.

---

# Setup and Teardown

Using `yield`:

```python
@pytest.fixture
def browser():
    browser = launch_browser()

    yield browser

    browser.close()
```

Execution:

```text
setup
 ↓
launch_browser()
 ↓
yield browser
 ↓
test runs
 ↓
browser.close()
```

This is extremely common in Playwright.

Example:

```python
@pytest.fixture
def page(browser):
    page = browser.new_page()

    yield page

    page.close()
```

---

# Fixture Scope

By default:

```python
@pytest.fixture
def db():
    ...
```

Scope is:

```python
scope="function"
```

Meaning:

```text
test1 → new fixture
test2 → new fixture
test3 → new fixture
```

---

### Module Scope

```python
@pytest.fixture(scope="module")
def db():
    ...
```

Created once per file:

```text
test_file.py

create db
 ↓
test1
test2
test3
 ↓
destroy db
```

---

### Session Scope

```python
@pytest.fixture(scope="session")
def browser():
    ...
```

Created once for the entire test run:

```text
pytest starts
 ↓
create browser
 ↓
all tests
 ↓
close browser
```

Very common for expensive resources.

---

# Fixtures in Playwright

The Playwright Python plugin uses fixtures heavily.

Example:

```python
def test_login(page):
    page.goto("https://example.com")
```

Where did `page` come from?

Pytest fixture.

The Playwright plugin provides:

```python
browser
context
page
```

fixtures automatically.

You don't create them yourself.

---

# Autouse Fixtures

Run automatically without being requested.

```python
@pytest.fixture(autouse=True)
def setup_env():
    print("setup")
```

Now every test gets it:

```python
def test_a():
    pass

def test_b():
    pass
```

Output:

```text
setup
test_a

setup
test_b
```

Useful for:

* environment initialization
* login setup
* temporary directories

---

# Fixtures vs Variables

Many beginners think:

```python
@pytest.fixture
def user():
    return User()
```

is just a fancy variable.

Not quite.

Fixtures provide:

* dependency injection
* lifecycle management
* setup/teardown
* sharing across tests
* scope control

That's why pytest uses them instead of global variables.

---

## Mental Model

Think of fixtures as a lightweight dependency injection system.

```text
Test Function
      ↓
Needs page
      ↓
Pytest creates page fixture
      ↓
Needs browser
      ↓
Pytest creates browser fixture
      ↓
Runs test
      ↓
Performs cleanup
```

This is why pytest code often looks magical:

```python
def test_something(page, user, db):
    ...
```

Those parameters aren't passed manually. Pytest sees the names, builds the required fixtures, injects them, and tears them down when appropriate.


## autouse

`autouse=True` means:

> **Run this fixture automatically for matching tests, even if the test does not explicitly request it.**

Normally, a fixture only runs when you include it as a parameter in a test.

---

## Without `autouse`

```python
import pytest

@pytest.fixture
def setup_env():
    print("Setting up environment")
```

Test:

```python
def test_a(setup_env):
    assert True
```

Output:

```text
Setting up environment
PASSED
```

But:

```python
def test_b():
    assert True
```

Output:

```text
PASSED
```

The fixture is **not executed** because the test didn't ask for it.

---

## With `autouse=True`

```python
import pytest

@pytest.fixture(autouse=True)
def setup_env():
    print("Setting up environment")
```

Now:

```python
def test_a():
    assert True

def test_b():
    assert True
```

Output:

```text
Setting up environment
PASSED

Setting up environment
PASSED
```

The fixture runs automatically for every test in its scope.

---

## Common Use Cases

### Environment setup

```python
@pytest.fixture(autouse=True)
def set_env():
    os.environ["TEST_MODE"] = "true"
```

Every test gets the environment variable.

---

### Database cleanup

```python
@pytest.fixture(autouse=True)
def clean_db():
    db.reset()

    yield

    db.reset()
```

Before and after every test:

```text
reset db
run test
reset db
```

---

### Login or authentication

Sometimes:

```python
@pytest.fixture(autouse=True)
def login(page):
    page.goto("/login")
    page.fill(...)
    page.click(...)
```

Every test starts logged in.

Although many teams prefer to make this explicit rather than autouse.

---

## Scope Still Applies

Autouse doesn't change fixture scope.

### Function scope (default)

```python
@pytest.fixture(autouse=True)
def setup():
    ...
```

Runs:

```text
test1
 ↑ setup

test2
 ↑ setup

test3
 ↑ setup
```

---

### Module scope

```python
@pytest.fixture(
    autouse=True,
    scope="module"
)
def setup():
    ...
```

Runs once per file:

```text
setup

test1
test2
test3

teardown
```

---

### Session scope

```python
@pytest.fixture(
    autouse=True,
    scope="session"
)
def setup():
    ...
```

Runs once for the entire pytest run.

```text
setup

all tests

teardown
```

---

## Autouse Fixtures Can Depend on Other Fixtures

```python
@pytest.fixture
def db():
    print("connect db")
    return Database()

@pytest.fixture(autouse=True)
def clean_database(db):
    db.reset()
```

Execution:

```text
db fixture created
clean_database fixture runs
test runs
```

Pytest resolves dependencies automatically.

---

## Scope of Autouse Visibility

Autouse fixtures are only automatically applied within the directory/module/class where pytest discovers them.

For example:

```text
tests/
├── conftest.py
├── test_a.py
└── api/
    ├── conftest.py
    └── test_b.py
```

An autouse fixture in:

```text
tests/api/conftest.py
```

only affects tests inside:

```text
tests/api/
```

not the entire project.

---

## When to Use Autouse

Good candidates:

* Test environment initialization
* Database cleanup
* Temporary directory setup
* Logging/tracing setup
* Mocking external services globally

Examples:

```python
@pytest.fixture(autouse=True)
def disable_network():
    ...
```

```python
@pytest.fixture(autouse=True)
def clean_cache():
    ...
```

---

## When Not to Use Autouse

Avoid autouse for fixtures that represent important test behavior:

```python
@pytest.fixture(autouse=True)
def login_admin():
    ...
```

Then a test:

```python
def test_user_profile():
    ...
```

gives no clue that an admin login happened.

Many teams prefer:

```python
def test_user_profile(admin_user):
    ...
```

because the dependency is visible in the test signature.

---

## Mental Model

Normal fixture:

```python
def test_x(db):
    ...
```

```text
test explicitly requests db
      ↓
pytest creates db
```

Autouse fixture:

```python
@pytest.fixture(autouse=True)
def db():
    ...
```

```text
pytest sees test
      ↓
automatically creates db
      ↓
runs test
```

So `autouse=True` is essentially:

> "Inject this fixture automatically into every applicable test, whether the test asks for it or not."
