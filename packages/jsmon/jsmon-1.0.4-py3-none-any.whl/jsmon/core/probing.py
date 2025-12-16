import re
import time
import json
import asyncio
import hashlib
import sys
from urllib.parse import urljoin
from pathlib import Path
from jsmon.network.browser import advanced_spa_wait
from jsmon.reporting.templates import RESULT_CARD_TEMPLATE # This is circular if reporting imports probing. 
# Wait, reporting imports probing results, not functions. 
# Actually generate_report_and_notify calls probing functions.
# So reporting -> probing.
# But probing doesn't need reporting templates.
# I will remove the import if not needed.
# ProbeResultWithScreenshot was defined in the original script. I need to define it here or in a common place.
# It's a dataclass. I'll put it in jsmon/models.py or jsmon/core/models.py
# For now I'll define it here.

from dataclasses import dataclass

@dataclass
class ProbeResultWithScreenshot:
    """Endpoint testing result with screenshot."""
    url: str
    display_name: str
    status: int
    title: str
    content_length: int
    response_time: float
    screenshot_path: str
    fetch_method: str = "browser"

    @property
    def screenshot_filename(self):
        return os.path.basename(self.screenshot_path) if self.screenshot_path else ""

import os

DYNAMIC_TEST_VALUES = {
    'numeric_id': ['1', '123', '0', '999999'],
    'uuid': ['123e4567-e89b-12d3-a456-426614174000', 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11'],
    'string_id': ['test', 'admin', 'user', 'demo'],
    'hash': ['d41d8cd98f00b204e9800998ecf8427e', 'abc123'],
    'email': ['admin@example.com', 'test@test.com'],
    'filename': ['config.json', 'data.xml', 'backup.sql'],
    'version': ['v1', 'v2', 'latest', '1.0'],
}

def detect_parameter_type(endpoint_context):
    """Determines the most likely parameter type based on the endpoint context."""
    endpoint_context = endpoint_context.lower()
    if 'user' in endpoint_context or 'id' in endpoint_context: return 'numeric_id'
    if 'uuid' in endpoint_context or 'guid' in endpoint_context: return 'uuid'
    if 'email' in endpoint_context or 'mail' in endpoint_context: return 'email'
    if 'file' in endpoint_context or 'image' in endpoint_context: return 'filename'
    if 'hash' in endpoint_context or 'token' in endpoint_context: return 'hash'
    return 'numeric_id' # Default

def generate_probe_endpoints(sanitized_endpoint, max_variants=2):
    """Generates endpoints for probing with validation"""
    if '{dynamic}' not in sanitized_endpoint:
        return [(sanitized_endpoint, sanitized_endpoint)]
    
    param_type = detect_parameter_type(sanitized_endpoint)
    test_values = DYNAMIC_TEST_VALUES.get(param_type, ['1'])[:max_variants]
    
    variants = []
    for val in test_values:
        url = sanitized_endpoint.replace('{dynamic}', val)
        variants.append((url, f"{sanitized_endpoint} ({val})"))
    return variants

async def stealth_probe_endpoint(session, base_url, endpoint_info, semaphore, timing, header_manager):
    """Stealth version probing endpoints"""
    if isinstance(endpoint_info, tuple):
        probe_url, display_name = endpoint_info
    else:
        probe_url = display_name = endpoint_info
        
    full_url = urljoin(base_url, probe_url)
    
    async with semaphore:
        await timing.get_delay()
        headers = header_manager.get_headers(full_url)
        
        try:
            async with session.get(full_url, headers=headers, timeout=10, ssl=False, allow_redirects=True) as resp:
                status = resp.status
                length = 0
                if 'content-length' in resp.headers:
                    length = int(resp.headers['content-length'])
                else:
                    content = await resp.read()
                    length = len(content)
                
                title = "N/A"
                # Simple title extraction
                if 'html' in resp.headers.get('Content-Type', '').lower():
                    try:
                        content_str = await resp.text(errors='ignore')
                        m = re.search(r'<title>(.*?)</title>', content_str, re.IGNORECASE)
                        if m: title = m.group(1).strip()[:100]
                    except: pass
                    
                return display_name, status, length, title
        except Exception as e:
            return display_name, 0, 0, f"Request Error: {type(e).__name__}"

async def _take_screenshot(page, full_url: str, status: int, screenshots_dir: Path) -> str:
    """Universal function for creating screenshots."""
    try:
        url_hash = hashlib.md5(full_url.encode()).hexdigest()[:12]
        screenshot_filename = f"{url_hash}_{status}.png"
        screenshot_path = screenshots_dir / screenshot_filename
        
        await page.screenshot(path=str(screenshot_path), full_page=False, type='png')
        return str(screenshot_path)
    except Exception:
        return ""

def _create_error_result(full_url, display_name, error_msg, fetch_method="unknown"):
    return ProbeResultWithScreenshot(
        url=full_url, display_name=display_name, status=0, title=error_msg,
        content_length=0, response_time=0, screenshot_path="", fetch_method=fetch_method
    )

async def _probe_with_aiohttp(session, full_url, display_name, header_manager, bearer_token=None):
    headers = header_manager.get_headers(full_url)
    if bearer_token: headers['Authorization'] = f'Bearer {bearer_token}'
    
    try:
        start_time = time.time()
        async with session.get(full_url, headers=headers, timeout=15, ssl=False, allow_redirects=True) as resp:
            status = resp.status
            content = await resp.read()
            length = len(content)
            response_time = int((time.time() - start_time) * 1000)
            
            title = "N/A"
            if 'html' in resp.headers.get('Content-Type', '').lower():
                try:
                    content_str = content.decode('utf-8', errors='ignore')
                    m = re.search(r'<title>(.*?)</title>', content_str, re.IGNORECASE)
                    if m: title = m.group(1).strip()[:100]
                except: title = "Parse Error"
            
            return ProbeResultWithScreenshot(
                url=full_url, display_name=display_name, status=status, title=title,
                content_length=length, response_time=response_time, screenshot_path="", fetch_method="aiohttp"
            )
    except Exception as e:
        return _create_error_result(full_url, display_name, f"Request Error: {type(e).__name__}", "aiohttp")

async def _probe_with_playwright(full_url, display_name, playwright_context, domain_session, screenshots_dir, session=None, header_manager=None):
    page = None
    try:
        page = await playwright_context.new_page()
        if domain_session:
            await page.context.add_cookies(domain_session.cookies)
            if domain_session.localstorage:
                await page.add_init_script(f"""
                    const storage = {json.dumps(domain_session.localstorage)};
                    for (const [key, value] of Object.entries(storage)) {{
                        localStorage.setItem(key, value);
                    }}
                """)
            if domain_session.bearer_token:
                await page.set_extra_http_headers({'Authorization': f'Bearer {domain_session.bearer_token}'})
        
        start_time = time.time()
        response = await page.goto(full_url, wait_until='domcontentloaded', timeout=15000)
        
        if not response: raise Exception("No response received")
        
        try: await advanced_spa_wait(page, debug=False)
        except: pass
        
        status = response.status
        length = 0
        try: length = int(response.headers.get('content-length', 0))
        except: pass
        if length == 0:
            try: length = len(await response.body())
            except: pass
            
        title = "N/A"
        try: title = await page.title()
        except: pass
        
        screenshot_path = ""
        if screenshots_dir:
            screenshot_path = await _take_screenshot(page, full_url, status, screenshots_dir)
            
        response_time = int((time.time() - start_time) * 1000)
        
        return ProbeResultWithScreenshot(
            url=full_url, display_name=display_name, status=status, title=title.strip()[:100],
            content_length=length, response_time=response_time, screenshot_path=screenshot_path, fetch_method="browser"
        )
        
    except Exception as e:
        # Fallback logic
        if session and header_manager:
            bearer = domain_session.bearer_token if domain_session else None
            fallback = await _probe_with_aiohttp(session, full_url, display_name, header_manager, bearer_token=bearer)
            fallback.fetch_method = "fallback"
            return fallback
            
        return _create_error_result(full_url, display_name, f"Browser Error: {type(e).__name__}", "browser")
    finally:
        if page and not page.is_closed():
            try: await page.close()
            except: pass

async def stealth_probe_endpoint_with_auth(session, base_url, endpoint_info, semaphore, timing, header_manager, domain_session=None, playwright_context=None, screenshots_dir: Path = None):
    if isinstance(endpoint_info, tuple):
        probe_url, display_name = endpoint_info
    else:
        probe_url = display_name = endpoint_info
    
    full_url = urljoin(base_url, probe_url)
    
    async with semaphore:
        await timing.get_delay()
        
        if playwright_context:
            return await _probe_with_playwright(full_url, display_name, playwright_context, domain_session, screenshots_dir, session, header_manager)
        elif screenshots_dir:
            return _create_error_result(full_url, display_name, "No browser context - config error", "configuration_error")
        else:
            bearer = domain_session.bearer_token if domain_session else None
            return await _probe_with_aiohttp(session, full_url, display_name, header_manager, bearer_token=bearer)
