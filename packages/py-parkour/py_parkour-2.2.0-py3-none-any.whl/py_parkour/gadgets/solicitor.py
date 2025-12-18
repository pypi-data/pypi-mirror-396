import asyncio
import aiohttp
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from playwright.async_api import Page

class CaptchaSolver(ABC):
    """
    Abstract Base Class for Captcha Solvers.
    Any provider (2Captcha, AntiCaptcha, etc.) must implement solve().
    """
    @abstractmethod
    async def solve(self, captcha_type: str, url: str, site_key: str, **kwargs) -> str:
        """
        Generic solve method.
        :param captcha_type: 'recaptcha_v2', 'recaptcha_v3', 'hcaptcha', 'turnstile'
        :param url: Page URL
        :param site_key: Site Key
        :param kwargs: Extra params like 'action', 'min_score', 'useragent', etc.
        """
        pass

class TwoCaptchaSolver(CaptchaSolver):
    """
    Implementation for 2Captcha API using pure aiohttp.
    Supports: ReCaptcha V2/V3, hCaptcha, Turnstile.
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://2captcha.com"

    async def solve(self, captcha_type: str, url: str, site_key: str, **kwargs) -> str:
        async with aiohttp.ClientSession() as session:
            # Base params
            params = {
                'key': self.api_key,
                'pageurl': url,
                'json': 1
            }

            # Type mapping
            if captcha_type == 'recaptcha_v2':
                params['method'] = 'userrecaptcha'
                params['googlekey'] = site_key
            elif captcha_type == 'recaptcha_v3':
                params['method'] = 'userrecaptcha'
                params['version'] = 'v3'
                params['googlekey'] = site_key
                params['action'] = kwargs.get('action', 'verify')
                params['min_score'] = kwargs.get('min_score', 0.3)
            elif captcha_type == 'hcaptcha':
                params['method'] = 'hcaptcha'
                params['sitekey'] = site_key
            elif captcha_type == 'turnstile':
                params['method'] = 'turnstile'
                params['sitekey'] = site_key
            else:
                raise ValueError(f"TwoCaptchaSolver: Unsupported type '{captcha_type}'")

            # 1. Submit Request
            async with session.post(f"{self.base_url}/in.php", data=params) as resp:
                data = await resp.json()
                if data.get('status') != 1:
                    raise RuntimeError(f"2Captcha Error (Submit): {data.get('request')}")
                request_id = data['request']
            
            print(f"Solicitor: Task ({captcha_type}) submitted to 2Captcha (ID: {request_id}). Waiting...")

            # 2. Poll for Result
            for _ in range(30): # Wait up to 150s
                await asyncio.sleep(5)
                async with session.get(f"{self.base_url}/res.php?key={self.api_key}&action=get&id={request_id}&json=1") as resp:
                    data = await resp.json()
                    status = data.get('status')
                    result = data.get('request')

                    if status == 1:
                        print("Solicitor: Captcha solved!")
                        return result
                    
                    if result != "CAPCHA_NOT_READY":
                        raise RuntimeError(f"2Captcha Error (Poll): {result}")
            
            raise TimeoutError("Solicitor: Timed out waiting for captcha solution.")

class Solicitor:
    """
    The Solicitor Gadget: Handles 3rd party Captcha solving.
    """
    def __init__(self, page: Page):
        self.page = page
        self.solver: Optional[CaptchaSolver] = None

    def set_solver(self, solver: CaptchaSolver):
        """Register a solver implementation."""
        self.solver = solver

    async def _ensure_solver(self):
        if not self.solver:
            raise RuntimeError("No solver configured. Call bot.solicitor.set_solver(...) first.")

    async def solve_recaptcha_v2(self, site_key: str = None, auto_inject: bool = True) -> str:
        """Solves ReCaptcha V2 (Checkbox)"""
        await self._ensure_solver()
        if not site_key:
            site_key = await self._detect_sitekey("data-sitekey", "iframe[src*='recaptcha']")
        
        token = await self.solver.solve('recaptcha_v2', self.page.url, site_key)
        
        if auto_inject:
             await self.page.evaluate(f'''
                document.getElementById("g-recaptcha-response").innerHTML = "{token}";
                if (typeof callback !== "undefined") callback("{token}");
            ''')
             print("Solicitor: Injected V2 token.")
        return token

    async def solve_recaptcha_v3(self, site_key: str, action: str = 'verify', min_score: float = 0.3) -> str:
        """Solves ReCaptcha V3 (Invisible). No auto-inject as usually requires custom callback."""
        await self._ensure_solver()
        # V3 sitekey is often in script tags or global config, harder to auto-detect reliably.
        # So we expect user to pass it.
        token = await self.solver.solve('recaptcha_v3', self.page.url, site_key, action=action, min_score=min_score)
        print(f"Solicitor: Retrieved V3 token (action={action})")
        return token

    async def solve_hcaptcha(self, site_key: str = None, auto_inject: bool = True) -> str:
        """Solves hCaptcha"""
        await self._ensure_solver()
        if not site_key:
            site_key = await self._detect_sitekey("data-sitekey", "iframe[src*='hcaptcha']")

        token = await self.solver.solve('hcaptcha', self.page.url, site_key)

        if auto_inject:
             await self.page.evaluate(f'''
                document.getElementsByName("h-captcha-response")[0].innerHTML = "{token}";
                document.getElementsByName("g-recaptcha-response")[0].innerHTML = "{token}";
            ''')
             print("Solicitor: Injected hCaptcha token.")
        return token

    async def solve_turnstile(self, site_key: str = None, auto_inject: bool = True) -> str:
        """Solves Cloudflare Turnstile"""
        await self._ensure_solver()
        if not site_key:
             # Turnstile often uses class="cf-turnstile" and data-sitekey
             site_key = await self._detect_sitekey("data-sitekey", ".cf-turnstile")

        token = await self.solver.solve('turnstile', self.page.url, site_key)
        
        if auto_inject:
             # Turnstile input name is 'cf-turnstile-response'
             await self.page.evaluate(f'''
                document.getElementsByName("cf-turnstile-response")[0].value = "{token}";
            ''')
             print("Solicitor: Injected Turnstile token.")
        return token

    async def _detect_sitekey(self, attr: str, selector_fallback: str) -> str:
        """Helper to find sitekey via attribute or fallback"""
        # 1. Try generic attribute search
        element = self.page.locator(f"[{attr}]").first
        if await element.count() > 0:
            key = await element.get_attribute(attr)
            print(f"Solicitor: Detected site_key {key} via attribute")
            return key
            
        print("Solicitor: Could not auto-detect site_key via attribute. Trying heuristics...")
        raise ValueError("Could not auto-detect site_key. Please provide it manually.")
