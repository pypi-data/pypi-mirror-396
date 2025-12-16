HTML_REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JS Analyzer Report - {scan_date}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        :root {{
            --bg-primary: #ffffff;
            --bg-secondary: #f8fafc;
            --bg-card: #ffffff;
            --text-primary: #0f172a;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --accent-primary: #6366f1;
            --accent-hover: #4f46e5;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
        }}
        
        [x-cloak] {{ display: none !important; }}
        
        .dark {{
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --border-color: #334155;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.4);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.5);
        }}
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            transition: background-color 0.3s ease, color 0.3s ease;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 2rem;
        }}
        
        /* Header */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 1rem;
            padding: 3rem 2rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-xl);
            position: relative;
            overflow: hidden;
        }}
        
        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg"><defs><pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M 20 0 L 0 0 0 20" fill="none" stroke="white" stroke-width="0.5" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }}
        
        .header-content {{
            position: relative;
            z-index: 1;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            color: white;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }}
        
        .header .subtitle {{
            color: rgba(255,255,255,0.9);
            font-size: 1.1rem;
        }}
        
        .header-actions {{
            position: absolute;
            top: 2rem;
            right: 2rem;
            display: flex;
            gap: 0.75rem;
            z-index: 2;
        }}
        
        /* Toolbar */
        .toolbar {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-md);
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 300px;
            position: relative;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 0.75rem 1rem 0.75rem 2.5rem;
            border: 1px solid var(--border-color);
            border-radius: 0.5rem;
            background: var(--bg-secondary);
            color: var(--text-primary);
            font-family: inherit;
            font-size: 0.95rem;
            transition: all 0.2s;
        }}
        
        .search-box input:focus {{
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }}
        
        .search-icon {{
            position: absolute;
            left: 0.75rem;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-secondary);
        }}
        
        /* Buttons */
        .btn {{
            padding: 0.625rem 1.25rem;
            border-radius: 0.5rem;
            font-weight: 500;
            font-size: 0.875rem;
            cursor: pointer;
            transition: all 0.2s;
            border: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .btn-primary {{
            background: var(--accent-primary);
            color: white;
        }}
        
        .btn-primary:hover {{
            background: var(--accent-hover);
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }}
        
        .btn-secondary {{
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 1px solid var(--border-color);
        }}
        
        .btn-secondary:hover {{
            background: var(--bg-card);
            transform: translateY(-1px);
        }}
        
        /* Stats Grid */
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            padding: 1.5rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            box-shadow: var(--shadow-sm);
        }}
        
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-lg);
            border-color: var(--accent-primary);
        }}
        
        .stat-card.active {{
            border-color: var(--accent-primary);
            border-width: 2px;
            background: rgba(99, 102, 241, 0.05);
        }}
        
        .stat-card .number {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--accent-primary);
            margin-bottom: 0.25rem;
        }}
        
        .stat-card .label {{
            color: var(--text-secondary);
            font-size: 0.875rem;
            font-weight: 500;
        }}
        
        /* Results Grid */
        .results-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
        }}
        
        .result-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 0.75rem;
            overflow: hidden;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            box-shadow: var(--shadow-sm);
        }}
        
        .result-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--shadow-xl);
            border-color: var(--accent-primary);
        }}
        
        .result-card.hidden {{
            display: none;
        }}
        
        /* Screenshot */
        .screenshot-container {{
            position: relative;
            width: 100%;
            height: 220px;
            background: var(--bg-secondary);
            overflow: hidden;
        }}
        
        .screenshot {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            cursor: pointer;
            transition: transform 0.3s;
        }}
        
        .screenshot:hover {{
            transform: scale(1.05);
        }}
        
        .no-screenshot {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--text-secondary);
            font-size: 1rem;
        }}
        
        /* Badges */
        .badge {{
            position: absolute;
            padding: 0.375rem 0.75rem;
            border-radius: 0.375rem;
            font-weight: 600;
            font-size: 0.75rem;
            backdrop-filter: blur(12px);
            box-shadow: var(--shadow-md);
        }}
        
        .status-badge {{
            top: 0.75rem;
            right: 0.75rem;
        }}
        
        .status-200 {{ background: rgba(34, 197, 94, 0.9); color: white; }}
        .status-301, .status-302 {{ background: rgba(251, 191, 36, 0.9); color: #1f2937; }}
        .status-401, .status-403 {{ background: rgba(239, 68, 68, 0.9); color: white; }}
        .status-404 {{ background: rgba(107, 114, 128, 0.9); color: white; }}
        .status-500 {{ background: rgba(220, 38, 38, 0.9); color: white; }}
        .status-other {{ background: rgba(99, 102, 241, 0.9); color: white; }}
        
        .fetch-badge {{
            top: 0.75rem;
            left: 0.75rem;
        }}
        
        .fetch-browser {{ background: rgba(59, 130, 246, 0.9); color: white; }}
        .fetch-aiohttp {{ background: rgba(168, 85, 247, 0.9); color: white; }}
        .fetch-fallback {{ background: rgba(251, 146, 60, 0.9); color: white; }}
        
        /* Card Content */
        .card-content {{
            padding: 1.25rem;
        }}
        
        .card-url {{
            font-size: 0.8rem;
            color: var(--accent-primary);
            word-break: break-all;
            margin-bottom: 0.75rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .copy-btn {{
            padding: 0.25rem 0.5rem;
            background: rgba(99, 102, 241, 0.1);
            border: 1px solid var(--accent-primary);
            border-radius: 0.25rem;
            cursor: pointer;
            color: var(--accent-primary);
            font-size: 0.7rem;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        
        .copy-btn:hover {{
            background: var(--accent-primary);
            color: white;
        }}
        
        .card-title {{
            font-size: 1rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: var(--text-primary);
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-meta {{
            display: flex;
            gap: 1rem;
            padding-top: 0.75rem;
            margin-top: 0.75rem;
            border-top: 1px solid var(--border-color);
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}
        
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.375rem;
        }}
        
        /* API Keys Section */
        .api-section {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-left: 4px solid #f59e0b;
            border-radius: 0.75rem;
            padding: 1.5rem;
            margin-bottom: 2rem;
            box-shadow: var(--shadow-md);
        }}
        
        .api-section h2 {{
            color: var(--text-primary);
            margin-bottom: 1rem;
            font-size: 1.5rem;
        }}
        
        .api-key-card {{
            background: var(--bg-secondary);
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-radius: 0.5rem;
            border-left: 3px solid #ef4444;
        }}
        
        .api-key-type {{
            font-weight: 600;
            color: #ef4444;
            margin-bottom: 0.5rem;
        }}
        
        .api-key-value {{
            font-family: 'Courier New', monospace;
            background: var(--bg-primary);
            padding: 0.5rem;
            border-radius: 0.375rem;
            margin: 0.5rem 0;
            word-break: break-all;
            font-size: 0.85rem;
        }}
        
        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            backdrop-filter: blur(8px);
        }}
        
        .modal.active {{
            display: flex;
            align-items: center;
            justify-content: center;
            animation: fadeIn 0.2s;
        }}
        
        .modal img {{
            max-width: 90%;
            max-height: 90%;
            object-fit: contain;
            border-radius: 0.5rem;
            box-shadow: var(--shadow-xl);
        }}
        
        .modal-close {{
            position: absolute;
            top: 2rem;
            right: 2rem;
            color: white;
            font-size: 2.5rem;
            font-weight: bold;
            cursor: pointer;
            width: 3rem;
            height: 3rem;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            background: rgba(255,255,255,0.1);
            transition: all 0.2s;
        }}
        
        .modal-close:hover {{
            background: rgba(255,255,255,0.2);
            transform: scale(1.1);
        }}
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        
        @keyframes slideDown {{
            from {{ 
                opacity: 0;
                transform: translateY(-10px);
            }}
            to {{ 
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .slide-down {{
            animation: slideDown 0.3s ease-out;
        }}
        
        /* Duplicate section */
        .duplicates-section {{
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px dashed var(--border-color);
        }}
        
        .duplicates-header {{
            cursor: pointer;
            padding: 0.75rem;
            background: var(--bg-secondary);
            border-radius: 0.5rem;
            transition: all 0.2s;
            user-select: none;
        }}
        
        .duplicates-header:hover {{
            background: var(--border-color);
        }}
        
        .duplicates-list {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease-out;
        }}
        
        .duplicates-list.expanded {{
            max-height: 800px;
            margin-top: 0.75rem;
        }}
        
        .duplicate-item {{
            padding: 0.625rem;
            margin: 0.375rem 0;
            background: var(--bg-secondary);
            border-left: 3px solid var(--accent-primary);
            border-radius: 0.375rem;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body x-data="appData()" :class="darkMode ? 'dark' : ''" x-cloak>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>🔍 JS Analyzer Report</h1>
                <div class="subtitle">Generated on {scan_date}</div>
            </div>
            <div class="header-actions">
                <button @click="exportJSON()" class="btn btn-secondary">
                    📥 Export JSON
                </button>
                <button @click="darkMode = !darkMode" class="btn btn-secondary">
                    <span x-show="!darkMode">🌙</span>
                    <span x-show="darkMode">☀️</span>
                </button>
            </div>
        </div>
        
        <div class="toolbar">
            <div class="search-box">
                <span class="search-icon">🔍</span>
                <input 
                    type="text" 
                    placeholder="Search by URL or title..." 
                    x-model="searchQuery"
                    @input="filterResults()"
                >
            </div>
            <div style="color: var(--text-secondary); font-size: 0.875rem;">
                <span x-text="filteredCount"></span> results
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card" :class="{{ 'active': activeFilter === 'all' }}" @click="setFilter('all')">
                <div class="number">{total_probed}</div>
                <div class="label">Total Probed</div>
            </div>
            <div class="stat-card" :class="{{ 'active': activeFilter === '200' }}" @click="setFilter('200')">
                <div class="number">{status_200}</div>
                <div class="label">200 OK</div>
            </div>
            <div class="stat-card" :class="{{ 'active': activeFilter === '3xx' }}" @click="setFilter('3xx')">
                <div class="number">{status_3xx}</div>
                <div class="label">3xx Redirects</div>
            </div>
            <div class="stat-card" :class="{{ 'active': activeFilter === '4xx' }}" @click="setFilter('4xx')">
                <div class="number">{status_4xx}</div>
                <div class="label">4xx Errors</div>
            </div>
            <div class="stat-card" :class="{{ 'active': activeFilter === '5xx' }}" @click="setFilter('5xx')">
                <div class="number">{status_5xx}</div>
                <div class="label">5xx Errors</div>
            </div>
        </div>
        
        {api_keys_html}
        
        <div style="margin-bottom: 1rem;">
            <h2 style="color: var(--text-primary); font-size: 1.5rem;">📡 Endpoint Probing Results</h2>
        </div>
        
        <div class="results-grid">
            {results_html}
        </div>
    </div>
    
    <div class="modal" id="imageModal">
        <span class="modal-close" onclick="closeModal()">&times;</span>
        <img id="modalImage" src="">
    </div>
    
    <script>
        function appData() {{
            return {{
                darkMode: localStorage.getItem('darkMode') === 'true',
                searchQuery: '',
                activeFilter: 'all',
                filteredCount: {total_probed},
                allResults: [],
                
                init() {{
                    this.$watch('darkMode', value => {{
                        localStorage.setItem('darkMode', value);
                    }});
                    
                    // Store all results for filtering
                    this.allResults = Array.from(document.querySelectorAll('.result-card')).map(card => ({{
                        element: card,
                        url: card.querySelector('.card-url')?.textContent.toLowerCase() || '',
                        title: card.querySelector('.card-title')?.textContent.toLowerCase() || '',
                        status: card.dataset.status
                    }}));
                }},
                
                setFilter(filter) {{
                    this.activeFilter = filter;
                    this.filterResults();
                }},
                
                filterResults() {{
                    const query = this.searchQuery.toLowerCase();
                    let count = 0;
                    
                    this.allResults.forEach(result => {{
                        const matchesSearch = !query || 
                            result.url.includes(query) || 
                            result.title.includes(query);
                        
                        const matchesFilter = this.activeFilter === 'all' || 
                            this.matchesStatusFilter(result.status, this.activeFilter);
                        
                        const shouldShow = matchesSearch && matchesFilter;
                        result.element.classList.toggle('hidden', !shouldShow);
                        
                        if (shouldShow) count++;
                    }});
                    
                    this.filteredCount = count;
                }},
                
                matchesStatusFilter(status, filter) {{
                    const code = parseInt(status);
                    if (filter === '200') return code === 200;
                    if (filter === '3xx') return code >= 300 && code < 400;
                    if (filter === '4xx') return code >= 400 && code < 500;
                    if (filter === '5xx') return code >= 500;
                    return false;
                }},
                
                exportJSON() {{
                    const data = {{
                        scan_date: '{scan_date}',
                        stats: {{
                            total_probed: {total_probed},
                            status_200: {status_200},
                            status_3xx: {status_3xx},
                            status_4xx: {status_4xx},
                            status_5xx: {status_5xx}
                        }},
                        results: this.allResults.map(r => ({{
                            url: r.url,
                            title: r.title,
                            status: r.status
                        }}))
                    }};
                    
                    const blob = new Blob([JSON.stringify(data, null, 2)], {{ type: 'application/json' }});
                    const url = URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = 'js-analyzer-report-{scan_date}.json';
                    a.click();
                    URL.revokeObjectURL(url);
                }}
            }}
        }}
        
        function openModal(imgSrc) {{
            document.getElementById('imageModal').classList.add('active');
            document.getElementById('modalImage').src = imgSrc;
        }}
        
        function closeModal() {{
            document.getElementById('imageModal').classList.remove('active');
        }}
        
        function copyURL(url, btn) {{
            navigator.clipboard.writeText(url).then(() => {{
                const originalText = btn.textContent;
                btn.textContent = '✓ Copied';
                setTimeout(() => {{
                    btn.textContent = originalText;
                }}, 1500);
            }});
        }}
        
        function toggleDuplicates(header) {{
            const list = header.nextElementSibling;
            list.classList.toggle('expanded');
        }}
        
        document.getElementById('imageModal').addEventListener('click', function(e) {{
            if (e.target === this) closeModal();
        }});
        
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') closeModal();
        }});
    </script>
</body>
</html>"""

RESULT_CARD_TEMPLATE = """
<div class="result-card slide-down" data-status="{status}" data-method="{fetch_method}">
    <div class="screenshot-container">
        {screenshot_html}
        <div class="badge fetch-badge fetch-{fetch_method}">{fetch_badge_text}</div>
        <div class="badge status-badge status-{status_class}">{status}</div>
        {duplicate_badge}
    </div>
    <div class="card-content">
        <div class="card-url">
            <span style="flex: 1; overflow: hidden; text-overflow: ellipsis;">{display_url}</span>
            <button class="copy-btn" onclick="copyURL('{full_url}', this)">📋 Copy</button>
        </div>
        <div class="card-title">{title}</div>
        <div class="card-meta">
            <div class="meta-item"><span>📦</span><span>{content_length}</span></div>
            <div class="meta-item"><span>⏱️</span><span>{response_time}ms</span></div>
        </div>
        {duplicates_section}
    </div>
</div>
"""
