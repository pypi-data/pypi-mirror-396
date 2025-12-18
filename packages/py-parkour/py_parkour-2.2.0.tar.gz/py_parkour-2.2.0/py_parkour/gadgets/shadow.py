from playwright.async_api import Page
import aiohttp
import asyncio

class Shadow:
    """
    The Shadow Gadget: Session Transfer.
    "Breaks in with the Browser, Steals the Soul for the API."
    """
    def __init__(self, page: Page):
        self.page = page

    async def create_session(self) -> aiohttp.ClientSession:
        """
        Creates an aiohttp ClientSession with all cookies and headers 
        transferred from the current browser state.
        """
        if not self.page:
            raise RuntimeError("Shadow needs a running browser page.")

        # 1. Harvest Cookies
        cookies = await self.page.context.cookies()
        cookie_jar = {}
        for cookie in cookies:
            cookie_jar[cookie['name']] = cookie['value']

        # 2. Harvest User-Agent
        user_agent = await self.page.evaluate("navigator.userAgent")

        # 3. Create Session with transplanted soul
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        
        session = aiohttp.ClientSession(
            headers=headers,
            cookies=cookie_jar
        )
        return session
