import random
from urllib.parse import urlparse

REALISTIC_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

class SmartHeaders:
    """Manages HTTP headers to mimic a real browser."""
    def __init__(self):
        self.base_headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        self.ua = random.choice(REALISTIC_USER_AGENTS)
        self.cookies = {}

    def get_headers(self, url: str) -> dict:
        headers = self.base_headers.copy()
        headers['User-Agent'] = self.ua
        
        parsed = urlparse(url)
        headers['Host'] = parsed.netloc
        
        # Add cookies if available
        if self.cookies:
            cookie_str = '; '.join([f"{k}={v}" for k, v in self.cookies.items()])
            headers['Cookie'] = cookie_str
            
        return headers

    def update_session(self, response_headers: dict, url: str):
        """Updates cookies from the response."""
        # Simple cookie parsing (can be improved)
        if 'Set-Cookie' in response_headers:
            # Logic for parsing Set-Cookie
            pass
