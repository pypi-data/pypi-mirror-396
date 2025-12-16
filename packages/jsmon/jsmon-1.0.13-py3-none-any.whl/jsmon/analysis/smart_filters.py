"""
Smart Filters for Advanced JS Discovery

Reduces false positives when analyzing:
- Lazy-loaded JavaScript chunks
- Service Workers
- GraphQL operations
"""

import re
from typing import Tuple

def should_analyze_lazy_chunk(chunk_path: str, js_content: str) -> Tuple[bool, str]:
    """
    Smart filter for lazy-loaded chunks.
    
    Args:
        chunk_path: URL/path to the chunk file
        js_content: Content of the chunk
        
    Returns:
        (should_analyze: bool, reason: str)
    """
    
    # 1. Skip vendor/node_modules
    vendor_patterns = ['vendor', 'node_modules', 'npm', 'dependencies']
    if any(x in chunk_path.lower() for x in vendor_patterns):
        return False, "vendor_bundle"
    
    # 2. Skip localization
    locale_patterns = ['i18n', 'locale', 'lang', 'translation', 'intl']
    if any(x in chunk_path.lower() for x in locale_patterns):
        return False, "localization"
    
    # 3. Skip polyfills
    polyfill_patterns = ['polyfill', 'legacy', 'compat', 'shim', 'es5']
    if any(x in chunk_path.lower() for x in polyfill_patterns):
        return False, "polyfill"
    
    # 4. Skip webpack runtime chunks
    if 'runtime' in chunk_path.lower() or 'manifest' in chunk_path.lower():
        if 'webpackJsonp' in js_content or '__webpack_require__' in js_content:
            if len(js_content) < 10000:  # Small runtime chunks
                return False, "webpack_runtime"
    
    # 5. Skip if содержит только import statements (no logic)
    lines = js_content.split('\n')
    import_count = sum(1 for line in lines if line.strip().startswith(('import ', 'export ')))
    if len(lines) > 0 and import_count / len(lines) > 0.5:  # >50% imports
        return False, "import_only"
    
    # 6. Check for actual endpoints/API calls
    api_patterns = [
        r'fetch\s*\(',
        r'axios\.',
        r'\.post\s*\(',
        r'\.get\s*\(',
        r'/api/',
        r'/v\d+/',
        r'graphql'
    ]
    has_api_calls = any(re.search(pattern, js_content, re.IGNORECASE) for pattern in api_patterns)
    
    if not has_api_calls:
        return False, "no_api_calls"
    
    # 7. Size check - слишком маленькие chunk'и (likely webpack overhead)
    if len(js_content) < 500:
        return False, "too_small"
    
    # 8. Check for meaningful code (not just minified gibberish)
    # Count meaningful identifiers
    meaningful_words = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]{3,}\b', js_content)
    if len(meaningful_words) < 10:
        return False, "no_meaningful_code"
    
    return True, "legitimate_chunk"

def should_analyze_service_worker(sw_url: str, sw_content: str) -> Tuple[bool, str]:
    """
    Smart filter for service workers.
    
    Args:
        sw_url: URL to the service worker
        sw_content: Content of the service worker
        
    Returns:
        (should_analyze: bool, reason: str)
    """
    
    # 1. Skip Google Workbox
    workbox_indicators = ['workbox', 'workbox-sw', 'workbox-core']
    if any(x in sw_content.lower() for x in workbox_indicators):
        return False, "google_workbox"
    
    # 2. Skip if mostly importScripts from CDN
    cdn_imports = re.findall(r"importScripts\s*\(\s*['\"]https?://", sw_content)
    if len(cdn_imports) > 3:
        return False, "cdn_heavy"
    
    # 3. Skip Firebase SW
    firebase_indicators = ['firebase', 'gstatic.com', 'firebasejs']
    if any(x in sw_content.lower() for x in firebase_indicators):
        return False, "firebase_messaging"
    
    # 4. Skip very small SW (likely template)
    if len(sw_content) < 300:
        return False, "too_small"
    
    # 5. Check for custom API logic
    has_custom_fetch = bool(re.search(r"fetch\s*\(\s*['\"]/(api|v\d)", sw_content))
    has_message_handling = 'addEventListener' in sw_content and 'message' in sw_content
    has_sync = 'sync' in sw_content.lower() and 'background' in sw_content.lower()
    
    # If it has custom fetch handlers or message handling, it's interesting
    if has_custom_fetch or has_message_handling or has_sync:
        return True, "custom_logic"
    
    # 6. Check if it's just a basic cache-first template
    template_keywords = ['addEventListener', 'install', 'activate', 'fetch']
    keyword_count = sum(1 for kw in template_keywords if kw in sw_content)
    
    # If has all template keywords but no custom logic and small size
    if keyword_count == len(template_keywords) and len(sw_content) < 2000:
        return False, "template_sw"
    
    return True, "custom_sw"

def should_analyze_graphql_operation(operation: str, operation_name: str = "") -> Tuple[bool, str]:
    """
    Smart filter for GraphQL operations.
    
    Args:
        operation: GraphQL operation string (query/mutation/subscription)
        operation_name: Name of the operation (if available)
        
    Returns:
        (should_analyze: bool, reason: str)
    """
    
    # 1. Skip introspection queries
    introspection_keywords = ['IntrospectionQuery', '__schema', '__type', '__typename']
    if any(x in operation_name for x in introspection_keywords) or any(x in operation for x in introspection_keywords):
        return False, "introspection"
    
    # 2. Skip playground examples
    skip_names = ['example', 'test', 'playground', 'sample', 'demo', 'mock']
    if any(x in operation_name.lower() for x in skip_names):
        return False, "example_query"
    
    # 3. Skip auto-generated fragments (no new endpoints)
    if 'FragmentDoc' in operation_name or 'fragment ' in operation.lower().split('\n')[0]:
        # First line is fragment definition
        return False, "fragment_definition"
    
    # 4. Look for meaningful operations
    has_mutation = 'mutation ' in operation.lower()
    has_subscription = 'subscription ' in operation.lower()
    
    # Admin/sensitive keywords
    admin_keywords = ['admin', 'delete', 'remove', 'update', 'create', 'edit', 'manage', 'internal', 'beta']
    has_admin_keyword = any(x in operation.lower() for x in admin_keywords)
    
    if has_mutation or has_subscription or has_admin_keyword:
        return True, "interesting_operation"
    
    # 5. Skip very simple getters (likely just reading public data)
    brace_count = operation.count('{')
    if brace_count < 3:  # Too shallow (e.g., query { user { id } })
        return False, "simple_query"
    
    # 6. Check for meaningful field names
    # Extract field names from operation
    field_pattern = r'\b(\w+)\s*(?:\(|{)'
    fields = re.findall(field_pattern, operation)
    meaningful_fields = [f for f in fields if len(f) > 3 and f not in ['query', 'mutation', 'subscription']]
    
    if len(meaningful_fields) < 2:
        return False, "too_simple"
    
    return True, "potential_feature"

def extract_dynamic_imports(js_content: str) -> list:
    """
    Extract dynamic import() calls from JavaScript.
    
    Args:
        js_content: JavaScript source code
        
    Returns:
        List of dynamically imported modules
    """
    imports = []
    
    # Pattern 1: import('path')
    pattern1 = r"import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    imports.extend(re.findall(pattern1, js_content))
    
    # Pattern 2: import(`template-${var}`)
    pattern2 = r"import\s*\(\s*`([^`]+)`\s*\)"
    imports.extend(re.findall(pattern2, js_content))
    
    # Pattern 3: require.ensure (webpack legacy)
    pattern3 = r"require\.ensure\s*\(\s*\[[^\]]*['\"]([^'\"]+)['\"]"
    imports.extend(re.findall(pattern3, js_content))
    
    # Pattern 4: System.import (older spec)
    pattern4 = r"System\.import\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    imports.extend(re.findall(pattern4, js_content))
    
    return list(set(imports))  # Deduplicate

def extract_web_workers(js_content: str) -> list:
    """
    Extract Web Worker script URLs from JavaScript.
    
    Args:
        js_content: JavaScript source code
        
    Returns:
        List of worker script URLs
    """
    workers = []
    
    # Pattern: new Worker('path')
    pattern = r"new\s+Worker\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    workers.extend(re.findall(pattern, js_content))
    
    # Pattern: new SharedWorker('path')
    pattern2 = r"new\s+SharedWorker\s*\(\s*['\"]([^'\"]+)['\"]\s*\)"
    workers.extend(re.findall(pattern2, js_content))
    
    return list(set(workers))

def extract_graphql_operations(js_content: str) -> list:
    """
    Extract GraphQL operations from JavaScript.
    
    Args:
        js_content: JavaScript source code
        
    Returns:
        List of (operation_type, operation_name, operation_body) tuples
    """
    operations = []
    
    # Pattern 1: gql`query Name { ... }`
    gql_pattern = r"gql\s*`\s*(query|mutation|subscription)\s+(\w+)[^`]*`"
    matches = re.finditer(gql_pattern, js_content, re.IGNORECASE | re.DOTALL)
    for match in matches:
        op_type = match.group(1)
        op_name = match.group(2)
        op_body = match.group(0)
        operations.append((op_type, op_name, op_body))
    
    # Pattern 2: graphql(gql`...`)
    graphql_pattern = r"graphql\s*\(\s*gql\s*`\s*(query|mutation|subscription)\s+(\w+)[^`]*`"
    matches = re.finditer(graphql_pattern, js_content, re.IGNORECASE | re.DOTALL)
    for match in matches:
        op_type = match.group(1)
        op_name = match.group(2)
        operations.append((op_type, op_name, match.group(0)))
    
    # Pattern 3: Direct string queries
    string_pattern = r"['\"]\\s*(query|mutation|subscription)\\s+(\\w+)"
    matches = re.finditer(string_pattern, js_content, re.IGNORECASE)
    for match in matches:
        operations.append((match.group(1), match.group(2), ""))
    
    return operations
