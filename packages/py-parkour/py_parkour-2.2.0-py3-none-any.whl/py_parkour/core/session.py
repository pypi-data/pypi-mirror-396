from typing import Optional
from .driver import ParkourDriver

class ParkourSession:
    """
    Manages the bot session, holding the state and driver.
    """
    def __init__(self, headless: bool = True):
        self.driver = ParkourDriver(headless=headless)
        # Gadgets will be attached here or in the main bot class, 
        # but the session basically holds the active *driver* and identity state.
        self.active_identity = None

    async def start(self):
        await self.driver.start()

    async def close(self):
        await self.driver.stop()
