import re
import json
import aiohttp
from urllib.parse import urljoin

async def check_and_extract_sourcemap(session: aiohttp.ClientSession, js_url: str, js_content: str) -> dict:
    """
    Checks for the presence of a sourcemap and extracts content from it.
    Returns: {'sources': [{'name': str, 'content': str}]} or None
    """
    sourcemap_url = None
    
    # 1. Searching for a link to the map in the code
    # //# sourceMappingURL=file.js.map
    map_match = re.search(r'//#\s*sourceMappingURL=(.+)', js_content)
    if map_match:
        map_filename = map_match.group(1).strip()
        sourcemap_url = urljoin(js_url, map_filename)
    else:
        # 2. Trying to add .map
        sourcemap_url = js_url + '.map'
        
    if not sourcemap_url:
        return None
        
    try:
        async with session.get(sourcemap_url, timeout=10, ssl=False) as resp:
            if resp.status == 200:
                try:
                    map_data = await resp.json()
                    if 'sources' in map_data and 'sourcesContent' in map_data:
                        extracted = {'sources': []}
                        for i, source_path in enumerate(map_data['sources']):
                            if i < len(map_data['sourcesContent']):
                                content = map_data['sourcesContent'][i]
                                if content:
                                    extracted['sources'].append({
                                        'name': source_path,
                                        'content': content
                                    })
                        return extracted if extracted['sources'] else None
                except json.JSONDecodeError:
                    pass
    except Exception:
        pass
        
    return None
