from playwright.async_api import Page, Request, Response
from typing import List, Dict, Any
import asyncio
import json

class Radar:
    """
    The Radar Gadget: Hidden API Detector.
    Passively listens to background network traffic to find JSON endpoints.
    """
    def __init__(self, page: Page):
        self.page = page
        self._captured_requests: List[Dict[str, Any]] = []
        self._latest_json: Dict[str, Any] = {}
        self._is_active = False

    def start(self):
        """Starts listening to network traffic."""
        if not self._is_active:
            self.page.on("response", self._handle_response)
            self._is_active = True

    def stop(self):
        """Stops listening."""
        if self._is_active:
            self.page.remove_listener("response", self._handle_response)
            self._is_active = False

    async def _handle_response(self, response: Response):
        """Internal handler for intercepted responses."""
        try:
            # We filter for JSON content types
            content_type = response.headers.get("content-type", "").lower()
            
            if "application/json" in content_type:
                try:
                    data = await response.json()
                    self._latest_json = data
                    
                    # Log the request details for replay
                    req_info = {
                        "url": response.url,
                        "method": response.request.method,
                        "headers": response.request.headers,
                        "post_data": response.request.post_data,
                        "payload_preview": str(data)[:100] + "..." 
                    }
                    self._captured_requests.append(req_info)
                except:
                    pass # Ignore if json parsing fails or body empty
        except Exception:
            pass # Safety net for async issues

    @property
    def latest_json(self) -> Dict[str, Any]:
        """Returns the most recently captured JSON payload."""
        return self._latest_json

    @property
    def requests(self) -> List[Dict[str, Any]]:
        """Returns a list of all captured API requests."""
        return self._captured_requests

    def clear(self):
        """Clears the capture memory."""
        self._captured_requests = []
        self._latest_json = {}
