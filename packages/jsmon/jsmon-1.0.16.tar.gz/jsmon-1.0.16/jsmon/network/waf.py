import re

class WAFDetector:
    """Defines WAF lock types"""
    
    WAF_SIGNATURES = {
        'cloudflare_challenge': [
            r'checking your browser',
            r'cloudflare',
            r'cf-ray',
            r'__cf_bm',
            r'challenge-platform'
        ],
        'akamai_block': [
            r'reference #\d+\.\w+\.\d+',
            r'akamai',
            r'access denied'
        ],
        'generic_js_challenge': [
            r'please enable javascript',
            r'javascript is required',
            r'browser check',
            r'security check'
        ]
    }
    
    @staticmethod
    def detect_waf_type(response_text: str, headers: dict, status_code: int) -> tuple:
        """
        Returns (is_blocked, waf_type, needs_browser)
        """
        response_lower = response_text.lower()
        headers_lower = {k.lower(): v.lower() for k, v in headers.items()}
        
        # Checking the headers
        if 'server' in headers_lower:
            server = headers_lower['server']
            if 'cloudflare' in server:
                if any(re.search(pattern, response_lower) for pattern in WAFDetector.WAF_SIGNATURES['cloudflare_challenge']):
                    return True, 'cloudflare_challenge', True
            elif 'akamaighost' in server:
                return True, 'akamai_block', True
        
        # Checking the status of the code
        if status_code in [403, 406, 429]:
            if any(re.search(pattern, response_lower) for pattern in WAFDetector.WAF_SIGNATURES['generic_js_challenge']):
                return True, 'generic_js_challenge', True
            return True, 'http_block', False
        
        # Checking content on JS challenges
        for waf_type, patterns in WAFDetector.WAF_SIGNATURES.items():
            if any(re.search(pattern, response_lower) for pattern in patterns):
                return True, waf_type, True
        
        return False, None, False
