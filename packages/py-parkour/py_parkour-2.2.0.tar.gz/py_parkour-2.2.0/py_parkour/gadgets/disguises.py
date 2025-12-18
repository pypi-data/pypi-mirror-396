import random
import asyncio
import re

class Identity:
    def __init__(self, email: str, country: str):
        self.email = email
        self.country = country

class Disguises:
    """
    Wrapper for free/cheap temporary email and SMS APIs.
    """
    def __init__(self):
        # In a real app, we would initialize API clients here.
        # For now, we use a mock verification flow.
        pass

    async def generate_identity(self, country: str = "US") -> Identity:
        """
        Generates a temporary email (Mock).
        """
        # Mock generation
        domain = "tempmail.com"
        username = f"user_{random.randint(1000, 9999)}"
        email = f"{username}@{domain}"
        await asyncio.sleep(0.5) # Simulate API call
        return Identity(email=email, country=country)

    async def wait_for_code(self, regex_pattern: str = r"(\d+)") -> str:
        """
        Polling logic that waits for an incoming email/text.
        """
        print("Disguises: Waiting for verification code (Mocking reception)...")
        # Start polling
        for _ in range(10): # Try 10 times
            await asyncio.sleep(1)
            # Mocking receiving an email
            if random.random() > 0.7: # 30% chance to 'get' it each second
                mock_body = "Your verification code is 123456."
                match = re.search(regex_pattern, mock_body)
                if match:
                    code = match.group(1)
                    print(f"Disguises: Found code {code}")
                    return code
        
        print("Disguises: Timed out waiting for code.")
        return ""
