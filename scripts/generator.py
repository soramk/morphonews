import os
import json
import shutil
import feedparser
import google.generativeai as genai
from datetime import datetime, timezone, timedelta
import time

# --- 設定 ---
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    # 開発環境などでキーがない場合の安全策（Github ActionsではSecrets必須）
    pass 

# Geminiの設定
if API_KEY:
    genai.configure(api_key=API_KEY)
    
MODEL_NAME = "gemini-2.5-flash-preview-05-20"

# ディレクトリ構成
PUBLIC_DIR = "public"
ARCHIVE_DIR = os.path.join(PUBLIC_DIR, "archives") # HTML保管場所
DATA_DIR = os.path.join(PUBLIC_DIR, "data")       # JSON保管場所
HISTORY_FILE = os.path.join(PUBLIC_DIR, "history.json")

# JST タイムゾーン
JST = timezone(timedelta(hours=9))

RSS_FEEDS = [
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "https://qiita.com/popular-items/feed",
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
]

# --- ヘルパー関数: 履歴管理 ---
def load_history():
    """履歴JSONを読み込む（新形式に対応）"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                # 新形式（辞書型）と旧形式（リスト型）の両方に対応
                if isinstance(data, dict):
                    return data
                elif isinstance(data, list):
                    # 旧形式をマイグレーション
                    return {"entries": [{"id": h} for h in data], "version": 2}
            except:
                return {"entries": [], "version": 2}
    return {"entries": [], "version": 2}

def save_history(history):
    """履歴JSONを保存"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_history_entry(history, entry_data):
    """履歴にエントリを追加"""
    # 既存エントリを確認
    existing_ids = {e['id'] for e in history['entries']}
    if entry_data['id'] not in existing_ids:
        history['entries'].append(entry_data)
        # IDでソート
        history['entries'] = sorted(history['entries'], key=lambda x: x['id'])
    return history

def get_prev_link(current_id, history):
    """履歴リストから、今回(current_id)の一つ前のIDを探してリンクを返す"""
    sorted_entries = sorted(history['entries'], key=lambda x: x['id'])
    past_ids = [e['id'] for e in sorted_entries if e['id'] < current_id]
    
    if past_ids:
        prev_id = past_ids[-1]
        return f"./{prev_id}.html"
    
    return "#"

# --- 1. ニュース収集 (編集者AI) ---
def fetch_and_summarize_news(timestamp_id):
    print("Step 1: Fetching news...")
    start_time = datetime.now(JST)
    fetch_start = time.time()
    
    articles = []
    source_urls = []
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            source_urls.append(url)
            # 各フィードから最新2件
            for entry in feed.entries[:2]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get('summary', '')[:200] + "...",
                    "source": feed.feed.get('title', 'Unknown')
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    summary_prompt = f"""
    ITジャーナリストとして、以下の記事リストからWeb記事コンテンツを作成してください。
    
    【要件】
    1. 「今日のテックトレンド要約」(400文字)を作成。
    2. 注目ニュース3選をピックアップ。
    3. 出力はJSON形式。
    
    入力: {json.dumps(articles, ensure_ascii=False)}
    
    出力Schema:
    {{
        "daily_summary": "...",
        "top_news": [ {{ "title": "...", "description": "...", "link": "..." }} ],
        "mood_keyword": "今のニュースの雰囲気(英単語)"
    }}
    """
    
    print(f"Requesting AI summarization ({MODEL_NAME})...")
    summary_gen_start = time.time()
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )
    response = model.generate_content(summary_prompt)
    summary_gen_time = time.time() - summary_gen_start
    
    content_json = json.loads(response.text)
    
    # メタデータ (IDとしてtimestamp_idを使用)
    content_json['meta'] = {
        'id': timestamp_id,
        'display_date': start_time.strftime('%Y-%m-%d %H:%M'),
        'fetch_time_jst': start_time.strftime('%Y-%m-%d %H:%M:%S JST'),
        'sources': source_urls,
        'model_name': MODEL_NAME,
        'summary_prompt': summary_prompt.strip(),
        'summary_tokens': {
            'input': response.usage_metadata.prompt_token_count,
            'output': response.usage_metadata.candidates_token_count,
            'total': response.usage_metadata.total_token_count
        },
        'summary_generation_time_sec': round(summary_gen_time, 2),
        'article_count': len(articles)
    }
    
    total_fetch_time = time.time() - fetch_start
    content_json['meta']['total_fetch_time_sec'] = round(total_fetch_time, 2)
    
    # JSONデータの保存
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, f"{timestamp_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content_json, f, ensure_ascii=False, indent=2)
        
    return content_json

# --- 2. デザイン生成 (デザイナーAI) ---
def evolve_ui(news_data, prev_link, history):
    current_id = news_data['meta']['id']
    display_date = news_data['meta']['display_date']
    print(f"Step 2: Evolving UI for {current_id}...")
    
    design_start = time.time()
    
    # 最新のアーカイブがあれば参考にする（なければ空）
    reference_html = ""
    try:
        archives = sorted(os.listdir(ARCHIVE_DIR))
        if archives:
            latest_archive = archives[-1]
            with open(os.path.join(ARCHIVE_DIR, latest_archive), "r", encoding="utf-8") as f:
                reference_html = f.read()[:5000]  # トークン節約のため先頭5000文字のみ
    except:
        pass
    
    design_prompt = f"""
    あなたは前衛的Webデザイナーです。MorphoNewsのHTMLを作成します。
    
    【指令】
    1. 以前のデザイン（HTML構造）を参考にしつつ、
       ムード「{news_data['mood_keyword']}」に合わせて、
       **配色・フォント・レイアウトを大胆に変異**させてください。
    
    2. **ナビゲーションバーの実装 (必須)**:
       ページ上部または下部にナビゲーションを作ってください。
       - [<< Prev Update] ボタン: リンク先 "{prev_link}" (prev_linkが "#" なら非表示か無効化)
       - [Archive List] ボタン: リンク先 "../history.html"
       - 現在の日時表示: {display_date} (JST)

    3. **システム情報の表示 (必須)**:
       フッターに以下の生成統計を明確に表示するセクションを作成してください。
       - 取得日時(JST): {news_data['meta']['fetch_time_jst']}
       - 収集記事数: {news_data['meta']['article_count']}
       - 使用モデル: {news_data['meta']['model_name']}
       - 要約AIトークン: 入力={news_data['meta']['summary_tokens']['input']}, 出力={news_data['meta']['summary_tokens']['output']}, 合計={news_data['meta']['summary_tokens']['total']}
       - 要約生成時間: {news_data['meta']['summary_generation_time_sec']}秒
       - デザインAIトークン: {{{{ DESIGN_TOKENS }}}} (後で置換)
       - デザイン生成時間: {{{{ DESIGN_TIME }}}}秒 (後で置換)
       - 全体処理時間: {{{{ TOTAL_TIME }}}}秒 (後で置換)

    4. **プロンプト開示セクション (必須)**:
       `<details>` タグを使い、折りたたみで以下のプロンプトを表示してください。
       - 「要約AIプロンプト」: {{{{ SUMMARY_PROMPT }}}}
       - 「デザインAIプロンプト」: {{{{ DESIGN_PROMPT }}}}

    5. 出力はHTMLのみ。`<!DOCTYPE html>` から開始。
    
    【ニュースデータ】
    {json.dumps({k: v for k, v in news_data.items() if k != 'meta'}, ensure_ascii=False)}
    """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(design_prompt)
    design_gen_time = time.time() - design_start
    
    clean_html = response.text.replace("```html", "").replace("```", "").strip()

    # トークン情報
    design_tokens = {
        'input': response.usage_metadata.prompt_token_count,
        'output': response.usage_metadata.candidates_token_count,
        'total': response.usage_metadata.total_token_count
    }
    
    total_summary_tokens = news_data['meta']['summary_tokens']['total']
    total_all_tokens = total_summary_tokens + design_tokens['total']
    total_time = news_data['meta']['total_fetch_time_sec'] + design_gen_time
    
    # プレースホルダー置換
    final_html = clean_html
    final_html = final_html.replace("{{ DESIGN_TOKENS }}", f"入力={design_tokens['input']}, 出力={design_tokens['output']}, 合計={design_tokens['total']}")
    final_html = final_html.replace("{{DESIGN_TOKENS}}", f"入力={design_tokens['input']}, 出力={design_tokens['output']}, 合計={design_tokens['total']}")
    final_html = final_html.replace("{{ DESIGN_TIME }}", f"{round(design_gen_time, 2)}")
    final_html = final_html.replace("{{DESIGN_TIME}}", f"{round(design_gen_time, 2)}")
    final_html = final_html.replace("{{ TOTAL_TIME }}", f"{round(total_time, 2)}")
    final_html = final_html.replace("{{TOTAL_TIME}}", f"{round(total_time, 2)}")
    
    # プロンプト置換（HTMLエスケープ）
    import html
    escaped_summary_prompt = html.escape(news_data['meta']['summary_prompt'])
    escaped_design_prompt = html.escape(design_prompt)
    final_html = final_html.replace("{{ SUMMARY_PROMPT }}", escaped_summary_prompt)
    final_html = final_html.replace("{{SUMMARY_PROMPT}}", escaped_summary_prompt)
    final_html = final_html.replace("{{ DESIGN_PROMPT }}", escaped_design_prompt)
    final_html = final_html.replace("{{DESIGN_PROMPT}}", escaped_design_prompt)
    
    # メタデータにデザイン情報を追加
    news_data['meta']['design_prompt'] = design_prompt.strip()
    news_data['meta']['design_tokens'] = design_tokens
    news_data['meta']['design_generation_time_sec'] = round(design_gen_time, 2)
    news_data['meta']['total_tokens'] = total_all_tokens
    news_data['meta']['total_processing_time_sec'] = round(total_time, 2)
    
    # JSONデータを更新
    json_path = os.path.join(DATA_DIR, f"{current_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    
    return final_html, news_data

# --- 3. 履歴一覧ページ生成 ---
def generate_history_page(history):
    """履歴一覧HTMLを生成"""
    print("Step 3: Generating history page...")
    
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

# --- メイン処理 ---
if __name__ == "__main__":
    if not API_KEY:
        print("Error: OPENAI_API_KEY not found.")
        exit(1)

    try:
        # 実行IDとして「年月日時分」を使用 (例: 2026-01-08_0930)
        timestamp_id = datetime.now(JST).strftime('%Y-%m-%d_%H%M')
        
        # 1. 履歴のロードと前のリンク取得
        history = load_history()
        prev_link = get_prev_link(timestamp_id, history)
        
        # 2. ニュース取得
        daily_content = fetch_and_summarize_news(timestamp_id)
        
        # 3. HTML生成
        new_html, updated_content = evolve_ui(daily_content, prev_link, history)
        
        # 4. 保存処理
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        # A. アーカイブ保存 (ユニークなファイル名)
        archive_filename = f"{timestamp_id}.html"
        archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(new_html)
            
        # B. index.html をリダイレクト用に更新
        index_path = os.path.join(PUBLIC_DIR, "index.html")
        redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting to MorphoNews...</title>
    <meta http-equiv="refresh" content="0; url=./archives/{archive_filename}">
    <style>body{{background:#0a0a0f;color:#6366f1;font-family:system-ui;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;flex-direction:column;gap:1rem;}}</style>
</head>
<body>
    <p>🦋 Loading MorphoNews ({timestamp_id})...</p>
    <p><a href="./archives/{archive_filename}" style="color:#8b5cf6;">Click here if not redirected.</a></p>
</body>
</html>"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(redirect_html)

        # C. 履歴リスト更新（詳細データ含む）
        entry_data = {
            'id': timestamp_id,
            'fetch_time_jst': updated_content['meta']['fetch_time_jst'],
            'mood_keyword': updated_content.get('mood_keyword', 'Unknown'),
            'daily_summary': updated_content.get('daily_summary', ''),
            'model_name': updated_content['meta']['model_name'],
            'total_tokens': updated_content['meta']['total_tokens'],
            'total_processing_time_sec': updated_content['meta']['total_processing_time_sec']
        }
        history = add_history_entry(history, entry_data)
        save_history(history)
        
        # D. 履歴一覧ページ生成
        generate_history_page(history)
            
        print(f"Success! Archived to {archive_path} (ID: {timestamp_id})")
        print(f"Total tokens used: {updated_content['meta']['total_tokens']}")
        print(f"Total processing time: {updated_content['meta']['total_processing_time_sec']}s")

    except Exception as e:
        import traceback
        print(f"Fatal Error: {e}")
        traceback.print_exc()
        exit(1)
