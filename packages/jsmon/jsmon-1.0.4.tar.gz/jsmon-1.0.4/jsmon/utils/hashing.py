import hashlib

def calculate_content_hash(content: str) -> str:
    """Calculate MD5 hash of content for deduplication"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()
