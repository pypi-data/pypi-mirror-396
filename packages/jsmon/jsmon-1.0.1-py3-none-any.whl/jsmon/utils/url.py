import re
from urllib.parse import urlparse, urljoin
from jsmon.config.constants import SCRIPT_BLOCKLIST_DOMAINS, KNOWN_FIRST_PARTY_CDN, JS_FILENAME_BLACKLIST_REGEX

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

def is_third_party_js(js_url: str, source_host: str, debug: bool = False) -> tuple:
    """
    Determines whether the JS file is third party.
    Returns: (is_third_party: bool, reason: str)
    """
    parsed = urlparse(js_url)
    js_domain = parsed.netloc.lower()
    js_path = parsed.path.lower()
    
    if is_blocked_domain(js_url, SCRIPT_BLOCKLIST_DOMAINS):
        return True, f"Blocked domain: {js_domain}"
    
    target_base_domain = '.'.join(source_host.split('.')[-2:])
    is_same_domain = (
        js_domain == source_host or 
        js_domain.endswith(f'.{target_base_domain}')
    )
    
    if not is_same_domain:
        for cdn_domain, owner_domains in KNOWN_FIRST_PARTY_CDN.items():
            if cdn_domain in js_domain:
                if any(owner in source_host for owner in owner_domains):
                    if debug:
                        print(f"[ALLOWED CDN] {js_domain} belongs to {source_host}")
                    return False, f"Known first-party CDN: {cdn_domain}"
        return True, f"Foreign domain: {js_domain}"
    
    if JS_FILENAME_BLACKLIST_REGEX.search(js_path):
        matched_pattern = JS_FILENAME_BLACKLIST_REGEX.search(js_path).group()
        return True, f"Third-party pattern: '{matched_pattern}'"
    
    return False, "Passed all checks"
