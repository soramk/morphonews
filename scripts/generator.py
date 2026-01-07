import os
import json
import feedparser
from openai import OpenAI
from datetime import datetime

# --- 設定 ---
# GitHub SecretsからAPIキーを取得
API_KEY = os.environ.get("OPENAI_API_KEY")
CLIENT = OpenAI(api_key=API_KEY)

# ニュースソース (RSS URL)
# 日本と海外のテックニュースをミックス
RSS_FEEDS = [
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml", # ITmedia (JP)
    "https://qiita.com/popular-items/feed",              # Qiita (JP)
    "https://techcrunch.com/feed/",                      # TechCrunch (Global)
    "https://feeds.feedburner.com/TheHackersNews",       # The Hacker News (Global/Security)
]

# 生成ファイルのパス
OUTPUT_HTML_PATH = "public/index.html" # GitHub Pagesの公開ディレクトリに合わせて調整
ARCHIVE_JSON_PATH = "public/news_archive.json"

# --- 関数: ニュース収集と要約 (編集者AI) ---
def fetch_and_summarize_news():
    print("Step 1: Fetching news from RSS...")
    articles = []
    
    # 各RSSから最新記事を取得（合計で最大8件程度に絞る）
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            # 各フィードから上位2件だけ抽出
            for entry in feed.entries[:2]:
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "summary": entry.get('summary', '')[:200] + "...", # 長すぎる場合はカット
                    "source": feed.feed.get('title', 'Unknown Source')
                })
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    print(f"Fetched {len(articles)} articles. Starting AI summarization...")

    # AIへの指示: 記事リストを渡して、日本語のダイジェストを作成させる
    prompt = f"""
    あなたは優秀なITジャーナリストです。
    以下の記事リストから、特にエンジニアにとって重要・興味深いトピックを選定し、
    **日本語で** Web記事のコンテンツを作成してください。

    【要件】
    1. 記事全体で400文字程度の「今日のテックトレンド要約」を作成する。
    2. その後、個別の注目ニュースを3つピックアップし、それぞれ3行程度で紹介する。
    3. 日本のエンジニアが読みやすい文体（「だ・である」調、または「です・ます」調、お任せします）。
    4. 結果は **JSON形式** で出力すること。
    
    【入力データ】
    {json.dumps(articles, ensure_ascii=False)}

    【出力フォーマット (JSON)】
    {{
        "daily_summary": "400文字程度の全体のまとめ...",
        "top_news": [
            {{ "title": "記事1タイトル", "description": "要約...", "link": "URL" }},
            {{ "title": "記事2タイトル", "description": "要約...", "link": "URL" }},
            {{ "title": "記事3タイトル", "description": "要約...", "link": "URL" }}
        ],
        "mood_keyword": "今日のニュースの雰囲気を表す英単語1つ (例: Cyberpunk, Minimal, Urgent, Happy)"
    }}
    """

    response = CLIENT.chat.completions.create(
        model="gpt-4o", # 賢いモデル推奨
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    content_json = json.loads(response.choices[0].message.content)
    print("Summarization complete.")
    return content_json

# --- 関数: Webページの進化 (デザイナーAI) ---
def evolve_ui(news_data):
    print("Step 2: Evolving UI/UX...")
    
    # 前回のHTMLを読み込む（存在しなければ空）
    current_html = ""
    if os.path.exists(OUTPUT_HTML_PATH):
        with open(OUTPUT_HTML_PATH, "r", encoding="utf-8") as f:
            current_html = f.read()
    else:
        current_html = "(No previous HTML found. Create a new one from scratch.)"

    # 今日の日付
    today_str = datetime.now().strftime('%Y-%m-%d')

    # AIへの指示: 前回のコードと今回のニュースを元に、新しいHTMLを生成
    design_prompt = f"""
    あなたは世界最高の前衛的Webデザイナー兼エンジニアです。
    「MorphoNews」という、毎日デザインが進化・変異するニュースサイトのコーディングを担当します。

    【任務】
    前回（昨日）のHTMLコードを解析し、それを **「破壊的かつ創造的」にリファクタリング** して、
    今日のニュースを表示する新しい `index.html` を作成してください。

    【ニュースデータ】
    - 日付: {today_str}
    - 全体要約: {news_data['daily_summary']}
    - ピックアップ記事: {json.dumps(news_data['top_news'], ensure_ascii=False)}
    - 今日のムード: {news_data['mood_keyword']}

    【デザイン・進化の指針】
    1. **UI/UXの改善**: 前回のHTMLを見て、可読性が悪い箇所があれば修正する。
    2. **ムード反映**: 「今日のムード」キーワード ({news_data['mood_keyword']}) を元に、配色(CSS)やフォント、レイアウトを大胆に変更する。
    3. **構造の変化**: 単なる色変えだけでなく、グリッドレイアウト、リスト表示、カード型など、HTML構造自体を変えてみる。
    4. **必須要素**: ニュースの内容は必ず全て表示すること。
    5. **1ファイル完結**: HTMLの中にCSS (<style>) と JS (<script>) を埋め込むこと。外部ファイル読み込みは禁止（CDNはOK）。
    
    【前回のHTML】
    {current_html[:4000]} ... (省略) ...

    【出力】
    解説は不要です。 `<!DOCTYPE html>` から始まる完全なHTMLコードのみを出力してください。
    """

    response = CLIENT.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": design_prompt}]
    )

    # Markdownのコードブロック記号を除去
    raw_html = response.choices[0].message.content
    clean_html = raw_html.replace("```html", "").replace("```", "").strip()
    
    return clean_html

# --- メイン実行 ---
if __name__ == "__main__":
    try:
        # 1. ニュースを取得・加工
        daily_content = fetch_and_summarize_news()
        
        # 2. UIを進化させてHTML生成
        new_html = evolve_ui(daily_content)
        
        # 3. ファイル書き出し
        # ディレクトリ作成
        os.makedirs(os.path.dirname(OUTPUT_HTML_PATH), exist_ok=True)
        
        with open(OUTPUT_HTML_PATH, "w", encoding="utf-8") as f:
            f.write(new_html)
            
        print(f"Successfully evolved MorphoNews! Saved to {OUTPUT_HTML_PATH}")

    except Exception as e:
        print(f"Fatal Error: {e}")
        exit(1)
