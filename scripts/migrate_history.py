"""
既存のhistory.jsonを新形式に移行し、history.htmlを生成するスクリプト
"""
import os
import json

PUBLIC_DIR = "public"
DATA_DIR = os.path.join(PUBLIC_DIR, "data")
HISTORY_FILE = os.path.join(PUBLIC_DIR, "history.json")

def migrate_history():
    """旧形式のhistory.jsonを新形式に移行"""
    
    # 既存のhistory.jsonを読み込み
    if not os.path.exists(HISTORY_FILE):
        print("history.json not found")
        return
    
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 既に新形式の場合はスキップ
    if isinstance(data, dict) and 'entries' in data:
        print("Already in new format")
        return data
    
    # 旧形式（リスト）から新形式（辞書）に変換
    entries = []
    
    for entry_id in data:
        json_path = os.path.join(DATA_DIR, f"{entry_id}.json")
        entry_data = {'id': entry_id}
        
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                news_data = json.load(f)
            
            meta = news_data.get('meta', {})
            entry_data['fetch_time_jst'] = meta.get('fetch_time', meta.get('fetch_time_jst', entry_id))
            entry_data['mood_keyword'] = news_data.get('mood_keyword', 'Unknown')
            entry_data['daily_summary'] = news_data.get('daily_summary', '')
            entry_data['model_name'] = meta.get('model_name', 'gemini-3-flash-preview')
            
            # トークン情報（旧形式は単一数値、新形式は辞書）
            summary_tokens = meta.get('summary_tokens', 0)
            if isinstance(summary_tokens, dict):
                entry_data['total_tokens'] = summary_tokens.get('total', 0)
            else:
                entry_data['total_tokens'] = summary_tokens
            
            entry_data['total_processing_time_sec'] = meta.get('total_processing_time_sec', 0)
        
        entries.append(entry_data)
    
    # 新形式で保存
    new_history = {
        "version": 2,
        "entries": sorted(entries, key=lambda x: x['id'])
    }
    
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_history, f, ensure_ascii=False, indent=2)
    
    print(f"Migrated {len(entries)} entries to new format")
    return new_history

def generate_history_page(history):
    """履歴一覧HTMLを生成"""
    print("Generating history page...")
    
    entries_html = ""
    sorted_entries = sorted(history['entries'], key=lambda x: x['id'], reverse=True)
    
    for entry in sorted_entries:
        mood = entry.get('mood_keyword', 'Unknown')
        summary = entry.get('daily_summary', '')[:150] + '...' if len(entry.get('daily_summary', '')) > 150 else entry.get('daily_summary', '')
        fetch_time = entry.get('fetch_time_jst', entry.get('id', 'Unknown'))
        tokens = entry.get('total_tokens', 'N/A')
        model = entry.get('model_name', 'N/A')
        
        entries_html += f"""
        <article class="history-card" data-mood="{mood.lower()}">
            <div class="card-header">
                <time class="card-date">{fetch_time}</time>
                <span class="card-mood">{mood}</span>
            </div>
            <p class="card-summary">{summary}</p>
            <div class="card-meta">
                <span class="meta-item">🤖 {model}</span>
                <span class="meta-item">🔢 {tokens} tokens</span>
            </div>
            <div class="card-actions">
                <a href="./archives/{entry['id']}.html" class="btn-view">📰 記事を見る</a>
                <a href="./data/{entry['id']}.json" class="btn-data">📊 JSONデータ</a>
            </div>
        </article>
        """
    
    history_html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MorphoNews Archive | 進化するニュースの記録</title>
    <meta name="description" content="MorphoNewsの過去のニュースアーカイブ一覧。AIが自動生成した日々のテックニュースを振り返ることができます。">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0a0f;
            --bg-secondary: #12121a;
            --bg-card: #1a1a25;
            --text-primary: #e8e8ef;
            --text-secondary: #9898a8;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            --border-color: #2a2a3a;
            --success: #22c55e;
            --warning: #f59e0b;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background: var(--bg-primary);
            color: var(--text-primary);
            font-family: 'Noto Sans JP', sans-serif;
            min-height: 100vh;
            line-height: 1.6;
        }}

        /* Animated background */
        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 80%, rgba(99, 102, 241, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(139, 92, 246, 0.08) 0%, transparent 50%),
                radial-gradient(circle at 50% 50%, rgba(168, 85, 247, 0.05) 0%, transparent 70%);
            pointer-events: none;
            z-index: -1;
        }}

        header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
        }}

        .header-content {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }}

        .logo-icon {{
            width: 48px;
            height: 48px;
            background: var(--accent-gradient);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            animation: pulse 2s infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        .logo h1 {{
            font-size: 1.75rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .logo span {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            display: block;
        }}

        nav {{
            display: flex;
            gap: 1rem;
        }}

        nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.3s ease;
            font-size: 0.9rem;
        }}

        nav a:hover {{
            background: var(--bg-card);
            color: var(--text-primary);
        }}

        nav a.active {{
            background: var(--accent-gradient);
            color: white;
        }}

        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
        }}

        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .stat-label {{
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-top: 0.25rem;
        }}

        .history-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
        }}

        .history-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .history-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--accent-gradient);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .history-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            box-shadow: 0 8px 32px rgba(99, 102, 241, 0.15);
        }}

        .history-card:hover::before {{
            opacity: 1;
        }}

        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}

        .card-date {{
            font-family: 'Fira Code', monospace;
            font-size: 0.875rem;
            color: var(--text-secondary);
        }}

        .card-mood {{
            background: var(--accent-gradient);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .card-summary {{
            color: var(--text-primary);
            font-size: 0.95rem;
            line-height: 1.7;
            margin-bottom: 1rem;
        }}

        .card-meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}

        .meta-item {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}

        .card-actions {{
            display: flex;
            gap: 0.75rem;
        }}

        .card-actions a {{
            flex: 1;
            text-align: center;
            padding: 0.75rem 1rem;
            border-radius: 8px;
            text-decoration: none;
            font-size: 0.875rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}

        .btn-view {{
            background: var(--accent-gradient);
            color: white;
        }}

        .btn-view:hover {{
            transform: scale(1.02);
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
        }}

        .btn-data {{
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border-color);
        }}

        .btn-data:hover {{
            border-color: var(--accent-primary);
            color: var(--text-primary);
        }}

        footer {{
            background: var(--bg-secondary);
            border-top: 1px solid var(--border-color);
            padding: 2rem;
            margin-top: 3rem;
            text-align: center;
        }}

        .footer-content {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .footer-text {{
            color: var(--text-secondary);
            font-size: 0.875rem;
        }}

        .footer-text a {{
            color: var(--accent-primary);
            text-decoration: none;
        }}

        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-secondary);
        }}

        .empty-state-icon {{
            font-size: 4rem;
            margin-bottom: 1rem;
        }}

        @media (max-width: 768px) {{
            header {{
                padding: 1rem;
            }}
            
            .header-content {{
                flex-direction: column;
                text-align: center;
            }}
            
            main {{
                padding: 1rem;
            }}
            
            .history-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header>
        <div class="header-content">
            <div class="logo">
                <div class="logo-icon">🦋</div>
                <div>
                    <h1>MorphoNews</h1>
                    <span>Archive Collection</span>
                </div>
            </div>
            <nav>
                <a href="./archives/{sorted_entries[0]['id'] if sorted_entries else ''}.html">🏠 最新版</a>
                <a href="./history.html" class="active">📚 アーカイブ</a>
                <a href="https://github.com/sora0513/morphonews" target="_blank">💻 GitHub</a>
            </nav>
        </div>
    </header>

    <main>
        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-value">{len(sorted_entries)}</div>
                <div class="stat-label">総アーカイブ数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sorted_entries[0]['id'][:10] if sorted_entries else 'N/A'}</div>
                <div class="stat-label">最新更新日</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sorted_entries[-1]['id'][:10] if sorted_entries else 'N/A'}</div>
                <div class="stat-label">初回生成日</div>
            </div>
        </div>

        <section class="history-grid">
            {entries_html if entries_html else '<div class="empty-state"><div class="empty-state-icon">📭</div><p>まだアーカイブがありません</p></div>'}
        </section>
    </main>

    <footer>
        <div class="footer-content">
            <p class="footer-text">
                🦋 MorphoNews - AI駆動の自己進化型ニュースサイト<br>
                Powered by <a href="https://github.com/sora0513/morphonews" target="_blank">GitHub Actions</a> & Gemini AI
            </p>
        </div>
    </footer>
</body>
</html>"""
    
    history_page_path = os.path.join(PUBLIC_DIR, "history.html")
    with open(history_page_path, 'w', encoding='utf-8') as f:
        f.write(history_html)
    
    print(f"History page generated: {history_page_path}")

if __name__ == "__main__":
    history = migrate_history()
    if history:
        generate_history_page(history)
