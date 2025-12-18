from playwright.async_api import Page, Locator
import asyncio

class SpatialCompass:
    """
    Finds elements based on their visual/geometric position relative to other elements.
    Useful when CSS classes are obfuscated or dynamic.
    """
    def __init__(self, page: Page):
        self.page = page

    async def find_right_of(self, anchor_selector: str, target_tag: str = "input") -> Locator:
        """
        Finds the first 'target_tag' element that is visually to the RIGHT of the element 
        matching 'anchor_selector'.
        """
        anchor_box = await self.page.locator(anchor_selector).first.bounding_box()
        if not anchor_box:
            return None

        # Define the "Right" zone
        # We look for elements where:
        # x > anchor.x
        # y is roughly within the anchor's vertical range (allow some fuzziness)
        
        anchor_mid_y = anchor_box['y'] + (anchor_box['height'] / 2)
        
        # Get all potential targets
        candidates = await self.page.locator(target_tag).all()
        
        best_candidate = None
        min_distance = float('inf')

        for candidate in candidates:
            # We strictly need visible elements
            if not await candidate.is_visible():
                continue
                
            box = await candidate.bounding_box()
            if not box:
                continue

            # Check logic: Is it to the right?
            # Candidate Left Edge should be >= Anchor Right Edge (roughly)
            is_to_right = box['x'] >= (anchor_box['x'] + anchor_box['width'] - 10) # -10 buffer
            
            if is_to_right:
                # Check vertical alignment (is it on the same "line"?)
                cand_mid_y = box['y'] + (box['height'] / 2)
                y_diff = abs(cand_mid_y - anchor_mid_y)
                
                # If it's effectively on the same line (within 20px variation)
                if y_diff < 150: # Generous buffer for responsiveness
                    dist = box['x'] - (anchor_box['x'] + anchor_box['width'])
                    if dist < min_distance:
                        min_distance = dist
                        best_candidate = candidate

        return best_candidate

    async def find_below(self, anchor_selector: str, target_tag: str = "input") -> Locator:
        """
        Finds the first 'target_tag' element that is visually BELOW the anchor.
        """
        anchor_box = await self.page.locator(anchor_selector).first.bounding_box()
        if not anchor_box:
            return None
            
        anchor_mid_x = anchor_box['x'] + (anchor_box['width'] / 2)
        candidates = await self.page.locator(target_tag).all()
        
        best_candidate = None
        min_distance = float('inf')

        for candidate in candidates:
            if not await candidate.is_visible():
                continue
                
            box = await candidate.bounding_box()
            if not box:
                continue

            # Is it below?
            is_below = box['y'] >= (anchor_box['y'] + anchor_box['height'] - 5)
            
            if is_below:
                # Horizontal alignment check
                cand_mid_x = box['x'] + (box['width'] / 2)
                x_diff = abs(cand_mid_x - anchor_mid_x)
                
                # If aligned somewhat centrally
                if x_diff < 200: 
                    dist = box['y'] - (anchor_box['y'] + anchor_box['height'])
                    if dist < min_distance and dist > 0:
                        min_distance = dist
                        best_candidate = candidate
        
        return best_candidate
