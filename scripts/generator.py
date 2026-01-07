import os
import json
import shutil
import feedparser
import google.generativeai as genai
from datetime import datetime

# --- 設定 ---
API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    # 開発環境などでキーがない場合の安全策（Github ActionsではSecrets必須）
    pass 

# Geminiの設定
if API_KEY:
    genai.configure(api_key=API_KEY)
    
MODEL_NAME = "gemini-3-flash-preview"

# ディレクトリ構成
PUBLIC_DIR = "public"
ARCHIVE_DIR = os.path.join(PUBLIC_DIR, "archives") # HTML保管場所
DATA_DIR = os.path.join(PUBLIC_DIR, "data")       # JSON保管場所
HISTORY_FILE = os.path.join(PUBLIC_DIR, "history.json")

RSS_FEEDS = [
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "https://qiita.com/popular-items/feed",
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
]

# --- ヘルパー関数: 履歴管理 ---
def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_history(history):
    # 文字列ソートで時系列順を保証
    sorted_history = sorted(list(set(history)))
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted_history, f, indent=2)

def get_prev_link(current_id, history):
    """履歴リストから、今回(current_id)の一つ前のIDを探してリンクを返す"""
    # 念のためソート
    sorted_history = sorted(list(set(history)))
    
    # 今回のIDがまだ履歴に含まれていない場合を考慮して、今回より小さい最大のIDを探す
    past_ids = [hid for hid in sorted_history if hid < current_id]
    
    if past_ids:
        prev_id = past_ids[-1]
        return f"./{prev_id}.html"
    
    return "#"

# --- 1. ニュース収集 (編集者AI) ---
def fetch_and_summarize_news(timestamp_id):
    print("Step 1: Fetching news...")
    start_time = datetime.now()
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

    prompt = f"""
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
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config={"response_mime_type": "application/json"}
    )
    response = model.generate_content(prompt)
    content_json = json.loads(response.text)
    
    # メタデータ (IDとしてtimestamp_idを使用)
    content_json['meta'] = {
        'id': timestamp_id,
        'display_date': start_time.strftime('%Y-%m-%d %H:%M'), # 表示用日時
        'fetch_time': start_time.strftime('%Y-%m-%d %H:%M:%S JST'),
        'sources': source_urls,
        'summary_tokens': response.usage_metadata.total_token_count,
        'article_count': len(articles)
    }
    
    # JSONデータの保存
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, f"{timestamp_id}.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(content_json, f, ensure_ascii=False, indent=2)
        
    return content_json

# --- 2. デザイン生成 (デザイナーAI) ---
def evolve_ui(news_data, prev_link):
    current_id = news_data['meta']['id']
    display_date = news_data['meta']['display_date']
    print(f"Step 2: Evolving UI for {current_id}...")
    
    # 最新のアーカイブがあれば参考にする（なければ空）
    # historyから最新を取得してもいいが、単純にアーカイブフォルダの最新ファイルを探す
    reference_html = ""
    try:
        archives = sorted(os.listdir(ARCHIVE_DIR))
        if archives:
            latest_archive = archives[-1]
            with open(os.path.join(ARCHIVE_DIR, latest_archive), "r", encoding="utf-8") as f:
                reference_html = f.read()
    except:
        pass

    # 参考HTMLが長すぎるとトークンを圧迫するので、冒頭部分だけ渡すなどの工夫も可
    # ここではそのまま渡す
    
    design_prompt = f"""
    あなたは前衛的Webデザイナーです。MorphoNewsのHTMLを作成します。
    
    【指令】
    1. 以前のデザイン（HTML構造）を参考にしつつ、
       ムード「{news_data['mood_keyword']}」に合わせて、
       **配色・フォント・レイアウトを大胆に変異**させてください。
    
    2. **ナビゲーションバーの実装 (必須)**:
       ページ上部または下部にナビゲーションを作ってください。
       - [<< Prev Update] ボタン: リンク先 "{prev_link}" (prev_linkが "#" なら非表示か無効化)
       - [Archive List] ボタン: リンク先 "../history.json"
       - 現在の日時表示: {display_date}

    3. **システム情報の表示**:
       フッターに生成統計を表示。
       - デザインAIトークン: {{ DESIGN_TOTAL_TOKENS }}

    4. 出力はHTMLのみ。
    
    【ニュースデータ】
    {json.dumps(news_data, ensure_ascii=False)}
    """

    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(design_prompt)
    
    clean_html = response.text.replace("```html", "").replace("```", "").strip()

    # トークン置換
    design_tokens = response.usage_metadata.total_token_count
    total = news_data['meta']['summary_tokens'] + design_tokens
    final_html = clean_html.replace("{{ DESIGN_TOTAL_TOKENS }}", f"{design_tokens} (Total: {total})")
    
    return final_html

# --- メイン処理 ---
if __name__ == "__main__":
    if not API_KEY:
        print("Error: OPENAI_API_KEY not found.")
        exit(1)

    try:
        # 実行IDとして「年月日時分」を使用 (例: 2026-01-08_0930)
        timestamp_id = datetime.now().strftime('%Y-%m-%d_%H%M')
        
        # 1. 履歴のロードと前のリンク取得
        history = load_history()
        prev_link = get_prev_link(timestamp_id, history)
        
        # 2. ニュース取得
        daily_content = fetch_and_summarize_news(timestamp_id)
        
        # 3. HTML生成
        new_html = evolve_ui(daily_content, prev_link)
        
        # 4. 保存処理
        os.makedirs(ARCHIVE_DIR, exist_ok=True)
        
        # A. アーカイブ保存 (ユニークなファイル名)
        archive_filename = f"{timestamp_id}.html"
        archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
        with open(archive_path, "w", encoding="utf-8") as f:
            f.write(new_html)
            
        # B. index.html をリダイレクト用に更新
        # 常に「今生成したファイル」へ飛ばす
        index_path = os.path.join(PUBLIC_DIR, "index.html")
        redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting to MorphoNews...</title>
    <meta http-equiv="refresh" content="0; url=./archives/{archive_filename}">
    <style>body{{background:#000;color:#0f0;font-family:monospace;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;}}</style>
</head>
<body>
    <p>Loading MorphoNews ({timestamp_id})...</p>
    <p><a href="./archives/{archive_filename}">Click here if not redirected.</a></p>
</body>
</html>"""
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(redirect_html)

        # C. 履歴リスト更新
        if timestamp_id not in history:
            history.append(timestamp_id)
            save_history(history)
            
        print(f"Success! Archived to {archive_path} (ID: {timestamp_id})")

    except Exception as e:
        print(f"Fatal Error: {e}")
        exit(1)
