from playwright.async_api import Page
import asyncio

class Compass:
    """
    Auto-detects pagination pattern.
    """
    def __init__(self, page: Page):
        self.page = page

    async def crawl(self, max_pages: int = 5):
        """
        Generator that yields control for each page found.
        """
        for i in range(max_pages):
            yield i # Yield control back to user to scrape the current page
            
            # Try to find next page
            if not await self._next_page():
                break
            
            # Wait for meaningful content load (simple wait for now, can be improved)
            await self.page.wait_for_load_state("networkidle")

    async def _next_page(self) -> bool:
        """
        Strategy to find and go to Next page.
        """
        # Strategy 1: "Next" button
        next_keywords = ["next", "older", ">", ">>", "more"]
        for keyword in next_keywords:
             try:
                # Look for buttons/links with "Next" text, often localized or icon based.
                # Strictly mapping "Next" can be tricky, "Next >" is common.
                # Using a somewhat loose locator.
                locator = self.page.locator(f"text=/{keyword}/i").first
                if await locator.count() > 0 and await locator.is_visible():
                     print(f"Compass: Found Next button '{keyword}'")
                     # Snapshot check (simplified: just store URL)
                     prev_url = self.page.url
                     await locator.click(timeout=3000)
                     await asyncio.sleep(1) # Wait for navigation
                     if self.page.url != prev_url:
                         return True
                     # If URL didn't change, maybe content did? (SPA) - simplified check
                     return True
             except Exception:
                 pass
        
        # Strategy 2: Scroll (Infinite Scroll)
        # Implementation: Scroll to bottom, see if height increases
        try:
            prev_height = await self.page.evaluate("document.body.scrollHeight")
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(2) # Wait for load
            new_height = await self.page.evaluate("document.body.scrollHeight")
            if new_height > prev_height:
                print("Compass: Infinite scroll detected")
                return True
        except Exception:
            pass

        return False
