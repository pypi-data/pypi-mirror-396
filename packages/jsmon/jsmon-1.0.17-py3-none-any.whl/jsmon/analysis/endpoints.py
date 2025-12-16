import re

# Regex for finding endpoints
LINKFINDER_REGEX_STR = r"""
  (?:"|')                               # Start newline delimiter
  (
    ((?:/|\.\./|\./)                    # Start with /, ../, ./
    [^"'><,;| *()(%%$^/\\\[\]]          # Forbidden characters
    [^"'><,;|()]{1,})                   # End of URL
    |
    ([a-zA-Z0-9_\-/]{1,}/               # Or alphanumeric path
    [a-zA-Z0-9_\-/]{3,}                 # Length check
    \.[a-z]{2,4})                       # Extension
  )
  (?:"|')                               # End newline delimiter
"""

MODERN_JS_PATTERNS = [
    r"""(?:"|')(((?:/|\.\./|\./)[a-zA-Z0-9_\-/.?=&%]+)|([a-zA-Z0-9_\-/.?=&%]+\.(?:json|php|asp|aspx|jsp|html|xml)))""",
    r"""(?:url|href|src)\s*[:=]\s*(?:"|')([^"']+)""",
    r"""(?:axios|fetch|get|post|put|delete|patch)\s*\(\s*(?:"|')([^"']+)""",
    r"""(?:path|route)\s*:\s*(?:"|')([^"']+)""",
]

LINKFINDER_REGEX = re.compile(LINKFINDER_REGEX_STR, re.VERBOSE)
MODERN_REGEX_LIST = [re.compile(p) for p in MODERN_JS_PATTERNS]

SIMPLE_REGEX = re.compile(
    r"""
    (?:"|')                               # Start quote
    (
        (?:/|http[s]?://)                 # Start with / or http
        [a-zA-Z0-9_\-/.?=&%]+             # Valid chars
    )
    (?:"|')                               # End quote
    """, 
    re.VERBOSE
)

# Filtering constants
FP_EXACT_MATCHES = {
    'application/json', 'text/html', 'use strict', 'utf-8',
    'text/javascript', 'application/x-www-form-urlencoded',
    'multipart/form-data', 'image/png', 'image/jpeg', 'image/svg+xml',
    'no-cache', 'keep-alive', 'undefined', 'null', 'true', 'false',
    'GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD',
    'self', 'window', 'document', 'localStorage', 'sessionStorage',
    'console.log', 'console.error', 'console.warn', 'console.info',
    'module.exports', 'export default', 'import', 'from',
    'node_modules', 'package.json', 'webpack',
    'react', 'vue', 'angular', 'jquery',
}

FP_SUBSTRINGS = [
    '<div', '<span', '<a href', '<script', '<link', '<img', '<svg', '<path',
    'function(', '=>', 'return ', 'if (', 'for (', 'while (', 'switch (',
    'var ', 'let ', 'const ', 'class ', 'import ', 'export ',
    '//', '/*', '*/', '<!--', '-->',
    '0.0.0.0', '127.0.0.1', 'localhost',
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.css',
]

FP_ENDS_WITH = (
    '.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
    '.woff', '.woff2', '.ttf', '.eot', '.map', '.json',
)

FP_REGEX_PATTERNS = [
    re.compile(r'^[a-f0-9]{32,64}$', re.IGNORECASE),  # Hashes
    re.compile(r'^[0-9]+$'),  # Numbers
    re.compile(r'^[a-zA-Z0-9_]+\.[a-zA-Z0-9_]+$'),  # Properties
    re.compile(r'^/[a-z]{2}-[A-Z]{2}/?$'),  # Locale
    re.compile(r'^/[a-z]{2}/?$'),  # Locale
    re.compile(r'^v\d+(\.\d+)*$'),  # Version
    re.compile(r'^/?(assets|static|images|img|fonts|styles|css|js|vendors|node_modules)/'),
]

API_WHITELIST_PATTERNS = [
    re.compile(r'/api/'), re.compile(r'/v\d+/'), re.compile(r'/graphql'),
    re.compile(r'/auth/'), re.compile(r'/user/'), re.compile(r'/admin/'),
    re.compile(r'/login'), re.compile(r'/register'), re.compile(r'/account'),
    re.compile(r'/dashboard'), re.compile(r'/settings'), re.compile(r'/profile'),
    re.compile(r'/search'), re.compile(r'/query'), re.compile(r'/upload'),
    re.compile(r'/download'), re.compile(r'/payment'), re.compile(r'/billing'),
    re.compile(r'/order'), re.compile(r'/cart'), re.compile(r'/checkout'),
    re.compile(r'/notification'), re.compile(r'/message'), re.compile(r'/chat'),
    re.compile(r'\.php$'), re.compile(r'\.json$'), re.compile(r'\.xml$'),
]

DYNAMIC_PATTERNS = [
    (re.compile(r'/\d+'), '/{id}'),
    (re.compile(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '/{uuid}'),
    (re.compile(r'=\d+'), '={id}'),
    (re.compile(r'=[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'), '={uuid}'),
    (re.compile(r'\$\{.*?\}'), '{dynamic}'),
    (re.compile(r':\w+'), '{dynamic}'),
    (re.compile(r'\[.*?\]'), '{dynamic}'),
]

SANITIZER_REGEX_PATTERNS = [
    re.compile(r'[^\x20-\x7E]'),  # Non-printable
    re.compile(r'\\u[0-9a-fA-F]{4}'),  # Unicode escapes
    re.compile(r'\\x[0-9a-fA-F]{2}'),  # Hex escapes
    re.compile(r'\s+'),  # Whitespace
]

CSS_CONTEXT_SUBSTRINGS = [
    'display:', 'color:', 'background:', 'font-', 'margin:', 'padding:',
    'border:', 'width:', 'height:', 'z-index:', 'position:', 'top:', 'left:',
    '@media', '@import', '@font-face', '@keyframes'
]

def parser_file(content: str, args=None) -> list:
    """Extracts potential endpoints from content."""
    endpoints = set()
    
    # 1. LinkFinder Regex
    for match in LINKFINDER_REGEX.finditer(content):
        endpoints.add(match.group(1))
    
    # 2. Modern Patterns
    for pattern in MODERN_REGEX_LIST:
        for match in pattern.finditer(content):
            if match.groups():
                # We take the first non-empty group
                item = next((g for g in match.groups() if g), None)
                if item: endpoints.add(item)
    
    # 3. Simple Regex (fallback)
    for match in SIMPLE_REGEX.finditer(content):
        endpoints.add(match.group(1))
    
    # === NEW: 4. GraphQL Operations ===
    from jsmon.analysis.smart_filters import extract_graphql_operations, should_analyze_graphql_operation
    
    graphql_ops = extract_graphql_operations(content)
    for op_type, op_name, op_body in graphql_ops:
        should_analyze, reason = should_analyze_graphql_operation(op_body, op_name)
        if should_analyze:
            # Format as endpoint-like string for tracking
            gql_endpoint = f"/graphql:{op_type}:{op_name}"
            endpoints.add(gql_endpoint)
        
    return list(endpoints)

def filter_false_positives(endpoints: list, args=None) -> list:
    """Filters out obvious garbage."""
    filtered = []
    for ep in endpoints:
        ep = ep.strip()
        if not ep or len(ep) < 3 or len(ep) > 200: continue
        
        # Exact matches
        if ep in FP_EXACT_MATCHES: continue
        
        # Substrings
        if any(s in ep for s in FP_SUBSTRINGS): continue
        
        # Ends with
        if ep.lower().endswith(FP_ENDS_WITH): continue
        
        # Regex patterns
        if any(p.search(ep) for p in FP_REGEX_PATTERNS): continue
        
        # CSS check
        if any(s in ep for s in CSS_CONTEXT_SUBSTRINGS): continue
        
        filtered.append(ep)
    return filtered

def filter_whitelist_endpoints(endpoints: list, args=None) -> list:
    """Leaves only interesting endpoints."""
    # If whitelist is disabled (not implemented yet), return all
    # For now, we assume we want to filter
    
    filtered = []
    for ep in endpoints:
        if any(p.search(ep) for p in API_WHITELIST_PATTERNS):
            filtered.append(ep)
    return filtered

def ultimate_pre_filter_and_sanitize(endpoints: list, args=None) -> list:
    """Advanced cleaning and normalization."""
    sanitized = set()
    
    for ep in endpoints:
        # Remove quotes
        ep = ep.strip("'\"`")
        
        # Remove leading/trailing slashes if it's not root
        if ep != '/':
            ep = ep.rstrip('/')
        
        # Normalize dynamic parts
        for pattern, replacement in DYNAMIC_PATTERNS:
            ep = pattern.sub(replacement, ep)
            
        # Remove non-printable chars
        for pattern in SANITIZER_REGEX_PATTERNS:
            ep = pattern.sub('', ep)
            
        # Heuristics
        if not ep: continue
        
        # Ratio of digits
        digit_count = sum(c.isdigit() for c in ep)
        if len(ep) > 10 and digit_count / len(ep) > 0.5: continue
        
        # Ratio of capital letters (excluding UUIDs)
        upper_count = sum(c.isupper() for c in ep)
        if len(ep) > 10 and upper_count / len(ep) > 0.5: continue
        
        sanitized.add(ep)
        
    return list(sanitized)
