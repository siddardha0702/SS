import os
import sys
import asyncio
import threading
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Browser, Page, Playwright
from backend.workspace.manager import workspace_manager


class _ProactorLoopManager:
    """
    Dedicated worker thread running an asyncio.ProactorEventLoop.
    Guarantees subprocess-transport support for Playwright on Windows regardless
    of how the parent FastAPI server/loop was initialized.
    """
    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def get_loop(self) -> asyncio.AbstractEventLoop:
        with self._lock:
            if self._loop is None or not self._loop.is_running():
                if sys.platform == "win32":
                    self._loop = asyncio.ProactorEventLoop()
                else:
                    self._loop = asyncio.new_event_loop()
                self._thread = threading.Thread(target=self._run, daemon=True, name="NexusPlaywrightProactorThread")
                self._thread.start()
            return self._loop

    def _run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def run_coro(self, coro):
        loop = self.get_loop()
        future = asyncio.run_coroutine_threadsafe(coro, loop)
        return await asyncio.wrap_future(future)


_runner = _ProactorLoopManager()


class BrowserService:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.screenshots_dir = workspace_manager.get_task_dir(task_id) / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    async def _impl_start_browser(self, headless: bool = True, viewport: Optional[dict] = None) -> Dict[str, Any]:
        if not self.playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            vp = viewport or {"width": 1280, "height": 800}
            self.page = await self.browser.new_page(viewport=vp)
        return {"status": "browser_started", "viewport": viewport}

    async def _impl_set_viewport_size(self, width: int, height: int):
        if self.page:
            await self.page.set_viewport_size({"width": width, "height": height})

    async def _impl_open_page(self, url: str) -> Dict[str, Any]:
        if not self.page:
            await self._impl_start_browser()
        response = await self.page.goto(url, wait_until="domcontentloaded", timeout=15000)
        status = response.status if response else 200
        title = await self.page.title()
        return {"status": "navigated", "url": url, "http_status": status, "title": title}

    async def _impl_click(self, selector: str) -> Dict[str, Any]:
        await self.page.wait_for_selector(selector, timeout=5000)
        await self.page.click(selector)
        return {"status": "clicked", "selector": selector}

    async def _impl_fill(self, selector: str, text: str) -> Dict[str, Any]:
        await self.page.wait_for_selector(selector, timeout=5000)
        await self.page.fill(selector, text)
        return {"status": "filled", "selector": selector, "text": text}

    async def _impl_get_text(self, selector: str) -> str:
        await self.page.wait_for_selector(selector, timeout=5000)
        return await self.page.inner_text(selector)

    async def _impl_assert_visible(self, selector: str, timeout: int = 5000) -> bool:
        try:
            await self.page.wait_for_selector(selector, state="visible", timeout=timeout)
            return True
        except Exception:
            return False

    async def _impl_assert_text(self, selector: str, expected: str, timeout: int = 5000) -> bool:
        try:
            await self.page.wait_for_selector(selector, timeout=timeout)
            text = await self.page.inner_text(selector)
            return expected.lower() in text.lower()
        except Exception:
            return False

    async def _impl_take_screenshot(self, filename: str) -> str:
        if not filename.endswith(".png"):
            filename = f"{filename}.png"
        filepath = self.screenshots_dir / filename
        await self.page.screenshot(path=str(filepath), full_page=True)
        return str(filepath)

    async def _impl_close_browser(self):
        if self.page:
            try:
                await self.page.close()
            except Exception:
                pass
            self.page = None
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
            self.playwright = None

    # Public asynchronous facade dispatched to Proactor runner
    async def start_browser(self, headless: bool = True, viewport: Optional[dict] = None) -> Dict[str, Any]:
        """Launches Chromium browser session."""
        return await _runner.run_coro(self._impl_start_browser(headless=headless, viewport=viewport))

    async def set_viewport_size(self, width: int, height: int):
        return await _runner.run_coro(self._impl_set_viewport_size(width=width, height=height))

    async def open_page(self, url: str) -> Dict[str, Any]:
        """Navigates to specified URL."""
        return await _runner.run_coro(self._impl_open_page(url=url))

    async def click(self, selector: str) -> Dict[str, Any]:
        """Clicks on element matching selector."""
        return await _runner.run_coro(self._impl_click(selector=selector))

    async def fill(self, selector: str, text: str) -> Dict[str, Any]:
        """Types text into input matching selector."""
        return await _runner.run_coro(self._impl_fill(selector=selector, text=text))

    async def get_text(self, selector: str) -> str:
        """Retrieves inner text of selector."""
        return await _runner.run_coro(self._impl_get_text(selector=selector))

    async def assert_visible(self, selector: str, timeout: int = 5000) -> bool:
        """Verifies selector is visible on page."""
        return await _runner.run_coro(self._impl_assert_visible(selector=selector, timeout=timeout))

    async def assert_text(self, selector: str, expected: str, timeout: int = 5000) -> bool:
        """Verifies selector contains expected text."""
        return await _runner.run_coro(self._impl_assert_text(selector=selector, expected=expected, timeout=timeout))

    async def take_screenshot(self, filename: str) -> str:
        """Captures full-page screenshot and saves to task screenshots dir."""
        return await _runner.run_coro(self._impl_take_screenshot(filename=filename))

    async def close_browser(self):
        """Closes browser and stops Playwright."""
        return await _runner.run_coro(self._impl_close_browser())

