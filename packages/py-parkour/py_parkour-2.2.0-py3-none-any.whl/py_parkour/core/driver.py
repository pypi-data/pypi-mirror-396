import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class ParkourDriver:
    """
    Wrapper around Playwright to manage the browser lifecycle.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def start(self):
        """Starts the Playwright engine and browser."""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()

    async def stop(self):
        """Stops the browser and Playwright engine."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def goto(self, url: str):
        """Navigates to the specified URL."""
        if not self.page:
            raise RuntimeError("Driver not started. Call await driver.start() first.")
        await self.page.goto(url)

    async def get_content(self) -> str:
        """Returns the current page content."""
        if not self.page:
             raise RuntimeError("Driver not started.")
        return await self.page.content()
