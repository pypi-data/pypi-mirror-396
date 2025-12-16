import aiohttp
from typing import Optional, Dict, Any
from jsmon.analysis.ai_providers import get_ai_provider, format_ai_alert
from jsmon.analysis.trivia_filter import should_analyze_with_ai


async def send_diff_to_ai(
    session: aiohttp.ClientSession,
    diff: str,
    js_url: str,
    args,
    source_page: str = None,
    skip_trivia_check: bool = False,
) -> Optional[Dict[str, Any]]:
    """
    Sends a diff to the configured AI provider for analysis.
    
    Args:
        session: aiohttp session
        diff: The diff to analyze
        js_url: URL of the JS file
        args: Command line arguments
        source_page: Page where JS was found
        skip_trivia_check: If True, skip trivia filter (already checked by caller)
    
    Returns:
        Dict with analysis results or None if no analysis needed/failed
    """
    provider_name = getattr(args, "ai_provider", None)
    api_key = getattr(args, "ai_api_key", None)
    model = getattr(args, "ai_model", None)
    debug = getattr(args, "debug", False)

    if not provider_name or not api_key:
        return None

    # Pre-filter trivial diffs to save API calls
    # Skip if caller already checked (engine.py does its own check)
    if not skip_trivia_check:
        should_analyze, reason = await should_analyze_with_ai(diff, js_url, debug)
        
        if not should_analyze:
            if debug:
                print(f"[AI] Skipping {js_url}: {reason}")
            return None

    # Get AI provider
    provider = get_ai_provider(provider_name, api_key, model)
    if not provider:
        if debug:
            print(f"[AI] Unknown provider: {provider_name}")
        return None

    if debug:
        print(f"[AI] Analyzing {js_url} with {provider_name} ({len(diff)} chars)...")
        # Log AI request with full diff
        try:
            from jsmon.analysis.debug_logger import log_ai_request
            log_ai_request(
                js_url=js_url,
                source_page=source_page or "Unknown",
                diff_content=diff,
                provider=provider_name,
                model=model or provider.model
            )
        except ImportError:
            pass

    # Send to AI
    result = await provider.analyze_diff(
        session, diff, js_url, source_page or "Unknown"
    )

    if debug:
        # Log AI response with raw response for debugging
        try:
            from jsmon.analysis.debug_logger import log_ai_response
            # Get raw response if provider supports it
            raw_response = None
            if hasattr(provider, 'get_last_raw_response'):
                raw_response = provider.get_last_raw_response()
            
            if result:
                log_ai_response(
                    js_url=js_url,
                    has_changes=result.get("has_changes", False),
                    changes=result.get("changes", []),
                    summary=result.get("summary", ""),
                    raw_response=raw_response
                )
            else:
                log_ai_response(
                    js_url=js_url,
                    has_changes=False,
                    changes=[],
                    summary="",
                    raw_response=raw_response,
                    error="No response from AI provider"
                )
        except ImportError:
            pass
        
        if result:
            has_changes = result.get("has_changes", False)
            changes_count = len(result.get("changes", []))
            print(f"[AI] Result: has_changes={has_changes}, changes={changes_count}")

    return result


def get_ai_alert_text(result: Dict[str, Any]) -> str:
    """
    Convert AI analysis result to human-readable alert text.
    
    Args:
        result: AI analysis result dict
        
    Returns:
        Formatted alert string or empty string if no changes
    """
    return format_ai_alert(result)
