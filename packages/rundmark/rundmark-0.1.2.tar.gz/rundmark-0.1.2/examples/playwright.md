# Playwright Example

```python{file=browser.py,display=no}
import re
from playwright.sync_api import Playwright, expect

class PWBrowser():
    def __init__(self, playwright):
        print("- Opening headless browser", flush=True)
        self.browser = playwright.chromium.launch(headless=True)
        self.page = self.browser.new_page()
```


```python{run="capture image",wrap="uv",image="images/yahoo.png"}
from playwright.sync_api import sync_playwright
from browser import PWBrowser
import time
with sync_playwright() as p:
    b = PWBrowser(p)
    b.page.goto("https://news.yahoo.co.jp/")
    print("- page opened", flush=True)
    b.page.set_viewport_size({"width": 1280, "height": 800})
    b.page.screenshot(path="images/yahoo.png")
```

次のブロックで同じページをから操作を再開します。

```python{run="capture image",wrap="uv",image="images/yahoo2.png"}
from playwright.sync_api import sync_playwright
from browser import PWBrowser
with sync_playwright() as p:
    b = PWBrowser(p)
    b.page.set_viewport_size({"width": 1280, "height": 800})
    b.page.goto("https://news.yahoo.co.jp/")
    print("- page opened", flush=True)
    b.page.click("text=速報")
    b.page.screenshot(path="images/yahoo2.png")
```
