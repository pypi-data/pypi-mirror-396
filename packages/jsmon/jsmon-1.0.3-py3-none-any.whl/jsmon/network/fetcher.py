import asyncio
import aiohttp
import redis.asyncio as redis
import time
from jsmon.network.browser import OptimizedBrowserHandler
from jsmon.network.waf import WAFDetector
from jsmon.network.headers import SmartHeaders
from jsmon.config.constants import DEFAULT_RETRY_ATTEMPTS, DEFAULT_RETRY_DELAY

# TEMP DEBUG: Track active browser requests
_active_browser_requests = {}

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
        redis_start = time.time()
        try:
            cached = await asyncio.wait_for(self.r.get(cache_key), timeout=5.0)
        except asyncio.TimeoutError:
            print(f"[REDIS TIMEOUT] Cache check for {url[:60]}...")
            cached = None
        redis_elapsed = time.time() - redis_start
        if redis_elapsed > 1:
            print(f"[REDIS SLOW] Cache check took {redis_elapsed:.1f}s for {url[:60]}...")
        if cached:
            return cached.decode(), 200, 'cache'

        # 2. Try aiohttp
        headers = self.headers_manager.get_headers(url)
        if referer: headers['Referer'] = referer
        if bearer_token: headers['Authorization'] = f"Bearer {bearer_token}"

        try:
            aio_start = time.time()
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
        # TEMP DEBUG: Track browser requests
        request_id = id(asyncio.current_task())
        _active_browser_requests[request_id] = {
            'url': url,
            'start': time.time(),
            'stage': 'starting'
        }
        print(f"[BROWSER START] {url} (active: {len(_active_browser_requests)})")
        
        try:
            _active_browser_requests[request_id]['stage'] = 'fetching'
            content, status, _ = await self.browser.fetch_with_browser(url, referer=referer)
            _active_browser_requests[request_id]['stage'] = 'done'
            elapsed = time.time() - _active_browser_requests[request_id]['start']
            print(f"[BROWSER DONE] {url} in {elapsed:.1f}s (status={status})")
            
            if status == 200 and content:
                await self.r.set(cache_key, content, ex=3600)
                return content, status, 'browser'
                
            return "", status, 'failed'
        finally:
            _active_browser_requests.pop(request_id, None)
            # TEMP DEBUG: Show remaining active requests
            if _active_browser_requests:
                for rid, info in _active_browser_requests.items():
                    elapsed = time.time() - info['start']
                    print(f"[BROWSER ACTIVE] {info['url'][:60]}... ({elapsed:.0f}s, stage={info['stage']})")
