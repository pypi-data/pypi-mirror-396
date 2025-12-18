from playwright.async_api import Page, Locator
import asyncio

class Crusher:
    """
    detects and 'Accept' or 'Reject' cookie banners.
    """
    def __init__(self, page: Page):
        self.page = page

    async def clear_path(self):
        """
        Hunts down and clicks the closing button of any modal.
        """
        # Heuristics:
        # 1. Look for common keywords in buttons.
        # 2. Check for high z-index elements (overlay).
        
        keywords = ["accept", "agree", "allow", "consent", "i understand", "got it"]
        
        # Strategy 1: Find buttons with keywords
        for keyword in keywords:
            # Case insensitive search for button or link text
            try:
                # We target buttons, links, or divs that look like buttons
                locator = self.page.locator(f"text=/{keyword}/i").first
                if await locator.count() > 0 and await locator.is_visible():
                    print(f"Crusher: Found keyword '{keyword}', attempting click...")
                    await locator.click(timeout=2000)
                    # Small wait to see if it clears
                    await asyncio.sleep(0.5)
                    return
            except Exception as e:
                # Ignore errors finding/clicking individual elements
                pass

        # Strategy 2 (Generalized): Look for high Z-index elements (simplified for now)
        # This is harder to implement robustly without JS execution to check computed styles.
        # For this version, we stick to the keyword heuristic which covers 90% of basic cases.
        # A more advanced version would inject JS to find the highest z-index visible div.
        print("Crusher: No obvious cookie banner found.")
