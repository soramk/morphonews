import os
import json
import shutil
import html as html_module
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
    
MODEL_NAME = "gemini-3-flash-preview"

# 生成モード設定: 'modular' (テンプレートベース) または 'ai' (AI生成HTML)
# モジュラー構造を使用する場合は 'modular' に設定
GENERATION_MODE = os.environ.get("GENERATION_MODE", "modular")  # デフォルトはmodular

# ディレクトリ構成
PUBLIC_DIR = "public"
ARCHIVE_DIR = os.path.join(PUBLIC_DIR, "archives") # HTML保管場所
DATA_DIR = os.path.join(PUBLIC_DIR, "data")       # JSON保管場所
HISTORY_FILE = os.path.join(PUBLIC_DIR, "history.json")

# JST タイムゾーン
JST = timezone(timedelta(hours=9))

# RSSフィードリスト（日本・海外の主要テック/ITニュースソース）
RSS_FEEDS = [
    # --- 日本のテック/ITニュース ---
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",      # ITmedia NEWS
    "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",           # ITmedia AI+
    "https://qiita.com/popular-items/feed",                    # Qiita 人気記事
    "https://zenn.dev/feed",                                   # Zenn
    "https://gigazine.net/news/rss_2.0/",                      # GIGAZINE
    "https://www.publickey1.jp/atom.xml",                      # Publickey
    "https://gihyo.jp/feed/rss2",                              # gihyo.jp
    "https://jp.techcrunch.com/feed/",                         # TechCrunch Japan
    "https://codezine.jp/rss/new/20/index.xml",               # CodeZine
    "https://www.watch.impress.co.jp/data/rss/1.0/ipw/feed.rdf",  # Impress Watch
    
    # --- 海外のテック/ITニュース ---
    "https://techcrunch.com/feed/",                            # TechCrunch
    "https://feeds.feedburner.com/TheHackersNews",             # The Hacker News
    "https://www.theverge.com/rss/index.xml",                  # The Verge
    "https://feeds.arstechnica.com/arstechnica/index",         # Ars Technica
    "https://www.wired.com/feed/rss",                          # WIRED
    "https://feeds.feedburner.com/TechCrunch/",                # TechCrunch (backup)
    "https://rss.slashdot.org/Slashdot/slashdotMain",          # Slashdot
    "https://hnrss.org/frontpage",                             # Hacker News
    "https://www.engadget.com/rss.xml",                        # Engadget
    "https://feeds.feedburner.com/venturebeat/SZYF",           # VentureBeat
    "https://www.zdnet.com/news/rss.xml",                      # ZDNet
    "https://www.infoworld.com/index.rss",                     # InfoWorld
    
    # --- AI/ML専門 ---
    "https://openai.com/blog/rss/",                            # OpenAI Blog
    "https://blog.google/technology/ai/rss/",                  # Google AI Blog
    "https://ai.meta.com/blog/rss/",                           # Meta AI Blog
]

# 各フィードから取得する最大記事数
ARTICLES_PER_FEED = 3

# AIが選ぶ注目ニュースの数
TOP_NEWS_COUNT = 10

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
            # 各フィードから最新記事を取得
            for entry in feed.entries[:ARTICLES_PER_FEED]:
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
    1. 「今日のテックトレンド要約」(600文字程度)を作成。
    2. 注目ニュース{TOP_NEWS_COUNT}選をピックアップ。重複や類似トピックは避け、多様な分野をカバー。
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

# --- 2a. モジュラー構造でHTML生成 (テンプレートベース) ---
def generate_archive_html_modular(news_data, current_id, prev_link, display_date, generation_count):
    """モジュラー構造でアーカイブHTMLを生成（セキュアなアプローチ）"""
    
    # テンプレートを読み込み
    template_path = os.path.join('public', 'archives', 'TEMPLATE.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # プレースホルダーを置換
    html = html_template
    html = html.replace('{MOOD_KEYWORD}', html_module.escape(news_data['mood_keyword']))
    html = html.replace('{GENERATION_NUMBER}', str(generation_count))
    html = html.replace('{DISPLAY_DATE}', html_module.escape(display_date))
    
    # Previous article link handling with safe ID validation
    if prev_link and prev_link != '#':
        prev_id = prev_link.split('/')[-1].replace('.html', '')
        # Validate prev_id contains only safe characters (YYYY-MM-DD_HHMM format)
        # This should be alphanumeric, hyphens, and underscores only
        if prev_id.replace('-', '').replace('_', '').isalnum():
            prev_link_html = f'''<a href="./{prev_id}.html" class="nav-link">
                <i data-lucide="chevron-left" style="width: 18px; height: 18px;"></i>
                Prev
            </a>'''
        else:
            # Invalid ID format - skip previous link
            prev_link_html = ''
    else:
        prev_link_html = ''  # First article, no previous link
    html = html.replace('{PREV_ARTICLE_LINK}', prev_link_html)
    
    html = html.replace('{FETCH_TIME_JST}', html_module.escape(news_data['meta']['fetch_time_jst']))
    html = html.replace('{ARTICLE_COUNT}', str(news_data['meta']['article_count']))
    html = html.replace('{MODEL_NAME}', html_module.escape(news_data['meta']['model_name']))
    html = html.replace('{DAILY_SUMMARY}', html_module.escape(news_data['daily_summary']))
    
    # ARTICLE_IDを埋め込み（fetch()でJSONを読み込むため）
    # current_id should also be validated as it's used in JavaScript
    if current_id.replace('-', '').replace('_', '').isalnum():
        html = html.replace('{ARTICLE_ID}', current_id)
    else:
        raise ValueError(f"Invalid article ID format: {current_id}")
    
    # トークン情報
    html = html.replace('{SUMMARY_INPUT_TOKENS}', str(news_data['meta']['summary_tokens']['input']))
    html = html.replace('{SUMMARY_OUTPUT_TOKENS}', str(news_data['meta']['summary_tokens']['output']))
    html = html.replace('{SUMMARY_TOTAL_TOKENS}', str(news_data['meta']['summary_tokens']['total']))
    html = html.replace('{SUMMARY_TIME}', str(news_data['meta']['summary_generation_time_sec']))
    
    # デザイン情報（デフォルト値） - extract for readability
    design_tokens = news_data['meta'].get('design_tokens', {})
    design_total_tokens = design_tokens.get('total', 'N/A') if design_tokens else 'N/A'
    design_time = news_data['meta'].get('design_generation_time_sec', 0)
    total_processing_time = news_data['meta'].get('total_processing_time_sec', 0)
    
    html = html.replace('{DESIGN_TOTAL_TOKENS}', str(design_total_tokens))
    html = html.replace('{DESIGN_TIME}', str(design_time))
    html = html.replace('{TOTAL_PROCESSING_TIME}', str(total_processing_time))
    
    # プロンプトをエスケープして埋め込み
    html = html.replace('{SUMMARY_PROMPT}', html_module.escape(news_data['meta']['summary_prompt']))
    default_design_prompt = 'Template-based generation (no design AI prompt)'
    html = html.replace('{DESIGN_PROMPT}', html_module.escape(news_data['meta'].get('design_prompt', default_design_prompt)))
    
    # 注意: JSONデータはdata/{current_id}.jsonに保存されており、
    # テンプレート内のfetch()で読み込まれます
    
    return html

# --- 2b. HTML生成の統合関数 (モード切り替え) ---
def generate_archive_page(news_data, prev_link, history):
    """
    アーカイブページを生成（モードに応じて切り替え）
    
    Returns:
        tuple: (html_string, updated_news_data)
    """
    current_id = news_data['meta']['id']
    display_date = news_data['meta']['display_date']
    generation_count = len(history.get('entries', [])) + 1
    
    if GENERATION_MODE == "modular":
        print(f"Step 2: Generating archive page using modular template for {current_id}...")
        
        # モジュラー構造でHTML生成（処理時間を記録）
        start_time = time.time()
        html_output = generate_archive_html_modular(
            news_data, 
            current_id, 
            prev_link, 
            display_date, 
            generation_count
        )
        processing_time = time.time() - start_time
        
        # メタデータを更新（デザイン生成はテンプレートベースなのでトークン使用なし）
        news_data['meta']['design_prompt'] = 'Template-based generation (modular structure)'
        news_data['meta']['design_tokens'] = {'input': 0, 'output': 0, 'total': 0}
        news_data['meta']['design_generation_time_sec'] = round(processing_time, 2)
        news_data['meta']['total_tokens'] = news_data['meta']['summary_tokens']['total']
        # Total processing time should include summary generation time + template processing time
        news_data['meta']['total_processing_time_sec'] = round(
            news_data['meta']['summary_generation_time_sec'] + processing_time, 2
        )
        
        # JSONデータを更新
        json_path = os.path.join(DATA_DIR, f"{current_id}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(news_data, f, ensure_ascii=False, indent=2)
        
        print(f"  ✓ Modular template applied in {processing_time:.2f}s")
        return html_output, news_data
    
    else:
        # AI-based generation (existing evolve_ui function)
        return evolve_ui_ai(news_data, prev_link, history)

# --- 2c. デザイン生成 (デザイナーAI) ---
def evolve_ui_ai(news_data, prev_link, history):
    """AI-based UI evolution (original evolve_ui function)"""
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
    
    # 進化の世代数を計算
    generation_count = len(history.get('entries', [])) + 1
    
    design_prompt = f"""
    あなたは世界最高の前衛的Webデザイナー兼UIリサーチャーです。
    MorphoNewsは「自己進化するWebページ」をコンセプトとした実験プロジェクトです。
    あなたの役割は、毎回のデザインでWebデザインの新しい可能性を探求し、進化を続けることです。
    
    ===== 🧬 進化のコンテキスト =====
    
    【現在の世代】Generation #{generation_count}
    【今日のムード】{news_data['mood_keyword']}
    【これまでのアーカイブ数】{len(history.get('entries', []))}件
    
    【前回のデザイン参考（先頭5000文字）】
    ```html
    {reference_html if reference_html else '（初回生成のため参考なし）'}
    ```
    
    ===== 🎯 進化の指令 =====
    
    【1. 前回からの進化（最重要）】
    前回のデザインを分析し、以下の観点から**明確に異なる**アプローチを取ってください：
    
    - **レイアウト構造**: 前回と異なるグリッド/フレックス構成を試す
      （例：1カラム→2カラム、カード型→リスト型、縦スクロール→横スクロールセクション）
    
    - **タイポグラフィ**: 異なるフォントファミリーや文字サイズの比率を実験
      （Google Fontsから: Inter, Outfit, Poppins, Space Grotesk, Plus Jakarta Sans など）
    
    - **ビジュアル表現**: 新しいCSS技法を1つ以上取り入れる
      （グラスモーフィズム、ニューモーフィズム、グラデーションメッシュ、SVGパターン、
       CSS Grid の subgrid、container queries、scroll-driven animations など）
    
    - **マイクロインタラクション**: 前回と異なるホバー効果やトランジション
    
    【2. デザインの方向性】
    **明るいライトモードのデザイン**を基本としつつ、今日のムード「{news_data['mood_keyword']}」を反映：
    - 背景: 白 (#ffffff) または明るいグレー (#f8fafc, #f1f5f9) を基調
    - テキスト: 濃いグレー (#1e293b, #334155) で高い可読性
    - アクセント: ムードに合わせた配色（基本はインディゴ〜パープル系）
    - 余白とリズム: 心地よい視覚的リズムを意識
    
    【3. 必須コンポーネント】
    
    A) ナビゲーションバー:
       - [<< Prev Update] ボタン → リンク先 "{prev_link}" (prev_linkが "#" なら非表示/無効化)
       - [Archive List] ボタン → リンク先 "../history.html"
       - 現在の日時表示: {display_date} (JST)
       - 世代表示: 「Generation #{generation_count}」をどこかに

    B) メインコンテンツ:
       - 今日のトレンド要約を魅力的に表示
       - 注目ニュース{TOP_NEWS_COUNT}件をカード/リスト/タイムラインなど自由な形式で
       - 各ニュースのリンクは必ずクリック可能に

    C) システム情報フッター:
       - 取得日時(JST): {news_data['meta']['fetch_time_jst']}
       - 収集記事数: {news_data['meta']['article_count']}
       - 使用モデル: {news_data['meta']['model_name']}
       - 要約AIトークン: 入力={news_data['meta']['summary_tokens']['input']}, 出力={news_data['meta']['summary_tokens']['output']}, 合計={news_data['meta']['summary_tokens']['total']}
       - 要約生成時間: {news_data['meta']['summary_generation_time_sec']}秒
       - デザインAIトークン: {{{{ DESIGN_TOKENS }}}} (後で置換)
       - デザイン生成時間: {{{{ DESIGN_TIME }}}}秒 (後で置換)
       - 全体処理時間: {{{{ TOTAL_TIME }}}}秒 (後で置換)

    D) プロンプト開示セクション:
       `<details>` タグで折りたたみ表示：
       - 「要約AIプロンプト」: {{{{ SUMMARY_PROMPT }}}}
       - 「デザインAIプロンプト」: {{{{ DESIGN_PROMPT }}}}

    E) 進化ログセクション（推奨）:
       今回のデザインで試した新しいアプローチを簡潔に記述
       （例：「今回の実験: CSS Grid subgrid + グラスモーフィズムカード」）

    【4. 出力形式】
    - HTMLのみを出力。`<!DOCTYPE html>` から開始
    - 外部CSSは使用せず、<style>タグ内に全て記述
    - 外部JSライブラリは最小限に（アイコンにLucideを使う場合のみ許可）
    
    ===== 📰 ニュースデータ =====
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
    escaped_summary_prompt = html_module.escape(news_data['meta']['summary_prompt'])
    escaped_design_prompt = html_module.escape(design_prompt)
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

# Backward compatibility: keep old function name
def evolve_ui(news_data, prev_link, history):
    """Wrapper for backward compatibility - delegates to generate_archive_page"""
    return generate_archive_page(news_data, prev_link, history)

# --- 3. 履歴一覧ページ生成 ---
def generate_history_page(history):
    """履歴一覧HTMLを生成（ライトモード・Lucideアイコン使用）"""
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
                    <time class="card-date">
                        <i data-lucide="clock" style="width: 14px; height: 14px;"></i>
                        {fetch_time}
                    </time>
                    <span class="card-mood">{mood}</span>
                </div>
                <p class="card-summary">{summary}</p>
                <div class="card-meta">
                    <span class="meta-item">
                        <i data-lucide="cpu" style="width: 14px; height: 14px;"></i>
                        {model}
                    </span>
                    <span class="meta-item">
                        <i data-lucide="hash" style="width: 14px; height: 14px;"></i>
                        {tokens} tokens
                    </span>
                </div>
                <div class="card-actions">
                    <a href="./archives/{entry['id']}.html" class="btn-view">
                        <i data-lucide="newspaper" style="width: 16px; height: 16px;"></i>
                        記事を見る
                    </a>
                    <a href="./data/{entry['id']}.json" class="btn-data">
                        <i data-lucide="file-json" style="width: 16px; height: 16px;"></i>
                        JSONデータ
                    </a>
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
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {{
            --bg-primary: #f8fafc;
            --bg-secondary: #ffffff;
            --bg-card: #ffffff;
            --text-primary: #1e293b;
            --text-secondary: #64748b;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
            --border-color: #e2e8f0;
            --success: #22c55e;
            --warning: #f59e0b;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
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

        body::before {{
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: 
                radial-gradient(circle at 20% 20%, rgba(99, 102, 241, 0.03) 0%, transparent 50%),
                radial-gradient(circle at 80% 80%, rgba(139, 92, 246, 0.03) 0%, transparent 50%);
            pointer-events: none;
            z-index: -1;
        }}

        header {{
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border-color);
            padding: 1.5rem 2rem;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: var(--shadow-sm);
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
            border-radius: 10px;
            overflow: hidden;
        }}

        .logo-icon img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}

        .logo h1 {{
            font-size: 1.5rem;
            font-weight: 700;
            background: var(--accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}

        .logo span {{
            font-size: 0.8rem;
            color: var(--text-secondary);
            display: block;
        }}

        nav {{
            display: flex;
            gap: 0.5rem;
        }}

        nav a {{
            color: var(--text-secondary);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: 8px;
            transition: all 0.2s ease;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        nav a:hover {{
            background: var(--bg-primary);
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

        .page-title {{
            text-align: center;
            margin-bottom: 2rem;
        }}

        .page-title h2 {{
            font-size: 2rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 0.5rem;
        }}

        .page-title p {{
            color: var(--text-secondary);
            font-size: 1rem;
        }}

        .stats-bar {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}

        .stat-card {{
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }}

        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }}

        .stat-icon {{
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.75rem;
            color: var(--accent-primary);
        }}

        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
        }}

        .stat-label {{
            font-size: 0.8rem;
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
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
            box-shadow: var(--shadow-sm);
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
            transition: opacity 0.2s ease;
        }}

        .history-card:hover {{
            transform: translateY(-4px);
            border-color: var(--accent-primary);
            box-shadow: var(--shadow-lg);
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
            font-size: 0.85rem;
            color: var(--text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
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
            gap: 0.35rem;
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
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
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
            background: var(--bg-primary);
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
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }}

        .empty-state {{
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-secondary);
        }}

        .empty-state-icon {{
            width: 80px;
            height: 80px;
            background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1rem;
            color: var(--accent-primary);
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
                <div class="logo-icon">
                    <img src="./assets/icons/icon_butterfly_morphing.png" alt="MorphoNews Logo">
                </div>
                <div>
                    <h1>MorphoNews</h1>
                    <span>Archive Collection</span>
                </div>
            </div>
            <nav>
                <a href="./archives/{sorted_entries[0]['id'] if sorted_entries else ''}.html">
                    <i data-lucide="home" style="width: 18px; height: 18px;"></i>
                    最新版
                </a>
                <a href="./history.html" class="active">
                    <i data-lucide="archive" style="width: 18px; height: 18px;"></i>
                    アーカイブ
                </a>
                <a href="./style-gallery.html">
                    <i data-lucide="palette" style="width: 18px; height: 18px;"></i>
                    スタイル
                </a>
            </nav>
        </div>
    </header>

    <main>
        <div class="page-title">
            <h2>ニュースアーカイブ</h2>
            <p>AIが毎日生成したテックニュースの記録</p>
        </div>

        <div class="stats-bar">
            <div class="stat-card">
                <div class="stat-icon">
                    <i data-lucide="layers" style="width: 20px; height: 20px;"></i>
                </div>
                <div class="stat-value">{len(sorted_entries)}</div>
                <div class="stat-label">総アーカイブ数</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i data-lucide="calendar" style="width: 20px; height: 20px;"></i>
                </div>
                <div class="stat-value">{sorted_entries[0]['id'][:10] if sorted_entries else 'N/A'}</div>
                <div class="stat-label">最新更新日</div>
            </div>
            <div class="stat-card">
                <div class="stat-icon">
                    <i data-lucide="flag" style="width: 20px; height: 20px;"></i>
                </div>
                <div class="stat-value">{sorted_entries[-1]['id'][:10] if sorted_entries else 'N/A'}</div>
                <div class="stat-label">初回生成日</div>
            </div>
        </div>

        <section class="history-grid">
            {entries_html if entries_html else '<div class="empty-state"><div class="empty-state-icon"><i data-lucide="inbox" style="width: 40px; height: 40px;"></i></div><p>まだアーカイブがありません</p></div>'}
        </section>
    </main>

    <footer>
        <div class="footer-content">
            <p class="footer-text">
                <i data-lucide="sparkles" style="width: 16px; height: 16px;"></i>
                MorphoNews - AI駆動の自己進化型ニュースサイト
            </p>
        </div>
    </footer>

    <script>
        lucide.createIcons();
    </script>
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
        
        # 3. HTML生成（モード切り替え対応）
        new_html, updated_content = generate_archive_page(daily_content, prev_link, history)
        
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
