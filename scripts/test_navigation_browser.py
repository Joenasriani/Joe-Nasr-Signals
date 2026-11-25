import os
import re
import unittest
from urllib.parse import urlsplit
from playwright.sync_api import sync_playwright

BASE = os.environ.get("SIGNALS_TEST_URL", "http://127.0.0.1:8765").rstrip("/")
ROUTES = ["training-workshops-lectures", "certifications", "tools-technologies", "music", "publications", "interactive-projects", "video-campaigns"]

class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def assert_target(self, page, fragment):
        self.assertTrue(fragment.startswith("#"))
        target = page.locator(fragment)
        self.assertEqual(target.count(), 1)
        self.assertTrue(target.is_visible())
        page.wait_for_function("""hash => {
            const el = document.getElementById(hash.slice(1));
            const header = document.querySelector('.site-header');
            if (!el || !header) return false;
            const marker = el.querySelector('.section-label') || el.querySelector('h2') || el;
            const rect = marker.getBoundingClientRect();
            return rect.top >= header.getBoundingClientRect().bottom - 2 && rect.top < innerHeight;
        }""", arg=fragment, timeout=8000)

    def test_navigation_and_returns(self):
        for width in (1440, 375):
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={"width": width, "height": 900}, reduced_motion="reduce")
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                # Keep canonical same-origin navigation local in CI.
                page.route("https://joe-nasr-signals.vercel.app/**", lambda route: route.fulfill(status=302, headers={"Location": BASE + urlsplit(route.request.url).path + ("?" + urlsplit(route.request.url).query if urlsplit(route.request.url).query else "")}))
                try:
                    page.goto(BASE + "/", wait_until="load")
                    nav = page.locator(".header-nav")
                    self.assertTrue(nav.evaluate("(e) => e.scrollWidth <= e.clientWidth + 1"))
                    self.assertEqual(page.locator("#methodTitle").inner_text(), "Collections & Resources")
                    sizes = page.locator("#practiceTitle, #archiveTitle, #faqTitle, #client-bank-title, #methodTitle").evaluate_all("(els) => els.map(e => getComputedStyle(e).fontSize)")
                    self.assertEqual(len(sizes), 5)
                    self.assertEqual(len(set(sizes)), 1, "Section heading sizes differ")
                    self.assertEqual(page.locator(".method-copy a").count(), 7)
                    count = int(re.search(r"\d+", page.locator("#heroCount").inner_text()).group())
                    self.assertEqual(page.locator("#heroIndex").inner_text(), f"JN / 001-{count:03d}")
                    for link in nav.locator("a").all():
                        if not link.is_visible():
                            continue
                        fragment = link.get_attribute("href")
                        link.click()
                        self.assert_target(page, fragment)
                    for route in ROUTES:
                        page.goto(f"{BASE}/{route}/", wait_until="load")
                        link = page.get_by_role("link", name=re.compile("Back to Signals", re.I)).first
                        href = link.get_attribute("href")
                        self.assertEqual(href, "/")
                        self.assertTrue(page.locator(".site-header").get_by_role("link", name=re.compile("Back to Signals", re.I)).is_visible())
                        link.click()
                        page.wait_for_url(BASE + "/")
                        page.wait_for_function("window.scrollY <= 2 && !location.hash")
                        self.assertEqual(urlsplit(page.url).fragment, "")
                    self.assertEqual(errors, [])
                finally:
                    page.close()

if __name__ == "__main__":
    unittest.main()
