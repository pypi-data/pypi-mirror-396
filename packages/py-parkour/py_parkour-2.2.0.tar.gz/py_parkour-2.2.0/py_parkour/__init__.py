from .core.driver import ParkourDriver
from .gadgets.crusher import Crusher
from .gadgets.compass import Compass
from .gadgets.disguises import Disguises
from .gadgets.shadow import Shadow
from .gadgets.radar import Radar
from .gadgets.ghost_cursor import GhostCursor
from .gadgets.spatial import SpatialCompass
from .gadgets.chaos_typer import ChaosTyper
from .gadgets.solicitor import Solicitor, TwoCaptchaSolver
from typing import AsyncGenerator, Any

class ParkourBot:
    """
    The main unified API for Py-Parkour.
    Combines the Pilot (Driver) and the Gadgets.
    """
    def __init__(self, headless: bool = True):
        self.driver = ParkourDriver(headless=headless)
        self.identity = Disguises() # Identity gadget is always available
        # These are initialized after browser start
        self.crusher = None
        self.compass = None
        self.shadow = None
        self.radar = None
        self.ghost = None
        self.spatial = None
        self.typer = None
        self.solicitor = None

    async def start(self):
        """Starts the browser session."""
        await self.driver.start()
        # Helpers that depend on the page
        self.crusher = Crusher(self.driver.page)
        self.compass = Compass(self.driver.page)
        self.shadow = Shadow(self.driver.page)
        self.radar = Radar(self.driver.page)
        self.ghost = GhostCursor(self.driver.page)
        self.spatial = SpatialCompass(self.driver.page)
        self.typer = ChaosTyper(self.driver.page)
        self.solicitor = Solicitor(self.driver.page)
        
        self.radar.start() # active by default? Let's keep it manual or auto? Let's start it.

    async def close(self):
        """Closes the browser session."""
        await self.driver.stop()

    async def goto(self, url: str):
        """Navigates to a URL."""
        await self.driver.goto(url)

    @property
    def current_url(self) -> str:
        if self.driver.page:
            return self.driver.page.url
        return ""

    async def crush_cookies(self):
        """clear_path alias: Clears cookie banners."""
        if not self.crusher:
            raise RuntimeError("Bot not started. Call await bot.start()")
        await self.crusher.clear_path()

    async def crawl(self, max_pages: int = 5) -> AsyncGenerator[int, None]:
        """Iterates through pages using the Compass."""
        if not self.compass:
             raise RuntimeError("Bot not started. Call await bot.start()")
        async for page_num in self.compass.crawl(max_pages=max_pages):
            yield page_num

    async def auto_setup_identity(self, url: str):
        """
        The 'Magic' Auto-Setup:
        1. Checks if we need an account (Naively assume yes for this demo)
        2. Generates identity
        3. Fills email (assumes standard 'email' input name/id for now)
        4. Waits for code and fills it.
        """
        if not self.driver.page:
             await self.start()
        
        await self.goto(url)
        
        print("Auto-Setup: generating identity...")
        id_data = await self.identity.generate_identity()
        print(f"Auto-Setup: Using {id_data.email}")

        # Magic Action: Fill email
        # Heuristic: look for input[type=email] or name=email
        try:
            email_input = self.driver.page.locator("input[type='email'], input[name*='email']").first
            if await email_input.count() > 0:
                await email_input.fill(id_data.email)
                print("Auto-Setup: Filled email.")
                
                # Assume there is a submit button next
                # heuristic: button near it? Or simple enter?
                await email_input.press("Enter")
                print("Auto-Setup: Submitted email form.")
                
                # Wait for code
                code = await self.identity.wait_for_code()
                if code:
                    # Magic Action: Fill code
                    # Heuristic: input for code (often shorter, or named 'code', 'otp')
                    code_input = self.driver.page.locator("input[name*='code'], input[name*='otp'], input[id*='code']").first
                    if await code_input.count() > 0:
                        await code_input.fill(code)
                        await code_input.press("Enter")
                        print("Auto-Setup: Submitted verification code (Mock).")
                    else:
                        print("Auto-Setup: Could not find code input field.")
            else:
                 print("Auto-Setup: Could not find email input field.")

        except Exception as e:
            print(f"Auto-Setup failed or interrupted: {e}")
