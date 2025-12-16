"""
Trivia Filter - Eliminates noise from JavaScript diff analysis.

This module filters out trivial changes that don't represent new attack surface:
- Variable/function renames
- Code formatting changes
- Comment updates
- Webpack hash/chunk ID changes
- Library version bumps
- Session/CSRF token changes
- Asset URL changes
"""

import re
from typing import Tuple, List
from difflib import SequenceMatcher

# Patterns for detecting trivial changes
# Webpack hash: standalone hex string in quotes, typically 8+ chars
WEBPACK_HASH_PATTERN = re.compile(r'["\'][a-f0-9]{8,}["\']')
# Webpack chunk: chunk-xxx or standalone alphanumeric ID
WEBPACK_CHUNK_PATTERN = re.compile(r'["\'](chunk-)[a-zA-Z0-9]+["\']')
VERSION_PATTERN = re.compile(r'\d+\.\d+\.\d+')
COMMENT_PATTERN = re.compile(r'(//.*?$|/\*.*?\*/)', re.MULTILINE | re.DOTALL)

# Token/session patterns (noise)
TOKEN_PATTERNS = [
    re.compile(r'(csrf|token|session|request)[-_]?id?\s*[:=]\s*["\'][^"\']+["\']', re.I),
    re.compile(r'["\']sess_[a-zA-Z0-9]+["\']'),
    re.compile(r'["\']csrf_[a-zA-Z0-9]+["\']'),
    re.compile(r'["\']req_[a-zA-Z0-9]+["\']'),
]

# Webpack module ID pattern - must be quoted ID followed by :function
WEBPACK_MODULE_PATTERN = re.compile(r'["\'][a-zA-Z0-9]{10,}["\']\s*:\s*function')

# Patterns that indicate REAL code (not webpack noise)
REAL_CODE_PATTERNS = [
    re.compile(r'\.prototype\.'),  # Method definitions
    re.compile(r'function\s+\w+\s*\('),  # Named functions
    re.compile(r'return\s+\{'),  # Return objects
    re.compile(r'if\s*\([^)]+\)\s*\{'),  # If statements
    re.compile(r'\.(then|catch|finally)\s*\('),  # Promises
    re.compile(r'new\s+(Promise|Error|Date|Array|Object)'),  # Constructors
    re.compile(r'(const|let|var)\s+\w+\s*='),  # Variable declarations
]


def is_webpack_hash_change(diff: str) -> bool:
    """Detects if diff is primarily webpack hash/chunk ID changes."""
    lines = diff.split('\n')
    hash_changes = 0
    real_code_lines = 0
    total_changes = 0
    
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            if line.startswith('+++') or line.startswith('---'):
                continue
            total_changes += 1
            
            # Check if line contains real code patterns
            if any(p.search(line) for p in REAL_CODE_PATTERNS):
                real_code_lines += 1
                continue
            
            # Check for webpack patterns
            if (WEBPACK_HASH_PATTERN.search(line) or 
                WEBPACK_CHUNK_PATTERN.search(line) or
                WEBPACK_MODULE_PATTERN.search(line)):
                hash_changes += 1
    
    if total_changes == 0:
        return False
    
    # If there's significant real code, don't treat as webpack hash change
    if real_code_lines > total_changes * 0.3:
        return False
    
    return (hash_changes / total_changes) > 0.7


def is_token_change(diff: str) -> bool:
    """Detects if diff is primarily session/CSRF token changes."""
    lines = diff.split('\n')
    token_changes = 0
    total_changes = 0
    
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            if line.startswith('+++') or line.startswith('---'):
                continue
            total_changes += 1
            
            for pattern in TOKEN_PATTERNS:
                if pattern.search(line):
                    token_changes += 1
                    break
    
    if total_changes == 0:
        return False
    
    return (token_changes / total_changes) > 0.7


def is_comment_only_change(diff: str) -> bool:
    """Detects if diff only contains comment changes."""
    lines = diff.split('\n')
    comment_lines = 0
    total_changes = 0
    
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            if line.startswith('+++') or line.startswith('---'):
                continue
            total_changes += 1
            content = line[1:].strip()
            if (content.startswith('//') or 
                content.startswith('/*') or 
                content.startswith('*') or
                content.endswith('*/') or
                content.startswith('#')):
                comment_lines += 1
    
    if total_changes == 0:
        return False
    
    return (comment_lines / total_changes) > 0.9


def is_formatting_change(diff: str) -> bool:
    """Detects if diff is primarily formatting (whitespace/semicolons)."""
    lines = diff.split('\n')
    
    added = []
    removed = []
    
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            added.append(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            removed.append(line[1:])
    
    if len(added) != len(removed) or len(added) == 0:
        return False
    
    # Compare without whitespace and semicolons
    formatting_only = 0
    for a, r in zip(added, removed):
        a_normalized = re.sub(r'[\s;,]+', '', a)
        r_normalized = re.sub(r'[\s;,]+', '', r)
        if a_normalized == r_normalized:
            formatting_only += 1
    
    return (formatting_only / len(added)) > 0.9


def is_version_bump(diff: str) -> bool:
    """Detects library version updates and build timestamps."""
    lines = diff.split('\n')
    version_changes = 0
    total_changes = 0
    
    # Patterns for version/build metadata (must be assignments, not code)
    version_patterns = [
        re.compile(r'(VERSION|BUILD|TIMESTAMP)\s*[:=]', re.I),
        re.compile(r'["\'](version|build|timestamp)["\']\s*[:=]', re.I),
        re.compile(r'_TIME\s*[:=]'),
        re.compile(r'_ID\s*[:=]'),
    ]
    
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            if line.startswith('+++') or line.startswith('---'):
                continue
            total_changes += 1
            
            # Check for version pattern (1.0.0) with assignment
            has_version = VERSION_PATTERN.search(line) is not None and '=' in line
            # Check for version-related assignment patterns
            has_version_assign = any(p.search(line) for p in version_patterns)
            # Check for ISO timestamp in string
            has_timestamp = bool(re.search(r'["\'].*\d{4}-\d{2}-\d{2}.*["\']', line))
            
            if has_version or has_version_assign or has_timestamp:
                version_changes += 1
    
    if total_changes == 0:
        return False
    
    return (version_changes / total_changes) > 0.5


def is_rename_only(diff: str) -> bool:
    """Detects if diff is primarily variable/function renames."""
    lines = diff.split('\n')
    
    added = []
    removed = []
    
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            added.append(line[1:].strip())
        elif line.startswith('-') and not line.startswith('---'):
            removed.append(line[1:].strip())
    
    if not added or not removed or len(added) != len(removed):
        return False
    
    # Check each pair for structural similarity
    rename_pairs = 0
    for a, r in zip(added, removed):
        # Remove identifiers and compare structure
        a_struct = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'ID', a)
        r_struct = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', 'ID', r)
        
        if a_struct == r_struct:
            rename_pairs += 1
    
    return (rename_pairs / len(added)) > 0.8


def is_string_only_change(diff: str) -> bool:
    """
    Detects if diff only changes string literals (error messages, labels, etc).
    Structure stays the same, only quoted text changes.
    """
    lines = diff.split('\n')
    
    added = []
    removed = []
    
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            added.append(line[1:])
        elif line.startswith('-') and not line.startswith('---'):
            removed.append(line[1:])
    
    if len(added) != len(removed) or len(added) == 0:
        return False
    
    # Compare structure without string contents
    string_pattern = re.compile(r'(["\'])(?:(?!\1)[^\\]|\\.)*\1')
    
    string_only_changes = 0
    for a, r in zip(added, removed):
        # Replace all strings with placeholder
        a_struct = string_pattern.sub('"STR"', a)
        r_struct = string_pattern.sub('"STR"', r)
        
        if a_struct == r_struct:
            string_only_changes += 1
    
    return (string_only_changes / len(added)) > 0.8


def is_error_message_change(diff: str) -> bool:
    """
    Detects if diff is primarily error/status message text changes.
    Common patterns: errorMessages, errors, messages, labels objects.
    Only triggers if the changes are JUST message text, not new logic.
    """
    lines = diff.split('\n')
    
    # Patterns indicating error/message objects (must be in object context)
    message_patterns = [
        re.compile(r'(errorMessages?|messages?|labels?)\s*[=:{]', re.I),
        re.compile(r'["\'](AUTH_FAIL|NET_ERR|SERVER_ERROR|INVALID_|RATE_LIMIT|ACCOUNT_)["\']', re.I),
    ]
    
    # Patterns that indicate real code changes (not just messages)
    code_patterns = [
        re.compile(r'\.prototype\.'),
        re.compile(r'function\s*\('),
        re.compile(r'return\s*\{'),
        re.compile(r'if\s*\('),
        re.compile(r'\.then\s*\('),
        re.compile(r'new\s+\w+'),
    ]
    
    message_lines = 0
    code_lines = 0
    total_changes = 0
    
    for line in lines:
        if line.startswith('+') or line.startswith('-'):
            if line.startswith('+++') or line.startswith('---'):
                continue
            total_changes += 1
            
            # Check for real code
            if any(p.search(line) for p in code_patterns):
                code_lines += 1
                continue
            
            # Check if line is in a message/error object
            if any(p.search(line) for p in message_patterns):
                message_lines += 1
    
    if total_changes == 0:
        return False
    
    # If there's significant code, don't treat as message-only change
    if code_lines > total_changes * 0.2:
        return False
    
    # Must be primarily message changes with string-only structure
    if is_string_only_change(diff) and (message_lines / total_changes) > 0.6:
        return True
    
    return (message_lines / total_changes) > 0.8


def extract_new_strings(diff: str) -> List[str]:
    """Extracts new string literals from diff (potential endpoints/features)."""
    lines = diff.split('\n')
    new_strings = []
    
    string_pattern = re.compile(r'''["']([^"']{4,}?)["']''')
    
    # Noise patterns to exclude
    noise_patterns = [
        re.compile(r'^[a-f0-9]{8,}$'),  # Hashes
        re.compile(r'^chunk-'),  # Webpack chunks
        re.compile(r'^(sess|csrf|req|token)_'),  # Tokens
        re.compile(r'^\d+\.\d+\.\d+$'),  # Versions
        re.compile(r'^https?://cdn\.'),  # CDN URLs
        re.compile(r'\.(png|jpg|svg|css|woff)'),  # Assets
    ]
    
    for line in lines:
        if line.startswith('+') and not line.startswith('+++'):
            matches = string_pattern.findall(line)
            for match in matches:
                # Skip noise
                is_noise = any(p.search(match) for p in noise_patterns)
                if is_noise:
                    continue
                
                # Keep API-like strings
                if ('/' in match and 'api' in match.lower()) or '?' in match:
                    new_strings.append(match)
    
    return new_strings


def calculate_trivia_score(diff: str) -> float:
    """
    Comprehensive trivia score calculation.
    Returns 0.0-1.0, where 1.0 = completely trivial.
    """
    if not diff or len(diff) < 10:
        return 1.0
    
    scores = []
    
    # Check individual trivia types
    if is_webpack_hash_change(diff):
        scores.append(1.0)
    
    if is_token_change(diff):
        scores.append(1.0)
    
    if is_comment_only_change(diff):
        scores.append(1.0)
    
    if is_formatting_change(diff):
        scores.append(1.0)
    
    if is_version_bump(diff):
        scores.append(0.95)
    
    if is_rename_only(diff):
        scores.append(0.9)
    
    if is_error_message_change(diff):
        scores.append(0.95)
    
    if is_string_only_change(diff):
        scores.append(0.85)
    
    # Check if there are new API strings (reduces trivia score)
    new_strings = extract_new_strings(diff)
    if new_strings:
        scores.append(max(0.0, 0.3 - len(new_strings) * 0.1))
    
    if not scores:
        return 0.0
    
    return max(scores)


def has_api_indicators(diff: str) -> bool:
    """Check if diff contains API-related patterns that should always be analyzed."""
    # Patterns that indicate important changes
    api_patterns = [
        re.compile(r'fetch\s*\(\s*["\'][^"\']*["\']'),  # Any fetch call
        re.compile(r'/api/[a-zA-Z0-9/_-]+'),  # API paths
        re.compile(r'\b(admin|debug|internal|bypass)\b', re.I),  # Security keywords
        re.compile(r'(adminPass|adminUser|debugPass|secretKey)\s*[:=]', re.I),  # Hardcoded creds
    ]
    
    # Patterns to exclude (noise that looks like API indicators)
    exclude_patterns = [
        re.compile(r'CSRF_TOKEN\s*='),  # CSRF token assignment
        re.compile(r'SESSION_ID\s*='),  # Session ID assignment
        re.compile(r'\{key\s*:'),  # React key prop
    ]
    
    for line in diff.split('\n'):
        if line.startswith('+') and not line.startswith('+++'):
            # Skip if matches exclude pattern
            if any(p.search(line) for p in exclude_patterns):
                continue
            # Check for API indicators
            for pattern in api_patterns:
                if pattern.search(line):
                    return True
    return False


async def should_analyze_with_ai(diff: str, js_url: str, debug: bool = False) -> Tuple[bool, str]:
    """
    Determines if a diff should be sent to AI for analysis.
    
    Returns:
        (should_analyze: bool, reason: str)
    """
    # Collect all check results for logging
    checks = {}
    
    # FIRST: Check for API indicators - these always get analyzed
    api_indicators = has_api_indicators(diff)
    if api_indicators:
        if debug:
            print(f"[TRIVIA] {js_url}: has API indicators, will analyze")
            # Log to file
            try:
                from jsmon.analysis.debug_logger import log_trivia_analysis
                log_trivia_analysis(
                    js_url=js_url,
                    diff_size=len(diff),
                    checks={"has_api_indicators": True},
                    trivia_score=0.0,
                    has_api_indicators=True,
                    decision=True,
                    reason="has_api_indicators",
                    diff_content=diff
                )
            except ImportError:
                pass
        return True, "has_api_indicators"
    
    # Fast checks for trivial changes
    checks["webpack_hash"] = is_webpack_hash_change(diff)
    if checks["webpack_hash"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 1.0, False, False, "webpack_hash")
        return False, "webpack_hash"
    
    checks["token_change"] = is_token_change(diff)
    if checks["token_change"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 1.0, False, False, "token_change")
        return False, "token_change"
    
    checks["comments_only"] = is_comment_only_change(diff)
    if checks["comments_only"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 1.0, False, False, "comments_only")
        return False, "comments_only"
    
    checks["formatting_only"] = is_formatting_change(diff)
    if checks["formatting_only"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 1.0, False, False, "formatting_only")
        return False, "formatting_only"
    
    checks["version_bump"] = is_version_bump(diff)
    if checks["version_bump"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 0.95, False, False, "version_bump")
        return False, "version_bump"
    
    checks["rename_only"] = is_rename_only(diff)
    if checks["rename_only"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 0.9, False, False, "rename_only")
        return False, "rename_only"
    
    checks["error_messages"] = is_error_message_change(diff)
    if checks["error_messages"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 0.95, False, False, "error_messages")
        return False, "error_messages"
    
    checks["string_only"] = is_string_only_change(diff)
    if checks["string_only"]:
        if debug:
            _log_trivia_decision(js_url, diff, checks, 0.85, False, False, "string_only")
        return False, "string_only"
    
    # Comprehensive trivia check
    trivia_score = calculate_trivia_score(diff)
    
    if debug:
        print(f"[TRIVIA] {js_url}: score={trivia_score:.2f}")
    
    # Threshold: 0.75 = likely trivial
    if trivia_score > 0.75:
        if debug:
            _log_trivia_decision(js_url, diff, checks, trivia_score, False, False, f"trivial_score_{trivia_score:.2f}")
        return False, f"trivial_score_{trivia_score:.2f}"
    
    # Extract meaningful indicators
    new_strings = extract_new_strings(diff)
    if new_strings and debug:
        print(f"[TRIVIA] Found {len(new_strings)} potential new strings/endpoints")
    
    # Log successful pass-through
    if debug:
        _log_trivia_decision(js_url, diff, checks, trivia_score, False, True, "significant_change")
    
    return True, "significant_change"


def _log_trivia_decision(js_url: str, diff: str, checks: dict, score: float, 
                         has_api: bool, decision: bool, reason: str):
    """Helper to log trivia filter decision."""
    try:
        from jsmon.analysis.debug_logger import log_trivia_analysis
        log_trivia_analysis(
            js_url=js_url,
            diff_size=len(diff),
            checks=checks,
            trivia_score=score,
            has_api_indicators=has_api,
            decision=decision,
            reason=reason,
            diff_content=diff
        )
    except ImportError:
        pass
