import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict
from jsmon.reporting.templates import HTML_REPORT_TEMPLATE, RESULT_CARD_TEMPLATE

def group_similar_results(results: List, status_tolerance: int = 0, size_tolerance_percent: float = 0.05) -> List[Dict]:
    """Groups similar results by status code + content_length."""
    if not results:
        return []
    
    def calculate_tolerance(content_length: int) -> int:
        if content_length == 0: return 0
        if content_length < 100: return max(10, int(content_length * 0.20))
        elif content_length < 1024: return int(content_length * 0.15)
        elif content_length < 51200: return int(content_length * 0.10)
        else: return max(2048, int(content_length * 0.05))

    def are_similar(r1, r2) -> bool:
        if abs(r1.status - r2.status) > status_tolerance: return False
        if r1.status >= 400:
            if r1.title != r2.title:
                if r1.title != "N/A" and r2.title != "N/A": return False
        
        if r1.content_length < 512 or r2.content_length < 512:
            max_size = max(r1.content_length, r2.content_length)
            min_size = min(r1.content_length, r2.content_length)
            if min_size == 0: return max_size < 50
            ratio = max_size / min_size
            if ratio > 1.30: return False
        
        max_size = max(r1.content_length, r2.content_length)
        tolerance = calculate_tolerance(max_size)
        size_diff = abs(r1.content_length - r2.content_length)
        return size_diff <= tolerance
    
    groups = []
    used_indices = set()
    
    for i, primary in enumerate(results):
        if i in used_indices: continue
        current_group = [primary]
        used_indices.add(i)
        
        for j, candidate in enumerate(results):
            if j <= i or j in used_indices: continue
            if are_similar(primary, candidate):
                current_group.append(candidate)
                used_indices.add(j)
        
        total_size = sum(r.content_length for r in current_group)
        total_time = sum(r.response_time for r in current_group)
        
        groups.append({
            'primary': primary,
            'duplicates': current_group[1:],
            'count': len(current_group),
            'avg_size': total_size // len(current_group) if current_group else 0,
            'avg_time': total_time // len(current_group) if current_group else 0
        })
    
    return groups

def generate_html_report_with_screenshots(probe_results: List, api_keys_dict: dict, output_dir: Path) -> str:
    """Generates a beautiful HTML report with screenshots and grouping of duplicates."""
    print("[+] Generating HTML report with screenshots and duplicate grouping...")
    
    grouped_results = group_similar_results(probe_results)
    
    total_probed = len(probe_results)
    total_unique = len(grouped_results)
    total_duplicates = total_probed - total_unique
    
    status_200 = sum(1 for r in probe_results if r.status == 200)
    status_3xx = sum(1 for r in probe_results if 300 <= r.status < 400)
    status_4xx = sum(1 for r in probe_results if 400 <= r.status < 500)
    status_5xx = sum(1 for r in probe_results if r.status >= 500)
    
    api_keys_html = ""
    if api_keys_dict:
        total_keys = sum(len(keys) for keys in api_keys_dict.values())
        api_cards = []
        for host, keys in api_keys_dict.items():
            for key_type, key_value, source in sorted(list(set(keys))):
                card = f"""
                <div class="api-key-card">
                    <div class="api-key-type">🔥 {key_type}</div>
                    <div class="api-key-value">{key_value}</div>
                    <div class="api-key-source">Host: {host} | Found in: {source}</div>
                </div>
                """
                api_cards.append(card)
        
        api_keys_html = f"""
        <div class="api-keys-section">
            <h2>🔥 Found {total_keys} Potential API Keys</h2>
            {"".join(api_cards)}
        </div>
        """
    
    def generate_card_with_duplicates(group: Dict) -> str:
        primary = group['primary']
        duplicates = group['duplicates']
        count = group['count']
        
        if primary.status == 200: status_class = "200"
        elif 300 <= primary.status < 400: status_class = f"{primary.status}"
        elif primary.status in [401, 403]: status_class = f"{primary.status}"
        elif primary.status == 404: status_class = "404"
        elif primary.status >= 500: status_class = "500"
        else: status_class = "other"
        
        def format_size(size):
            if size > 1024 * 1024: return f"{size / (1024*1024):.2f} MB"
            elif size > 1024: return f"{size / 1024:.2f} KB"
            else: return f"{size} B"
        
        content_length = format_size(primary.content_length)
        
        fetch_badge_map = {"browser": "🌐 Browser", "aiohttp": "🔌 API", "fallback": "⚡ Fallback"}
        fetch_badge_text = fetch_badge_map.get(primary.fetch_method, "❓ Unknown")
        
        if primary.screenshot_path and os.path.exists(primary.screenshot_path):
            filename = os.path.basename(primary.screenshot_path)
            screenshot_html = f'<img src="screenshots/{filename}" alt="Screenshot" class="screenshot" onclick="openModal(\'screenshots/{filename}\')">'
        else:
            screenshot_html = '<div class="no-screenshot">No Screenshot</div>'
        
        duplicate_badge = ""
        if count > 1:
            duplicate_badge = f'<div class="duplicate-badge">+{count-1} similar</div>'
        
        duplicates_section = ""
        if duplicates:
            duplicate_items = []
            for dup in duplicates:
                dup_size = format_size(dup.content_length)
                duplicate_items.append(f"""
                <div class="duplicate-item">
                    <div class="dup-url">{dup.url}</div>
                    <div class="dup-meta">
                        <span>📦 {dup_size}</span>
                        <span>⏱️ {dup.response_time}ms</span>
                    </div>
                </div>
                """)
            
            duplicates_section = f"""
            <div class="duplicates-section">
                <div class="duplicates-header" onclick="toggleDuplicates(this)">
                    <div class="duplicates-title">
                        <span class="duplicates-arrow">▶</span>
                        <span>Show {len(duplicates)} similar result{'s' if len(duplicates) > 1 else ''}</span>
                    </div>
                    <span style="color: #6c757d; font-size: 0.85em;">
                        Avg: {format_size(group['avg_size'])} | {group['avg_time']}ms
                    </span>
                </div>
                <div class="duplicates-list">
                    {"".join(duplicate_items)}
                </div>
            </div>
            """
        
        # Truncate display URL for better readability
        display_url = primary.display_name if hasattr(primary, 'display_name') else primary.url
        if len(display_url) > 60:
            display_url = display_url[:57] + "..."
        
        return RESULT_CARD_TEMPLATE.format(
            screenshot_html=screenshot_html,
            status=primary.status if primary.status > 0 else "Error",
            status_class=status_class,
            full_url=primary.url,
            display_url=display_url,
            title=primary.title,
            content_length=content_length,
            response_time=primary.response_time,
            fetch_method=primary.fetch_method,
            fetch_badge_text=fetch_badge_text,
            duplicate_badge=duplicate_badge,
            duplicates_section=duplicates_section
        )
    
    # Combine all results (browser + API)
    all_html = []
    for group in sorted(grouped_results, key=lambda x: (x['primary'].status != 200, x['primary'].status)):
        all_html.append(generate_card_with_duplicates(group))
    
    html_content = HTML_REPORT_TEMPLATE.format(
        scan_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        total_probed=total_probed,
        status_200=status_200,
        status_3xx=status_3xx,
        status_4xx=status_4xx,
        status_5xx=status_5xx,
        api_keys_html=api_keys_html,
        results_html="".join(all_html)
    )
    
    report_path = output_dir / "report.html"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return str(report_path)
