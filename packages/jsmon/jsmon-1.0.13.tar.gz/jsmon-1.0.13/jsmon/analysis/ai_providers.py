import abc
import aiohttp
import asyncio
import json
import random
from typing import Optional, Dict, Any, List


# Retry configuration
MAX_RETRIES = 3
BASE_DELAY = 1.0  # seconds
MAX_DELAY = 30.0  # seconds

# Retryable HTTP status codes
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


async def retry_with_backoff(
    coro_func,
    max_retries: int = MAX_RETRIES,
    base_delay: float = BASE_DELAY,
    max_delay: float = MAX_DELAY,
    retryable_statuses: set = RETRYABLE_STATUS_CODES
):
    """
    Execute coroutine with exponential backoff retry logic.
    
    Args:
        coro_func: Async function that returns (result, status_code) or raises exception
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
        retryable_statuses: Set of HTTP status codes that should trigger retry
    
    Returns:
        Result from successful execution or None after all retries exhausted
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            result, status_code = await coro_func()
            
            # Success
            if status_code == 200:
                return result
            
            # Non-retryable error
            if status_code not in retryable_statuses:
                print(f"[AI Retry] Non-retryable status {status_code}, giving up")
                return None
            
            # Retryable error - continue to retry logic below
            print(f"[AI Retry] Got status {status_code}, will retry...")
            
        except asyncio.TimeoutError as e:
            last_exception = e
            print(f"[AI Retry] Timeout on attempt {attempt + 1}/{max_retries + 1}")
        except aiohttp.ClientError as e:
            last_exception = e
            print(f"[AI Retry] Client error on attempt {attempt + 1}: {e}")
        except Exception as e:
            last_exception = e
            print(f"[AI Retry] Unexpected error on attempt {attempt + 1}: {e}")
        
        # Don't sleep after the last attempt
        if attempt < max_retries:
            # Exponential backoff with jitter
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = random.uniform(0, delay * 0.1)  # 10% jitter
            total_delay = delay + jitter
            
            print(f"[AI Retry] Waiting {total_delay:.1f}s before retry {attempt + 2}/{max_retries + 1}")
            await asyncio.sleep(total_delay)
    
    print(f"[AI Retry] All {max_retries + 1} attempts failed")
    if last_exception:
        print(f"[AI Retry] Last error: {last_exception}")
    return None


class AIProvider(abc.ABC):
    """Abstract base class for AI providers."""

    def __init__(self, api_key: str, model: str = None):
        self.api_key = api_key
        self.model = model

    @abc.abstractmethod
    async def analyze_diff(
        self, session: aiohttp.ClientSession, diff: str, js_url: str, source_page: str
    ) -> Optional[Dict[str, Any]]:
        """Analyzes the diff and returns a structured JSON response."""
        pass


class GeminiProvider(AIProvider):
    """Google Gemini API provider."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1/models/{model}:generateContent"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash-lite"):
        super().__init__(api_key, model)
        self.url = self.BASE_URL.format(model=self.model)
        self._last_raw_response = None  # Store raw response for debugging
    
    def get_last_raw_response(self) -> Optional[str]:
        """Get the last raw response from Gemini for debugging."""
        return self._last_raw_response

    def _create_prompt(self, diff: str, js_url: str, source_page: str) -> str:
        return f"""
## Task: Analyze JavaScript Code Changes

### Context
- **JS File:** {js_url}
- **Found on page:** {source_page}

### Your Mission
Analyze this diff and find **meaningful code changes** in ACTIVE (non-commented) code.

### REPORT these types:
| Type | Description | Examples |
|------|-------------|----------|
| new_endpoint | New HTTP endpoint | fetch, axios, XMLHttpRequest calls |
| new_param | New request parameter | query params, headers, body fields |
| feature_flag | NEW feature flag | new key in experiments/flags object |
| access_control | Roles, permissions | role checks, permission grants, auth bypass |
| security_change | Security weakening | validation removed, auth bypass, hardcoded creds |
| payment_logic | Payment/pricing changes | discounts, subscriptions, price calculations |
| file_operation | File upload/download | upload handlers, file processing, export |
| data_exposure | Data export/leak risk | PII export, bulk data access, user enumeration |
| external_integration | Third-party APIs | webhooks, OAuth, external service calls |
| client_storage | Browser storage | localStorage, sessionStorage, cookies, IndexedDB |
| input_handling | Input processing | validation changes, sanitization, parsing |
| redirect_logic | URL redirects | window.location, navigate, redirect params |
| websocket | Real-time connections | WebSocket, Socket.io, SSE |
| crypto_operation | Cryptography | encryption, hashing, token generation |
| debug_code | Dev/test code | console.log, debugger, test endpoints |

### HIGH-VALUE CHANGES for Bug Bounty (prioritize these):

**security_change** (CRITICAL):
- SSRF: accepting user URL in fetch/proxy
- Auth bypass: && changed to ||, skipAuth parameters
- Hardcoded credentials: passwords, API keys
- Obfuscated endpoints: atob(), String.fromCharCode()

**payment_logic** (HIGH):
- New discount/coupon logic
- Price calculation changes
- Subscription tier changes
- Free trial logic

**file_operation** (HIGH):
- New upload endpoints
- File type validation changes
- Download/export functions

**data_exposure** (HIGH):
- Bulk data export
- User enumeration endpoints
- PII in responses

**client_storage** (MEDIUM):
- Tokens in localStorage (not httpOnly)
- Role/permission stored client-side
- Sensitive data in cookies

**redirect_logic** (MEDIUM):
- Open redirect potential
- URL parameter in redirect

### DO NOT REPORT (noise):
- Webpack chunk hash changes (abc123 -> xyz789)
- Source map URL changes
- Asset/CDN URL changes
- Session ID, CSRF token, request ID changes
- A/B test BUCKET reassignment (existing test changing bucket: control→treatment, enabled:false→true)
- Feature flag VALUE changes (same flag, different value) - this is NOT a new feature
- React key prop changes
- **Variable/function/constant RENAMES** (ENABLE_X → X_ENABLED is just rename, not new flag!)
- Version bumps without new functionality
- Error message text changes
- Logging format changes
- CSS/style changes
- **COMMENTED OUT CODE** (lines starting with //, /* */, or inside comments)
- **MOCK/TEST CODE** (MockService, Mock*, [MOCK], console.log("[MOCK]"), test-only code, localhost checks)
- **TODO comments** (// TODO:, // FIXME:)
- **Dead code** (unused variables, _unused_ prefixed)
- **Conditional mock services** (if hostname==="localhost" use MockService - this is dev-only)

### IMPORTANT RULES:
1. If you find security_change → ALWAYS set has_changes: true
2. A/B bucket change (control→treatment) is NOT a new feature flag - the flag already existed!
   Example NOISE: mail_redesign changing from control to treatment (same flag, different bucket)
   Example NEW: Adding NEW_CHECKOUT that wasn't there before (completely new flag)
3. Report ALL new parameters, not just sensitive ones
4. When in doubt about noise → don't report
5. **IGNORE commented code** - if it's in // or /* */, it's not active
6. **IGNORE mock/test services** - MockPaymentService, [MOCK] logs are not production code
7. **SSRF is ALWAYS security_change** - accepting arbitrary URLs is dangerous
8. **RENAMES are NOT new features** - ENABLE_DARK_MODE → DARK_MODE_ENABLED is the SAME flag renamed!
   If the same flags exist before and after with just different naming convention → has_changes: false
9. **Mock services with localhost check are noise** - code like `hostname==="localhost"?MockService:RealService` is dev-only
10. **MockService/Mock* classes are ALWAYS noise** - they are test doubles, not production code
    If you see MockPaymentService, MockUserService, etc. → ignore them completely

### Diff:
```diff
{diff[:30000]}
```

### Response Format (JSON):
{{
    "has_changes": true/false,
    "changes": [
        {{
            "type": "new_endpoint|new_param|feature_flag|access_control|security_change|new_function|debug_code",
            "title": "Short title (e.g. 'Admin Delete API')",
            "description": "What changed and why it matters",
            "code": "relevant code snippet (1-3 lines)",
            "severity": "critical|high|medium|low|info"
        }}
    ],
    "summary": "One sentence summary of all changes"
}}

If NO meaningful changes found:
{{
    "has_changes": false,
    "changes": [],
    "summary": "No significant changes - only [describe what noise was filtered]"
}}
"""

    async def analyze_diff(
        self, session: aiohttp.ClientSession, diff: str, js_url: str, source_page: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze diff with retry logic and exponential backoff."""
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}

        prompt = self._create_prompt(diff, js_url, source_page)

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1},
        }

        async def make_request():
            """Inner function for retry wrapper."""
            async with session.post(
                self.url, params=params, json=payload, headers=headers, timeout=90
            ) as resp:
                status_code = resp.status
                
                if status_code != 200:
                    text = await resp.text()
                    print(f"[Gemini] Error {status_code}: {text[:200]}")
                    return None, status_code

                data = await resp.json()
                return data, status_code

        # Execute with retry
        data = await retry_with_backoff(make_request)
        
        if data is None:
            return None

        # Parse response
        try:
            text_response = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Store raw response for debug logging
            self._last_raw_response = text_response

            # Parse JSON from response with aggressive cleaning
            clean = text_response.strip()
            
            # Remove markdown code blocks
            if clean.startswith("```"):
                parts = clean.split("```")
                if len(parts) > 1:
                    clean = parts[1]
                    if clean.startswith("json"):
                        clean = clean[4:]
                    clean = clean.strip()
            
            # Try to find JSON object boundaries
            if not clean.startswith("{"):
                start = clean.find("{")
                if start != -1:
                    clean = clean[start:]
            
            if not clean.endswith("}"):
                end = clean.rfind("}")
                if end != -1:
                    clean = clean[:end+1]
            
            # Fix common JSON issues
            import re
            # Remove trailing commas before } or ]
            clean = re.sub(r',\s*([}\]])', r'\1', clean)
            
            result = json.loads(clean)

            # Add metadata
            result["js_url"] = js_url
            result["source_page"] = source_page

            return result

        except (KeyError, IndexError, json.JSONDecodeError) as e:
            print(f"[Gemini] Parsing error: {e}")
            # Try to extract basic info even if JSON is malformed
            try:
                text = data["candidates"][0]["content"]["parts"][0]["text"]
                has_changes = '"has_changes": true' in text.lower() or '"has_changes":true' in text.lower()
                if not has_changes:
                    return {
                        "has_changes": False,
                        "changes": [],
                        "summary": "Parse error - assuming no changes",
                        "js_url": js_url,
                        "source_page": source_page
                    }
            except:
                pass
            return None


class GroqProvider(AIProvider):
    """Groq API provider (Llama, Mixtral)."""

    BASE_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "llama3-70b-8192"):
        super().__init__(api_key, model)

    async def analyze_diff(
        self, session: aiohttp.ClientSession, diff: str, js_url: str, source_page: str
    ) -> Optional[Dict[str, Any]]:
        """Analyze diff with retry logic and exponential backoff."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        system_prompt = """You are a JavaScript code change analyzer. 
Analyze diffs and identify meaningful changes like new endpoints, parameters, feature flags, security changes.
Return ONLY valid JSON. No markdown, no explanation."""

        user_prompt = f"""
JS File: {js_url}
Found on: {source_page}

Analyze this diff for meaningful changes (new endpoints, params, feature flags, security changes).
Ignore: renames, hashes, comments, formatting, A/B bucket reassignment.

Diff:
{diff[:15000]}

Return JSON:
{{"has_changes": true/false, "changes": [{{"type": "...", "title": "...", "description": "...", "code": "...", "severity": "..."}}], "summary": "..."}}
"""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
        }

        async def make_request():
            """Inner function for retry wrapper."""
            async with session.post(
                self.BASE_URL, json=payload, headers=headers, timeout=60
            ) as resp:
                status_code = resp.status
                
                if status_code != 200:
                    text = await resp.text()
                    print(f"[Groq] Error {status_code}: {text[:200]}")
                    return None, status_code

                data = await resp.json()
                return data, status_code

        # Execute with retry
        data = await retry_with_backoff(make_request)
        
        if data is None:
            return None

        try:
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)

            result["js_url"] = js_url
            result["source_page"] = source_page

            return result
        except Exception as e:
            print(f"[Groq] Parsing failed: {e}")
            return None


def get_ai_provider(
    provider_name: str, api_key: str, model: str = None
) -> Optional[AIProvider]:
    """Factory function to get AI provider instance."""
    providers = {
        "gemini": (GeminiProvider, "gemini-2.5-flash-lite"),
        "groq": (GroqProvider, "llama3-70b-8192"),
    }

    provider_info = providers.get(provider_name.lower())
    if not provider_info:
        return None

    provider_class, default_model = provider_info
    return provider_class(api_key, model or default_model)


def format_ai_alert(result: Dict[str, Any]) -> str:
    """Format AI analysis result as human-readable alert."""
    if not result or not result.get("has_changes"):
        return ""

    lines = []
    js_url = result.get("js_url", "Unknown")
    source_page = result.get("source_page", "Unknown")

    for change in result.get("changes", []):
        severity = change.get("severity", "info").upper()
        title = change.get("title", "Unknown change")
        description = change.get("description", "")
        code = change.get("code", "")
        change_type = change.get("type", "other")

        # Severity icons
        icon = {"CRITICAL": "🔴", "HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "INFO": "🟢"}.get(
            severity, "⚪"
        )

        lines.append(f"{icon} [{severity}] {title}")
        lines.append(f"   Type: {change_type}")
        lines.append(f"   JS: {js_url}")
        lines.append(f"   Page: {source_page}")
        if description:
            lines.append(f"   {description[:200]}")
        if code:
            lines.append(f"   Code: {code[:150]}")
        lines.append("")

    if result.get("summary"):
        lines.append(f"Summary: {result['summary']}")

    return "\n".join(lines)
