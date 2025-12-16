"""
Debug Logger for AI Analysis Pipeline.

Logs detailed information about:
- Trivia filter decisions
- AI analysis requests/responses
- Alert generation

Output: ai_analysis_debug.log (human-readable format)
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

DEBUG_LOG_FILE = "ai_analysis_debug.log"


def _get_timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _write_log(content: str):
    """Append content to debug log file."""
    with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(content)


def log_separator(title: str = ""):
    """Write a visual separator to the log."""
    sep = "=" * 70
    if title:
        _write_log(f"\n{sep}\n{title}\n{sep}\n")
    else:
        _write_log(f"\n{sep}\n")


def log_trivia_analysis(
    js_url: str,
    diff_size: int,
    checks: Dict[str, bool],
    trivia_score: float,
    has_api_indicators: bool,
    decision: bool,
    reason: str,
    diff_content: str = None
):
    """
    Log trivia filter analysis details.
    
    Args:
        js_url: URL of the JS file
        diff_size: Size of diff in characters
        checks: Dict of check_name -> result (True = is trivial)
        trivia_score: Overall trivia score (0-1)
        has_api_indicators: Whether API indicators were found
        decision: Final decision (True = analyze with AI)
        reason: Reason for decision
        diff_content: Full diff content for later analysis
    """
    content = f"""
[{_get_timestamp()}] TRIVIA FILTER ANALYSIS
════════════════════════════════════════════════════════════════════
JS URL: {js_url}
Diff Size: {diff_size} chars

CHECKS PERFORMED:
"""
    for check_name, is_trivial in checks.items():
        status = "⚠️ TRIVIAL" if is_trivial else "✅ OK"
        content += f"  • {check_name}: {status}\n"
    
    content += f"""
SCORES:
  • Trivia Score: {trivia_score:.2f} (threshold: 0.75)
  • Has API Indicators: {'✅ YES' if has_api_indicators else '❌ NO'}

DECISION: {'🔍 ANALYZE WITH AI' if decision else '⏭️ SKIP (trivial)'}
REASON: {reason}

"""
    # Add full diff content for later analysis
    if diff_content:
        content += f"""────────────────── DIFF CONTENT ──────────────────
{diff_content}
────────────────── END DIFF ──────────────────
"""
    
    content += "════════════════════════════════════════════════════════════════════\n"
    _write_log(content)


def log_ai_request(
    js_url: str,
    source_page: str,
    diff_content: str,
    provider: str,
    model: str
):
    """
    Log AI analysis request.
    
    Args:
        js_url: URL of the JS file
        source_page: Page where JS was found
        diff_content: Full diff content sent to AI
        provider: AI provider name
        model: Model name
    """
    content = f"""
[{_get_timestamp()}] AI ANALYSIS REQUEST
════════════════════════════════════════════════════════════════════
JS URL: {js_url}
Source Page: {source_page}
Provider: {provider}
Model: {model}
Diff Size: {len(diff_content)} chars

────────────────── DIFF SENT TO AI ──────────────────
{diff_content}
────────────────── END DIFF ──────────────────
════════════════════════════════════════════════════════════════════
"""
    _write_log(content)


def log_ai_response(
    js_url: str,
    has_changes: bool,
    changes: list,
    summary: str,
    raw_response: Optional[str] = None,
    error: Optional[str] = None
):
    """
    Log AI analysis response.
    
    Args:
        js_url: URL of the JS file
        has_changes: Whether changes were detected
        changes: List of change objects
        summary: AI summary
        raw_response: Raw response text from AI (for debugging)
        error: Error message if failed
    """
    if error:
        content = f"""
[{_get_timestamp()}] AI ANALYSIS ERROR
════════════════════════════════════════════════════════════════════
JS URL: {js_url}
ERROR: {error}
════════════════════════════════════════════════════════════════════
"""
    else:
        content = f"""
[{_get_timestamp()}] AI ANALYSIS RESPONSE
════════════════════════════════════════════════════════════════════
JS URL: {js_url}
Has Changes: {'✅ YES' if has_changes else '❌ NO'}
Changes Count: {len(changes)}

"""
        if changes:
            content += "CHANGES DETECTED:\n"
            for i, change in enumerate(changes, 1):
                severity = change.get("severity", "info").upper()
                severity_icon = {
                    "CRITICAL": "🔴",
                    "HIGH": "🔴", 
                    "MEDIUM": "🟡",
                    "LOW": "🟢",
                    "INFO": "🟢"
                }.get(severity, "⚪")
                
                content += f"""
  {i}. {severity_icon} [{severity}] {change.get('title', 'Unknown')}
     Type: {change.get('type', 'other')}
     Description: {change.get('description', '')}
     Code: {change.get('code', '')}
"""
        
        content += f"""
SUMMARY: {summary}
"""
        # Add raw response for debugging AI behavior
        if raw_response:
            content += f"""
────────────────── RAW AI RESPONSE ──────────────────
{raw_response}
────────────────── END RAW RESPONSE ──────────────────
"""
        
        content += "════════════════════════════════════════════════════════════════════\n"
    
    _write_log(content)


def log_alert_sent(
    js_url: str,
    change_type: str,
    title: str,
    severity: str,
    signature: str,
    was_duplicate: bool
):
    """
    Log alert notification.
    
    Args:
        js_url: URL of the JS file
        change_type: Type of change
        title: Alert title
        severity: Severity level
        signature: Deduplication signature
        was_duplicate: Whether this was a duplicate (not sent)
    """
    if was_duplicate:
        content = f"""
[{_get_timestamp()}] ALERT SKIPPED (duplicate)
  JS: {js_url}
  Type: {change_type}
  Title: {title}
  Signature: {signature[:16]}...
"""
    else:
        content = f"""
[{_get_timestamp()}] 📬 ALERT SENT
────────────────────────────────────────────────────────────────────
JS URL: {js_url}
Type: {change_type}
Severity: {severity.upper()}
Title: {title}
Signature: {signature[:16]}...
────────────────────────────────────────────────────────────────────
"""
    _write_log(content)


def log_session_start():
    """Log the start of a new analysis session."""
    content = f"""

{'#' * 70}
#  JSMON AI ANALYSIS SESSION STARTED
#  {_get_timestamp()}
{'#' * 70}

"""
    _write_log(content)


def log_session_summary(
    total_files: int,
    trivia_skipped: int,
    ai_analyzed: int,
    changes_found: int,
    alerts_sent: int
):
    """Log session summary statistics."""
    content = f"""

{'#' * 70}
#  SESSION SUMMARY - {_get_timestamp()}
{'#' * 70}

📊 STATISTICS:
  • Total JS files with changes: {total_files}
  • Skipped by trivia filter: {trivia_skipped} ({100*trivia_skipped/max(total_files,1):.1f}%)
  • Analyzed by AI: {ai_analyzed}
  • Changes detected: {changes_found}
  • Alerts sent: {alerts_sent}

{'#' * 70}

"""
    _write_log(content)
