import asyncio
import aiohttp
import redis.asyncio as redis
from jsmon.network.browser import OptimizedBrowserHandler
from jsmon.network.waf import WAFDetector
from jsmon.network.headers import SmartHeaders
from jsmon.config.constants import DEFAULT_RETRY_ATTEMPTS, DEFAULT_RETRY_DELAY

class SmartCachingHybridFetcher:
    """
    Orchestrates fetching:
    1. Tries aiohttp (fast)
    2. Checks for WAF
    3. If blocked, uses Browser (slow but effective)
    4. Caches results in Redis
    """
    def __init__(self, session: aiohttp.ClientSession, redis_client: redis.Redis, browser_handler: OptimizedBrowserHandler):
        self.session = session
        self.r = redis_client
        self.browser = browser_handler
        self.headers_manager = SmartHeaders()

    async def fetch(self, url: str, referer: str = None, bearer_token: str = None) -> tuple:
        """
        Returns: (content, status, source_type)
        source_type: 'aiohttp', 'browser', 'cache'
        """
        # 1. Check cache
        cache_key = f"cache:{url}"
        cached = await self.r.get(cache_key)
        if cached:
            return cached.decode(), 200, 'cache'

        # 2. Try aiohttp
        headers = self.headers_manager.get_headers(url)
        if referer: headers['Referer'] = referer
        if bearer_token: headers['Authorization'] = f"Bearer {bearer_token}"

        try:
            async with self.session.get(url, headers=headers, timeout=15, ssl=False) as resp:
                content = await resp.text()
                status = resp.status
                
                is_blocked, waf_type, needs_browser = WAFDetector.detect_waf_type(content, dict(resp.headers), status)
                
                if not is_blocked and status == 200:
                    await self.r.set(cache_key, content, ex=3600)
                    return content, status, 'aiohttp'
                
                if not needs_browser and status not in [403, 406, 429]:
                     return content, status, 'aiohttp'
                     
                print(f"[WAF] Detected {waf_type} for {url}, switching to browser...")

        except Exception as e:
            print(f"[FETCH] aiohttp failed for {url}: {e}")

        # 3. Fallback to browser
        content, status, _ = await self.browser.fetch_with_browser(url, referer=referer)
        if status == 200 and content:
            await self.r.set(cache_key, content, ex=3600)
            return content, status, 'browser'
            
        return "", status, 'failed'
