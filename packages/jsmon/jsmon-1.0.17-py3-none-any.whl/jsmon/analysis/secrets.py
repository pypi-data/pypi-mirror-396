import re

# Regex patterns for API keys
API_KEY_PATTERNS = {
    'google_api': r'AIza[0-9A-Za-z-_]{35}',
    'firebase': r'AIza[0-9A-Za-z-_]{35}',
    'aws_access_key': r'AKIA[0-9A-Z]{16}',
    'aws_secret': r'(?<![A-Za-z0-9/+=])[A-Za-z0-9/+=]{40}(?![A-Za-z0-9/+=])',
    'github_token': r'(gh[pous]_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})',
    'slack_token': r'xox[baprs]-([0-9a-zA-Z]{10,48})',
    'stripe_key': r'(?:r|s)k_live_[0-9a-zA-Z]{24}',
    'paypal_token': r'access_token\$production\$[0-9a-z]{16}\$[0-9a-f]{32}',
    'mailgun_key': r'key-[0-9a-zA-Z]{32}',
    'twilio_sid': r'AC[a-zA-Z0-9]{32}',
    'twilio_token': r'[a-f0-9]{32}',
    'sendgrid_key': r'SG\.[0-9A-Za-z-_]{22}\.[0-9A-Za-z-_]{43}',
    'generic_api_key': r'(?i)(?:api_key|apikey|secret|token|auth_token|access_token)[\"\']?\s*[:=]\s*[\"\']([a-zA-Z0-9_\-]{16,64})[\"\']',
    'jwt_token': r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*',
    'private_key': r'-----BEGIN PRIVATE KEY-----',
    'rsa_private_key': r'-----BEGIN RSA PRIVATE KEY-----',
    'ssh_private_key': r'-----BEGIN OPENSSH PRIVATE KEY-----',
    'pgp_private_key': r'-----BEGIN PGP PRIVATE KEY BLOCK-----',
    'facebook_access_token': r'EAACEdEose0cBA[0-9A-Za-z]+',
    'heroku_api_key': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
    'mailchimp_api_key': r'[0-9a-f]{32}-us[0-9]{1,2}',
    'square_access_token': r'sq0atp-[0-9A-Za-z\-_]{22}',
    'square_oauth_secret': r'sq0csp-[0-9A-Za-z\-_]{43}',
    'telegram_bot_token': r'[0-9]{9}:[a-zA-Z0-9_-]{35}',
}

COMPILED_API_KEY_PATTERNS = {
    name: re.compile(pattern) for name, pattern in API_KEY_PATTERNS.items()
}

def extract_api_keys(content: str) -> list:
    """Finds potential API keys in the content."""
    found_keys = []
    
    # Fast check: if there are no keywords, we skip heavy regexes
    if not any(k in content for k in ['key', 'token', 'secret', 'auth', 'AIza', 'AKIA', 'eyJ']):
        return []

    for name, pattern in COMPILED_API_KEY_PATTERNS.items():
        matches = pattern.findall(content)
        for match in matches:
            # Filtering out obvious false positives
            if isinstance(match, tuple): match = match[0]
            if len(match) < 8: continue
            if "example" in match.lower() or "test" in match.lower(): continue
            
            found_keys.append((name, match))
            
    return list(set(found_keys))
