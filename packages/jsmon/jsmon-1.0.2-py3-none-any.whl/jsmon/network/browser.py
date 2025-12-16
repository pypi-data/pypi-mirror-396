import asyncio
import json
import random
from playwright.async_api import async_playwright
from jsmon.network.headers import REALISTIC_USER_AGENTS

async def advanced_spa_wait(page, timeout=10000, debug=False):
    """
    Intelligently waits for SPA content to load by monitoring network activity.
    """
    try:
        # 1. Basic wait for load state
        await page.wait_for_load_state('domcontentloaded', timeout=timeout)
        
        # 2. Waiting for network silence (no new requests for 500ms)
        await page.wait_for_load_state('networkidle', timeout=timeout)
        
        # 3. Additional check for dynamic content
        # (e.g. checking for spinner disappearance or content appearance)
        # This is a simplified version
        await asyncio.sleep(1) 
        
    except Exception as e:
        if debug:
            print(f"[SPA] Wait warning: {e}")

class OptimizedBrowserHandler:
    """
    Optimized Playwright wrapper:
    - Resource blocking (images, fonts)
    - Session injection
    - WAF bypass
    """
    def __init__(self, concurrency=2):
        self.concurrency = concurrency
        self.playwright = None
        self.browser = None
        self.context = None
        self.semaphore = asyncio.Semaphore(concurrency)
        self.active_pages = 0

    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-features=IsolateOrigins,site-per-process',
            ]
        )
        
        self.context = await self.browser.new_context(
            user_agent=random.choice(REALISTIC_USER_AGENTS),
            viewport={'width': 1920, 'height': 1080},
            java_script_enabled=True,
            ignore_https_errors=True
        )
        
        # Blocking unnecessary resources
        await self.context.route("**/*", self._handle_route)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.context: await self.context.close()
        if self.browser: await self.browser.close()
        if self.playwright: await self.playwright.stop()

    async def _handle_route(self, route):
        resource_type = route.request.resource_type
        if resource_type in ['image', 'media', 'font', 'stylesheet']:
            await route.abort()
        else:
            await route.continue_()

    async def fetch_with_browser(self, url: str, domain_session=None, referer=None) -> tuple:
        """
        Returns: (content, status, title)
        """
        async with self.semaphore:
            page = await self.context.new_page()
            try:
                # Inject session
                if domain_session:
                    await self.context.add_cookies(domain_session.cookies)
                    if domain_session.localstorage:
                        await page.add_init_script(f"""
                            const storage = {json.dumps(domain_session.localstorage)};
                            for (const [key, value] of Object.entries(storage)) {{
                                localStorage.setItem(key, value);
                            }}
                        """)
                    if domain_session.bearer_token:
                        await page.set_extra_http_headers({
                            'Authorization': f'Bearer {domain_session.bearer_token}'
                        })

                if referer:
                    await page.set_extra_http_headers({'Referer': referer})

                response = await page.goto(url, wait_until='domcontentloaded', timeout=30000)
                
                if not response:
                    return "", 0, ""

                # WAF check and wait
                await advanced_spa_wait(page)
                
                content = await page.content()
                status = response.status
                title = await page.title()
                
                return content, status, title

            except Exception as e:
                print(f"[BROWSER] Error fetching {url}: {e}")
                return "", 0, ""
            finally:
                await page.close()
