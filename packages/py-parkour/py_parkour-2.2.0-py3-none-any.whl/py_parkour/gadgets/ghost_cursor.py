import asyncio
import random
import math
from playwright.async_api import Page

class GhostCursor:
    """
    Simulates human-like mouse movements using Bezier curves.
    Prevents anti-bot detection by avoiding instant 'teleportation' of the cursor.
    """
    def __init__(self, page: Page):
        self.page = page

    async def move_to(self, selector: str = None, x: int = None, y: int = None, steps: int = 25):
        """
        Moves the mouse to a target element (via selector) or coordinate (x, y)
        using a human-like path (Bezier curve).
        """
        start_x = 0
        start_y = 0
        
        # Get current mouse position (mock tracking if not available, or assume 0,0 for reset)
        # Playwright doesn't easily expose current mouse X/Y unless we track it.
        # For this gadget, we'll assume we start from the last known position or 0,0.
        # Ideally, we'd track self.current_x, self.current_y
        
        target_x = x
        target_y = y

        if selector:
            box = await self.page.locator(selector).first.bounding_box()
            if box:
                # Target center of element with some random offset
                target_x = box['x'] + (box['width'] / 2) + random.randint(-5, 5)
                target_y = box['y'] + (box['height'] / 2) + random.randint(-5, 5)
                
                # Heuristic: Start from a random edge or "off screen" if first move
                # But typically we want continuous movement. 
                # Let's just move from specific points for now.

        if target_x is None or target_y is None:
            return

        # Simple Linear vs Bezier
        # To keep it simple but effective, we use a Cubic Bezier with 2 control points.
        
        # Random control points to create the "curve"
        # Control point 1
        cp1_x = start_x + (random.uniform(0.2, 0.8) * (target_x - start_x)) + random.randint(-100, 100)
        cp1_y = start_y + (random.uniform(0.2, 0.8) * (target_y - start_y)) + random.randint(-100, 100)
        
        # Control point 2
        cp2_x = start_x + (random.uniform(0.2, 0.8) * (target_x - start_x)) + random.randint(-100, 100)
        cp2_y = start_y + (random.uniform(0.2, 0.8) * (target_y - start_y)) + random.randint(-100, 100)

        # Generate path
        path = []
        for i in range(steps + 1):
            t = i / steps
            
            # Cubic Bezier Formula
            # B(t) = (1-t)^3 * P0 + 3(1-t)^2 * t * P1 + 3(1-t) * t^2 * P2 + t^3 * P3
            
            px = ((1-t)**3 * start_x) + (3 * (1-t)**2 * t * cp1_x) + (3 * (1-t) * t**2 * cp2_x) + (t**3 * target_x)
            py = ((1-t)**3 * start_y) + (3 * (1-t)**2 * t * cp1_y) + (3 * (1-t) * t**2 * cp2_y) + (t**3 * target_y)
            
            path.append((px, py))

        # Execute movement
        for point in path:
            await self.page.mouse.move(point[0], point[1])
            # Micro-wait varies to simulate speed changes
            await asyncio.sleep(random.uniform(0.005, 0.02))

    async def click(self, selector: str):
        """
        Moves to element and clicks it naturally.
        """
        await self.move_to(selector)
        # Small hesitation before clicking
        await asyncio.sleep(random.uniform(0.1, 0.3))
        await self.page.click(selector)
