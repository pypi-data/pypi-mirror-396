import re
from urllib.parse import urlparse, urljoin
from jsmon.config.constants import SCRIPT_BLOCKLIST_DOMAINS, KNOWN_FIRST_PARTY_CDN, JS_FILENAME_BLACKLIST_REGEX

# Generic CDN domains where companies host their own JS
GENERIC_CDN_DOMAINS = {
    'cloudfront.net', 'amazonaws.com', 'akamaihd.net', 'akamai.net',
    'fastly.net', 'fastlylb.net', 'edgecastcdn.net', 'azureedge.net',
    'cloudflare.com', 'cdn77.org', 'stackpathdns.com', 'imgix.net',
    'muscache.com',  # Airbnb CDN
}

# Known third-party library patterns (always skip)
THIRD_PARTY_LIB_PATTERNS = [
    r'/npm/', r'/vendor/', r'/lib/', r'/node_modules/',
    r'react[\.-]', r'vue[\.-]', r'angular[\.-]', r'jquery[\.-]',
    r'lodash[\.-]', r'moment[\.-]', r'axios[\.-]', r'bootstrap[\.-]',
    r'popper[\.-]', r'chart[\.-]js', r'd3[\.-]', r'three[\.-]',
]

def get_canonical_url(url: str) -> str:
    """
    Advanced URL normalization:
    - Removes content hashes of any length (6-64 characters)
    - Removes query parameters
    - Preserves the structure of inline scripts
    """
    try:
        parsed_url = urlparse(url)
        
        if parsed_url.fragment.startswith('inline-script-'):
            return url
        
        path = parsed_url.path
        clean_path = path.split('?')[0].split('#')[0]
        
        # Matches hashes from 6 to 64 characters
        path_without_hash = re.sub(
            r'[\.-]([a-f0-9]{6,64}|[A-Z0-9]{6,64})(?=\.|$)',
            '',
            clean_path,
            flags=re.IGNORECASE
        )
        
        canonical_url = parsed_url._replace(
            path=path_without_hash,
            query='',
            fragment=''
        ).geturl()
        
        return canonical_url
    except Exception:
        return url

def is_blocked_domain(url: str, blocklist: set) -> bool:
    """Checks the URL against the block list, taking into account subdomains."""
    try:
        hostname = urlparse(url).netloc.lower()
        parts = hostname.split('.')
        for i in range(len(parts)):
            parent_domain = '.'.join(parts[i:])
            if parent_domain in blocklist:
                return True
        return False
    except Exception:
        return False

def _extract_company_name(host: str) -> str:
    """Extract main company name from host (e.g., 'www.uber.com' -> 'uber')."""
    parts = host.lower().split('.')
    # Remove common prefixes/suffixes
    skip = {'www', 'app', 'api', 'cdn', 'static', 'assets', 'web', 'm', 'mobile'}
    for part in parts:
        if part not in skip and len(part) > 2:
            return part
    return parts[0] if parts else ''

def _is_generic_library(js_path: str) -> bool:
    """Check if JS path looks like a generic third-party library."""
    path_lower = js_path.lower()
    for pattern in THIRD_PARTY_LIB_PATTERNS:
        if re.search(pattern, path_lower):
            return True
    return False

def _is_likely_first_party_cdn(js_url: str, js_domain: str, js_path: str, source_host: str, debug: bool = False) -> tuple:
    """
    Smart heuristic: Check if JS on generic CDN likely belongs to source company.
    Returns: (is_first_party: bool, reason: str or None)
    """
    # Check if it's a generic CDN
    is_generic_cdn = any(cdn in js_domain for cdn in GENERIC_CDN_DOMAINS)
    if not is_generic_cdn:
        return False, None
    
    # Skip if it's clearly a third-party library
    if _is_generic_library(js_path):
        return False, None
    
    # Extract company name from source host
    company_name = _extract_company_name(source_host)
    if len(company_name) < 3:
        return False, None
    
    # Check if company name appears in JS URL (domain or path)
    full_url_lower = js_url.lower()
    if company_name in full_url_lower:
        if debug:
            print(f"[SMART CDN] '{company_name}' found in {js_url}")
        return True, f"Company name '{company_name}' in CDN URL"
    
    # Check for common patterns: /companyname/, companyname-bundle, companyname.js
    company_patterns = [
        f'/{company_name}/',
        f'/{company_name}-',
        f'/{company_name}_',
        f'{company_name}.js',
        f'{company_name}.min.js',
        f'{company_name}-bundle',
        f'{company_name}_bundle',
    ]
    for pattern in company_patterns:
        if pattern in full_url_lower:
            if debug:
                print(f"[SMART CDN] Pattern '{pattern}' matched in {js_url}")
            return True, f"Company pattern '{pattern}' in CDN URL"
    
    return False, None

def is_third_party_js(js_url: str, source_host: str, debug: bool = False) -> tuple:
    """
    Determines whether the JS file is third party.
    Returns: (is_third_party: bool, reason: str)
    
    Logic:
    1. Check blocklist domains (Google, Facebook, etc.) → block
    2. Check if same domain or subdomain → allow
    3. Check known first-party CDN mappings → allow
    4. Smart heuristic: company name in CDN URL → allow
    5. Otherwise → block as foreign
    """
    parsed = urlparse(js_url)
    js_domain = parsed.netloc.lower()
    js_path = parsed.path.lower()
    
    # 1. Blocklist check
    if is_blocked_domain(js_url, SCRIPT_BLOCKLIST_DOMAINS):
        return True, f"Blocked domain: {js_domain}"
    
    # 2. Same domain check
    target_base_domain = '.'.join(source_host.split('.')[-2:])
    is_same_domain = (
        js_domain == source_host or 
        js_domain.endswith(f'.{target_base_domain}')
    )
    
    if is_same_domain:
        # Check filename blacklist even for same domain
        if JS_FILENAME_BLACKLIST_REGEX.search(js_path):
            matched_pattern = JS_FILENAME_BLACKLIST_REGEX.search(js_path).group()
            return True, f"Third-party pattern: '{matched_pattern}'"
        return False, "Same domain"
    
    # 3. Known first-party CDN check
    for cdn_domain, owner_domains in KNOWN_FIRST_PARTY_CDN.items():
        if cdn_domain in js_domain:
            if any(owner in source_host for owner in owner_domains):
                if debug:
                    print(f"[ALLOWED CDN] {js_domain} belongs to {source_host}")
                return False, f"Known first-party CDN: {cdn_domain}"
    
    # 4. Smart heuristic: company name in CDN URL
    is_first_party, reason = _is_likely_first_party_cdn(js_url, js_domain, js_path, source_host, debug)
    if is_first_party:
        return False, reason
    
    # 5. Foreign domain
    return True, f"Foreign domain: {js_domain}"
