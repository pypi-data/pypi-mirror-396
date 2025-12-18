import asyncio
import random
from playwright.async_api import Locator

class ChaosTyper:
    """
    Simulates human typing with random latency and occasional mistakes/corrections.
    """
    
    # Simple QWERTY adjacency map for simulating realistic fat-finger errors
    # Format: Key -> List of adjacent keys
    ADJACENCY = {
        'q': 'wa', 'w': 'qase', 'e': 'wsrd', 'r': 'edft', 't': 'rfgy', 'y': 'tghu', 'u': 'yhji', 'i': 'ujko', 'o': 'iklp', 'p': 'ol',
        'a': 'qwsz', 's': 'qweadzx', 'd': 'ersfcx', 'f': 'rtdgcv', 'g': 'tyfhvb', 'h': 'ybgjn', 'j': 'uikmhn', 'k': 'iolmj', 'l': 'opk',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
    }

    def __init__(self, page):
        self.page = page

    async def type_human(self, selector: str, text: str, mistake_chance: float = 0.05):
        """
        Types text into the element found by selector with human-like characteristics.
        mistake_chance: 0.0 to 1.0 probability of making a mistake per character.
        """
        locator = self.page.locator(selector)
        await locator.focus() # Ensure focus
        
        for char in text:
            # 1. Random Latency
            # Normal typing speed varies, average around 80-150ms per key
            delay = random.normalvariate(0.12, 0.05)
            if delay < 0.02: delay = 0.02
            await asyncio.sleep(delay)

            # 2. Chance of Mistake
            lower_char = char.lower()
            if random.random() < mistake_chance and lower_char in self.ADJACENCY:
                # Make a mistake!
                wrong_char = random.choice(self.ADJACENCY[lower_char])
                # Preserve case roughly
                if char.isupper(): wrong_char = wrong_char.upper()
                
                await self.page.keyboard.type(wrong_char)
                
                # Realization delay ("Oh shoot, I made a typo")
                await asyncio.sleep(random.uniform(0.1, 0.4))
                
                # Backspace
                await self.page.keyboard.press("Backspace")
                await asyncio.sleep(random.uniform(0.05, 0.2))
                
                # Retry with correct char (fall through to correct type below)
            
            # Type the correct character
            await self.page.keyboard.type(char)
