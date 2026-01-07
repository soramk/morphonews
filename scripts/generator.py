import os
import json
import feedparser
from openai import OpenAI
from datetime import datetime

# --- 設定 ---
API_KEY = os.environ.get("OPENAI_API_KEY")
CLIENT = OpenAI(api_key=API_KEY)

RSS_FEEDS = [
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "https://qiita.com/popular-items/feed",
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
]

OUTPUT_HTML_PATH = "public/index.html"

# --- 関数: ニュース収集と要約 (編集者AI) ---
def fetch_and_summarize_news():
    print("Step 1: Fetching news...")
    start_time = datetime.now()
    articles = []
    source_urls = []
    
    # 記事取得
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            source_urls.append(url)
            for entry in feed.entries[:2]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get('summary', '')[:200] + "...",
                    "source": feed.feed.get('title', 'Unknown')
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # プロンプト作成
    prompt = f"""
    あなたは優秀なITジャーナリストです。
    以下の記事リストから、特にエンジニアにとって重要・興味深いトピックを選定し、
    **日本語で** Web記事のコンテンツを作成してください。

    【要件】
    1. 記事全体で400文字程度の「今日のテックトレンド要約」を作成する。
    2. 個別の注目ニュースを3つピックアップし、それぞれ3行程度で紹介する。
    3. 結果は **JSON形式** で出力すること。
    
    【入力データ】
    {json.dumps(articles, ensure_ascii=False)}

    【出力フォーマット (JSON)】
    {{
        "daily_summary": "...",
        "top_news": [
            {{ "title": "...", "description": "...", "link": "..." }}
        ],
        "mood_keyword": "Cyberpunk, Minimal, Urgent, Retro, etc."
    }}
    """

    print("Requesting AI summarization...")
    response = CLIENT.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    content_json = json.loads(response.choices[0].message.content)
    
    # メタデータを追加
    content_json['meta'] = {
        'fetch_time': start_time.strftime('%Y-%m-%d %H:%M:%S JST'),
        'sources': source_urls,
        'summary_prompt': prompt,
        'summary_tokens': response.usage.total_tokens, # 要約に使ったトークン数
        'article_count': len(articles)
    }
    
    return content_json

# --- 関数: Webページの進化 (デザイナーAI) ---
def evolve_ui(news_data):
    print("Step 2: Evolving UI/UX...")
    
    current_html = ""
    if os.path.exists(OUTPUT_HTML_PATH):
        with open(OUTPUT_HTML_PATH, "r", encoding="utf-8") as f:
            current_html = f.read()

    # デザイン指示のプロンプト
    design_prompt = f"""
    あなたは前衛的Webデザイナーです。「MorphoNews」のHTMLを作成します。
    
    【コンテンツデータ】
    {json.dumps(news_data, ensure_ascii=False)}

    【デザイン要件】
    1. 前回 ({datetime.now().strftime('%Y-%m-%d')}) のHTML構造を参考にしつつ、
       今日のムード「{news_data['mood_keyword']}」に合わせて、
       **配色・フォント・レイアウトを大胆に変異**させてください。
    
    2. **システムログセクションの必須表示**:
       ページ下部（フッター付近）に、以下の「生成プロセス情報」を必ず表示エリアを作成してください。
       - 生成日時: {news_data['meta']['fetch_time']}
       - 参照ソース一覧: (リスト表示)
       - 収集記事数: {news_data['meta']['article_count']}
       - 要約AIトークン数: {news_data['meta']['summary_tokens']}
       - デザインAIトークン数: {{ DESIGN_TOTAL_TOKENS }}  <-- ※この文字列をそのまま書いてください。後で置換します。
       
    3. **プロンプトの開示**:
       システムログ内に `<details>` タグを使い、以下のプロンプト全文を表示してください。
       - Summary Prompt: (中身は "CHECK_JSON_DATA" と書いてください)
       - Design Prompt: (中身は "CHECK_PYTHON_SCRIPT" と書いてください)
       ※長すぎるため、ここでは仮置きします。

    4. 出力は `<!DOCTYPE html>` から始まるHTMLのみ。
    """

    response = CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": design_prompt}]
    )

    raw_html = response.choices[0].message.content
    clean_html = raw_html.replace("```html", "").replace("```", "").strip()

    # --- HTML内のプレースホルダーを実際の値に置換 ---
    # 1. デザイン生成にかかったトークン数
    design_tokens = response.usage.total_tokens
    total_cost_tokens = news_data['meta']['summary_tokens'] + design_tokens
    
    final_html = clean_html.replace("{{ DESIGN_TOTAL_TOKENS }}", f"{design_tokens} (Total: {total_cost_tokens})")

    # 2. プロンプトの実流し込み (HTMLエスケープ処理をして安全に埋め込む)
    import html
    safe_summary_prompt = html.escape(news_data['meta']['summary_prompt'])
    safe_design_prompt = html.escape(design_prompt)
    
    final_html = final_html.replace("CHECK_JSON_DATA", safe_summary_prompt)
    final_html = final_html.replace("CHECK_PYTHON_SCRIPT", safe_design_prompt)

    return final_html

# --- メイン実行 ---
if __name__ == "__main__":
    try:
        daily_content = fetch_and_summarize_news()
        new_html = evolve_ui(daily_content)
        
        os.makedirs(os.path.dirname(OUTPUT_HTML_PATH), exist_ok=True)
        with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
            
        print(f"Success! Updated {OUTPUT_HTML_PATH}")

    except Exception as e:
        print(f"Fatal Error: {e}")
        exit(1)
