import os
import json
import html as html_module
import feedparser
import google.generativeai as genai
from datetime import datetime, timezone, timedelta
import time
import re

# --- 設定 ---
API_KEY = os.environ.get("OPENAI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
    
MODEL_NAME = "gemini-3-flash-preview"

# 生成モード設定: 
# 'ai': AIによる機能・スタイル・レイアウトの個別進化
# 'full-evolve': AIによるHTML全体の再構築（完全自律進化）
# 'modular': 固定テンプレートベース
# 'news-only': ニュースデータの取得のみ
GENERATION_MODE = os.environ.get("GENERATION_MODE", "ai")

# ディレクトリ構成
PUBLIC_DIR = "public"
ARCHIVE_DIR = os.path.join(PUBLIC_DIR, "archives")
DATA_DIR = os.path.join(PUBLIC_DIR, "data")
FEATURES_DIR = os.path.join(PUBLIC_DIR, "features")
STYLES_DIR = os.path.join(PUBLIC_DIR, "styles")
LAYOUTS_DIR = os.path.join(PUBLIC_DIR, "layouts")
HISTORY_FILE = os.path.join(PUBLIC_DIR, "history.json")
FEATURES_FILE = os.path.join(FEATURES_DIR, "features.json")
STYLES_FILE = os.path.join(STYLES_DIR, "styles.json")
LAYOUTS_FILE = os.path.join(LAYOUTS_DIR, "layouts.json")

# JST タイムゾーン
JST = timezone(timedelta(hours=9))

# RSSフィードリスト
RSS_FEEDS = [
    # 日本のテック/ITニュース
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml",
    "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
    "https://qiita.com/popular-items/feed",
    "https://zenn.dev/feed",
    "https://gigazine.net/news/rss_2.0/",
    "https://www.publickey1.jp/atom.xml",
    "https://gihyo.jp/feed/rss2",
    "https://jp.techcrunch.com/feed/",
    "https://codezine.jp/rss/new/20/index.xml",
    "https://www.watch.impress.co.jp/data/rss/1.0/ipw/feed.rdf",
    # 海外のテック/ITニュース
    "https://techcrunch.com/feed/",
    "https://feeds.feedburner.com/TheHackersNews",
    "https://www.theverge.com/rss/index.xml",
    "https://feeds.arstechnica.com/arstechnica/index",
    "https://www.wired.com/feed/rss",
    "https://rss.slashdot.org/Slashdot/slashdotMain",
    "https://hnrss.org/frontpage",
    "https://www.engadget.com/rss.xml",
    "https://feeds.feedburner.com/venturebeat/SZYF",
    "https://www.zdnet.com/news/rss.xml",
    # AI/ML専門
    "https://openai.com/blog/rss/",
    "https://blog.google/technology/ai/rss/",
    "https://ai.meta.com/blog/rss/",
]

ARTICLES_PER_FEED = 3
TOP_NEWS_COUNT = 10


# =============================================================================
# ヘルパー関数
# =============================================================================

def load_json(filepath, default=None):
    """JSONファイルを読み込む"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                pass
    return default if default is not None else {}

def save_json(filepath, data):
    """JSONファイルを保存"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history():
    """履歴を読み込む"""
    data = load_json(HISTORY_FILE, {"entries": [], "version": 2})
    if isinstance(data, list):
        return {"entries": [{"id": h} for h in data], "version": 2}
    return data

def save_history(history):
    """履歴を保存"""
    save_json(HISTORY_FILE, history)

def add_history_entry(history, entry_data):
    """履歴にエントリを追加"""
    existing_ids = {e['id'] for e in history['entries']}
    if entry_data['id'] not in existing_ids:
        history['entries'].append(entry_data)
        history['entries'] = sorted(history['entries'], key=lambda x: x['id'])
    return history

def get_prev_link(current_id, history):
    """前のアーカイブリンクを取得"""
    sorted_entries = sorted(history['entries'], key=lambda x: x['id'])
    past_ids = [e['id'] for e in sorted_entries if e['id'] < current_id]
    if past_ids:
        return f"./{past_ids[-1]}.html"
    return "#"

def sanitize_id(text):
    """IDを安全な形式に変換"""
    return re.sub(r'[^a-zA-Z0-9_-]', '_', text.lower())

def get_previous_archive_html(prev_link, max_chars=5000):
    """前回のアーカイブHTMLを読み込む（進化参照用）"""
    if not prev_link or prev_link == '#':
        return None
    
    # prev_linkから実際のファイルパスを構築
    prev_id = prev_link.replace('./', '').replace('.html', '')
    prev_path = os.path.join(ARCHIVE_DIR, f"{prev_id}.html")
    
    if os.path.exists(prev_path):
        try:
            with open(prev_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content[:max_chars]
        except Exception as e:
            print(f"  ⚠ Could not read previous archive: {e}")
            return None
    return None


# =============================================================================
# 1. ニュース収集
# =============================================================================

def fetch_and_summarize_news(timestamp_id):
    """RSSフィードからニュースを取得し、AIで要約"""
    print("Step 1: Fetching news...")
    start_time = datetime.now(JST)
    fetch_start = time.time()
    
    articles = []
    source_urls = []
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            source_urls.append(url)
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
    
    # メタデータ
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
    save_json(json_path, content_json)
        
    return content_json


# =============================================================================
# 2. 機能生成 (AIモード)
# =============================================================================

def load_features():
    """features.jsonを読み込む"""
    return load_json(FEATURES_FILE, {"version": 1, "features": []})

def save_features(features_data):
    """features.jsonを保存"""
    features_data['lastUpdated'] = datetime.now(JST).strftime('%Y-%m-%d')
    save_json(FEATURES_FILE, features_data)

def get_existing_feature_ids():
    """既存の機能IDリストを取得"""
    features = load_features()
    return [f['id'] for f in features.get('features', [])]

def generate_new_feature(mood_keyword, timestamp_id):
    """AIに新しい機能を生成させる"""
    print("Step 2a: Generating new feature...")
    
    existing_ids = get_existing_feature_ids()
    
    feature_prompt = f"""
あなたはWebフロントエンド開発者です。MorphoNewsという進化型ニュースサイトに新しい機能を追加してください。

【プロジェクト概要】
MorphoNewsは「自己進化するWebページ」です。毎回の実行で新しい機能が追加されます。

【今日のムード】{mood_keyword}

【既存の機能】
{json.dumps(existing_ids, ensure_ascii=False)}

【要件】
1. 既存の機能と重複しない、新しいユーザー体験を提供する機能を1つ考案
2. JavaScriptで完結する機能（外部APIは使用しない）
3. 即座に自己実行関数(IIFE)で動作すること
4. CSSは自分でstyleタグとして追加すること

【出力形式】JSON
{{
    "id": "機能ID（英数字とハイフンのみ）",
    "name": "機能名（日本語）",
    "description": "機能の説明（日本語）",
    "category": "ui/accessibility/navigation/analytics/entertainment のいずれか",
    "code": "JavaScriptコード全文（即座実行関数形式）"
}}

コードのみ。説明不要。
"""

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(feature_prompt)
        print(f"  [DEBUG] Feature response received, length: {len(response.text)}")
        
        feature_data = json.loads(response.text)
        
        # 必須キーの確認
        required_keys = ['id', 'name', 'description', 'code']
        missing_keys = [k for k in required_keys if k not in feature_data]
        if missing_keys:
            print(f"  ⚠ Missing keys in response: {missing_keys}")
            print(f"  [DEBUG] Response keys: {list(feature_data.keys())}")
            return None
        
        # IDをサニタイズ
        feature_id = sanitize_id(feature_data['id'])
        
        # 重複チェック
        if feature_id in existing_ids:
            feature_id = f"{feature_id}-{timestamp_id[:10]}"
        
        # JSファイルとして保存
        js_filename = f"{feature_id}.js"
        js_path = os.path.join(FEATURES_DIR, "modules", js_filename)
        os.makedirs(os.path.dirname(js_path), exist_ok=True)
        
        js_content = f"""/**
 * MorphoNews Feature: {feature_data['name']}
 * Generated: {timestamp_id}
 * Description: {feature_data['description']}
 */
{feature_data['code']}
"""
        with open(js_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        # features.jsonに登録
        features = load_features()
        new_feature = {
            "id": feature_id,
            "name": feature_data['name'],
            "description": feature_data['description'],
            "file": f"modules/{js_filename}",
            "enabled": False,
            "required": False,
            "category": feature_data.get('category', 'ui'),
            "addedDate": datetime.now(JST).strftime('%Y-%m-%d'),
            "author": "ai"
        }
        features['features'].append(new_feature)
        save_features(features)
        
        print(f"  ✓ Generated feature: {feature_data['name']} ({feature_id})")
        return {
            **new_feature,
            "prompt": feature_prompt.strip(),
            "tokens": {
                "input": response.usage_metadata.prompt_token_count,
                "output": response.usage_metadata.candidates_token_count,
                "total": response.usage_metadata.total_token_count
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"  ⚠ Feature generation failed (JSON parse error): {e}")
        print(f"  [DEBUG] Raw response: {response.text[:500]}...")
        return None
    except Exception as e:
        import traceback
        print(f"  ⚠ Feature generation failed: {e}")
        traceback.print_exc()
        return None


# =============================================================================
# 3. スタイル生成 (AIモード)
# =============================================================================

def load_styles():
    """styles.jsonを読み込む"""
    return load_json(STYLES_FILE, {"version": 1, "themes": []})

def save_styles(styles_data):
    """styles.jsonを保存"""
    styles_data['lastUpdated'] = datetime.now(JST).strftime('%Y-%m-%d')
    save_json(STYLES_FILE, styles_data)

def get_existing_style_ids():
    """既存のスタイルIDリストを取得"""
    styles = load_styles()
    return [s['id'] for s in styles.get('themes', [])]

def generate_new_style(mood_keyword, timestamp_id):
    """AIに新しいスタイル（テーマ）を生成させる"""
    print("Step 2b: Generating new style...")
    
    existing_ids = get_existing_style_ids()
    
    style_prompt = f"""
あなたはWebデザイナーです。MorphoNewsという進化型ニュースサイトに新しいカラーテーマを作成してください。

【今日のムード】{mood_keyword}

【既存のテーマ】
{json.dumps(existing_ids, ensure_ascii=False)}

【要件】
1. 今日のムードを反映した、新しいカラーテーマを作成
2. 既存のテーマと明確に異なる配色
3. CSS Variablesを使用（:root内で定義）
4. 可読性を確保（コントラスト比に注意）

【必須CSS Variables】
--morpho-bg-primary: 背景色（メイン）
--morpho-bg-secondary: 背景色（サブ）
--morpho-bg-card: カード背景色
--morpho-text-primary: テキスト色（メイン）
--morpho-text-secondary: テキスト色（サブ）
--morpho-accent-primary: アクセント色（メイン）
--morpho-accent-secondary: アクセント色（サブ）
--morpho-border-color: ボーダー色
--morpho-accent-gradient: グラデーション

【出力形式】JSON
{{
    "id": "テーマID（英数字とハイフンのみ）",
    "name": "テーマ名（日本語）",
    "description": "テーマの説明（日本語）",
    "preview": {{
        "primary": "#hex色",
        "secondary": "#hex色",
        "background": "#hex色",
        "text": "#hex色"
    }},
    "css": "CSSコード全文（:root {{ ... }} 形式）"
}}

CSSのみ。説明不要。
"""

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(style_prompt)
        print(f"  [DEBUG] Style response received, length: {len(response.text)}")
        
        style_data = json.loads(response.text)
        
        # 必須キーの確認
        required_keys = ['id', 'name', 'description', 'css']
        missing_keys = [k for k in required_keys if k not in style_data]
        if missing_keys:
            print(f"  ⚠ Missing keys in response: {missing_keys}")
            print(f"  [DEBUG] Response keys: {list(style_data.keys())}")
            return None
        
        # IDをサニタイズ
        style_id = sanitize_id(style_data['id'])
        
        # 重複チェック
        if style_id in existing_ids:
            style_id = f"{style_id}-{timestamp_id[:10]}"
        
        # CSSファイルとして保存
        css_filename = f"{style_id}.css"
        css_path = os.path.join(STYLES_DIR, "themes", css_filename)
        os.makedirs(os.path.dirname(css_path), exist_ok=True)
        
        css_content = f"""/**
 * MorphoNews Theme: {style_data['name']}
 * Generated: {timestamp_id}
 * Mood: {mood_keyword}
 * Description: {style_data['description']}
 */
{style_data['css']}
"""
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # styles.jsonに登録
        styles = load_styles()
        new_style = {
            "id": style_id,
            "name": style_data['name'],
            "description": style_data['description'],
            "file": f"themes/{css_filename}",
            "preview": style_data.get('preview', {}),
            "addedDate": datetime.now(JST).strftime('%Y-%m-%d'),
            "author": "ai",
            "mood": mood_keyword
        }
        styles['themes'].append(new_style)
        save_styles(styles)
        
        print(f"  ✓ Generated style: {style_data['name']} ({style_id})")
        return {
            **new_style,
            "prompt": style_prompt.strip(),
            "tokens": {
                "input": response.usage_metadata.prompt_token_count,
                "output": response.usage_metadata.candidates_token_count,
                "total": response.usage_metadata.total_token_count
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"  ⚠ Style generation failed (JSON parse error): {e}")
        print(f"  [DEBUG] Raw response: {response.text[:500]}...")
        return None
    except Exception as e:
        import traceback
        print(f"  ⚠ Style generation failed: {e}")
        traceback.print_exc()
        return None


# =============================================================================
# 3b. レイアウト生成 (AIモード) - ページ構造の自己進化
# =============================================================================

def load_layouts():
    """layouts.jsonを読み込む"""
    return load_json(LAYOUTS_FILE, {"version": 1, "layouts": []})

def save_layouts(layouts_data):
    """layouts.jsonを保存"""
    layouts_data['lastUpdated'] = datetime.now(JST).strftime('%Y-%m-%d')
    save_json(LAYOUTS_FILE, layouts_data)

def get_existing_layout_ids():
    """既存のレイアウトIDリストを取得"""
    layouts = load_layouts()
    return [l['id'] for l in layouts.get('layouts', [])]

def generate_new_layout(mood_keyword, timestamp_id, prev_link=None, generation_count=1):
    """AIに新しいレイアウト（ページ構造）を生成させる - 進化型"""
    print("Step 2c: Generating new layout (enhanced evolution)...")
    
    existing_ids = get_existing_layout_ids()
    layouts = load_layouts()
    
    # 前回のレイアウト情報を取得
    prev_layout_info = ""
    if len(layouts.get('layouts', [])) > 0:
        last_layout = layouts['layouts'][-1]
        last_layout_path = os.path.join(LAYOUTS_DIR, last_layout.get('file', ''))
        if os.path.exists(last_layout_path):
            try:
                with open(last_layout_path, 'r', encoding='utf-8') as f:
                    prev_css = f.read()[:3000]
                prev_layout_info = f"""
【前回のレイアウト参考】
名前: {last_layout.get('name', 'Unknown')}
タイプ: {last_layout.get('preview', {}).get('gridType', 'Unknown')}
```css
{prev_css}
```
"""
            except:
                pass
    
    # 前回のHTMLを取得（進化の参照用）
    prev_html = get_previous_archive_html(prev_link, 3000) if prev_link else None
    prev_html_context = ""
    if prev_html:
        prev_html_context = f"""
【前回のページ構造参考（HTML抜粋）】
```html
{prev_html}
```
"""
    
    layout_prompt = f"""
あなたは世界最高の前衛的Webデザイナー兼UIリサーチャーです。
MorphoNewsは「自己進化するWebページ」をコンセプトとした実験プロジェクトです。
あなたの役割は、毎回のレイアウトでWebデザインの新しい可能性を探求し、進化を続けることです。

===== 🧬 進化のコンテキスト =====

【現在の世代】Generation #{generation_count}
【今日のムード】{mood_keyword}
【これまでのレイアウト数】{len(existing_ids)}件

【既存のレイアウトID】
{json.dumps(existing_ids, ensure_ascii=False)}
{prev_layout_info}
{prev_html_context}

===== 🎯 進化の指令 =====

【1. 前回からの進化（最重要）】
前回のレイアウトを分析し、以下の観点から**明確に異なる**アプローチを取ってください：

- **レイアウト構造**: 前回と異なるグリッド/フレックス構成を試す
  （例：1カラム→2カラム、カード型→タイムライン型、リスト→マソンリー、縦→横スクロール）

- **カード表現**: 前回と異なるカードの形状・比率・情報配置
  （例：横長→縦長、ミニマル→リッチ、ボーダー→シャドウ、角丸→シャープ）

- **アニメーション技法**: 新しいCSS技法を1つ以上取り入れる
  （scroll-driven animations, view transitions, @starting-style, 
   複合transformアニメーション, ステージング効果など）

- **マイクロインタラクション**: 前回と異なるホバー効果やトランジション
  （3D回転, スケール＋シャドウ, ボーダーアニメーション, 疑似要素アニメーションなど）

【2. レイアウトで変更可能な要素】
1. ニュースカードの配置（リスト、グリッド、マソンリー、カルーセル風、タイムライン、新聞風など）
2. カードの形状・サイズ比率・アスペクト比
3. アニメーション効果（フェード、スライド、スケール、回転、バウンス、ステージングなど）
4. ナンバリングバッジのスタイル（円形、四角、リボン風、アイコン、グラデーションなど）
5. ホバーエフェクト（transform、shadow、border、overlay、scaleなど）
6. レスポンシブブレークポイントでの挙動変化
7. スクロール連動アニメーション

【3. CSS変数（必ず定義）】
--layout-max-width: コンテンツ最大幅
--layout-news-columns: グリッド列数
--layout-card-gap: カード間隔
--layout-card-direction: flexbox方向
--layout-animation-style: アニメーション名

【4. 禁止事項】
- 色の直接指定（background-color, color, border-colorの直接値）は禁止
- 代わりにCSS変数を使用（var(--morpho-accent-primary)など）

【5. 進化ログ】
JSONのdescriptionに、今回試した新しいアプローチを記述してください。
（例：「CSS Grid subgrid + ステージングアニメーション + 3Dホバー効果」）

===== 出力形式 =====
JSON形式で出力してください：
{{
    "id": "レイアウトID（英数字とハイフンのみ、ユニークに）",
    "name": "レイアウト名（日本語、創造的に）",
    "description": "今回の進化ポイントを含む説明（日本語）",
    "preview": {{
        "gridType": "list/grid/masonry/carousel/timeline/newspaper",
        "cardStyle": "minimal/bold/compact/expanded/3d/glassmorphism",
        "animation": "slide/fade/scale/bounce/stagger/scroll-driven"
    }},
    "evolution_note": "今回試した新技法（例：scroll-driven animations + view transitions）",
    "css": "CSSコード全文"
}}

創造的で斬新なレイアウトを生成してください。前回との差異を明確にしてください。
"""

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME,
            generation_config={"response_mime_type": "application/json"}
        )
        response = model.generate_content(layout_prompt)
        print(f"  [DEBUG] Layout response received, length: {len(response.text)}")
        
        layout_data = json.loads(response.text)
        
        # 必須キーの確認
        required_keys = ['id', 'name', 'description', 'css']
        missing_keys = [k for k in required_keys if k not in layout_data]
        if missing_keys:
            print(f"  ⚠ Missing keys in response: {missing_keys}")
            print(f"  [DEBUG] Response keys: {list(layout_data.keys())}")
            return None
        
        # IDをサニタイズ
        layout_id = sanitize_id(layout_data['id'])
        
        # 重複チェック
        if layout_id in existing_ids:
            layout_id = f"{layout_id}-{timestamp_id[:10]}"
        
        # CSSファイルとして保存
        css_filename = f"{layout_id}.css"
        css_path = os.path.join(LAYOUTS_DIR, css_filename)
        os.makedirs(LAYOUTS_DIR, exist_ok=True)
        
        evolution_note = layout_data.get('evolution_note', 'N/A')
        css_content = f"""/**
 * MorphoNews Layout: {layout_data['name']}
 * Generated: {timestamp_id}
 * Generation: #{generation_count}
 * Mood: {mood_keyword}
 * Evolution: {evolution_note}
 * Description: {layout_data['description']}
 */
{layout_data['css']}
"""
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # layouts.jsonに登録
        layouts = load_layouts()
        new_layout = {
            "id": layout_id,
            "name": layout_data['name'],
            "description": layout_data['description'],
            "file": css_filename,
            "preview": layout_data.get('preview', {}),
            "evolution_note": evolution_note,
            "addedDate": datetime.now(JST).strftime('%Y-%m-%d'),
            "author": "ai",
            "mood": mood_keyword,
            "generation": generation_count
        }
        layouts['layouts'].append(new_layout)
        save_layouts(layouts)
        
        print(f"  ✓ Generated layout: {layout_data['name']} ({layout_id})")
        print(f"    Evolution: {evolution_note}")
        return {
            **new_layout,
            "prompt": layout_prompt.strip(),
            "tokens": {
                "input": response.usage_metadata.prompt_token_count,
                "output": response.usage_metadata.candidates_token_count,
                "total": response.usage_metadata.total_token_count
            }
        }
        
    except json.JSONDecodeError as e:
        print(f"  ⚠ Layout generation failed (JSON parse error): {e}")
        print(f"  [DEBUG] Raw response: {response.text[:500]}...")
        return None
    except Exception as e:
        import traceback
        print(f"  ⚠ Layout generation failed: {e}")
        traceback.print_exc()
        return None


# =============================================================================
# 3c. HTML全体生成 (full-evolveモード) - 完全自律型進化
# =============================================================================

def generate_full_evolve_html(news_data, current_id, prev_link, generation_count):
    """AIにHTML全体を生成させる - 完全自律型進化モード"""
    print("Step 3: Generating FULL EVOLVE HTML (AI-driven complete redesign)...")
    gen_start = time.time()
    
    # 前回のHTMLを取得
    prev_html = get_previous_archive_html(prev_link, 5000)
    prev_html_context = ""
    if prev_html:
        prev_html_context = f"""
【前回のデザイン参考（先頭5000文字）】
```html
{prev_html}
```
"""
    
    display_date = news_data['meta']['display_date']
    mood_keyword = news_data.get('mood_keyword', 'neutral')
    fetch_time_jst = news_data['meta']['fetch_time_jst']
    article_count = news_data['meta']['article_count']
    model_name = news_data['meta']['model_name']
    summary_tokens = news_data['meta']['summary_tokens']
    summary_time = news_data['meta']['summary_generation_time_sec']
    summary_prompt = news_data['meta']['summary_prompt']
    
    # ニュースデータをJSON形式で
    top_news = news_data.get('top_news', [])
    daily_summary = news_data.get('daily_summary', '')
    
    design_prompt = f"""あなたは世界最高の前衛的Webデザイナー兼UIリサーチャーです。
MorphoNewsは「自己進化するWebページ」をコンセプトとした実験プロジェクトです。
あなたの役割は、毎回のデザインでWebデザインの新しい可能性を探求し、進化を続けることです。

===== 🧬 進化のコンテキスト =====

【現在の世代】Generation #{generation_count}
【今日のムード】{mood_keyword}
【これまでのアーカイブ数】{generation_count - 1}件
{prev_html_context}

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
**明るいライトモードのデザイン**を基本としつつ、今日のムード「{mood_keyword}」を反映：
- 背景: 白 (#ffffff) または明るいグレー (#f8fafc, #f1f5f9) を基調
- テキスト: 濃いグレー (#1e293b, #334155) で高い可読性
- アクセント: ムードに合わせた配色（基本はインディゴ〜パープル系）
- 余白とリズム: 心地よい視覚的リズムを意識

【3. 必須コンポーネント】

A) ナビゲーションバー:
   - [<< Prev Update] ボタン → リンク先 "{prev_link}" (prev_linkが "#" なら非表示/無効化)
   - [Archive List] ボタン → リンク先 "../history.html"
   - [Settings] ボタン → リンク先 "../settings.html"
   - 現在の日時表示: {display_date} (JST)
   - 世代表示: 「Generation #{generation_count}」をどこかに

B) メインコンテンツ:
   - 今日のトレンド要約を魅力的に表示:
     {daily_summary}
   
   - 注目ニュース{len(top_news)}件をカード/リスト/タイムラインなど自由な形式で:
{json.dumps(top_news, ensure_ascii=False, indent=2)}
   
   - 各ニュースのリンクは必ずクリック可能に

C) システム情報フッター:
   - 取得日時(JST): {fetch_time_jst}
   - 収集記事数: {article_count}
   - 使用モデル: {model_name}
   - 要約AIトークン: 入力={summary_tokens.get('input', 0)}, 出力={summary_tokens.get('output', 0)}, 合計={summary_tokens.get('total', 0)}
   - 要約生成時間: {summary_time}秒
   - デザインAIトークン: {{{{ DESIGN_TOKENS }}}} (後で置換)
   - デザイン生成時間: {{{{ DESIGN_TIME }}}}秒 (後で置換)
   - 全体処理時間: {{{{ TOTAL_TIME }}}}秒 (後で置換)

D) プロンプト開示セクション:
   `<details>` タグで折りたたみ表示：
   - 「要約AIプロンプト」: 
   ```
   {summary_prompt[:1000]}...
   ```
   - 「デザインAIプロンプト」: {{{{ DESIGN_PROMPT }}}}

E) 進化ログセクション（推奨）:
   今回のデザインで試した新しいアプローチを簡潔に記述
   （例：「今回の実験: CSS Grid subgrid + グラスモーフィズムカード」）

【4. 出力形式】
- HTMLのみを出力。`<!DOCTYPE html>` から開始
- 外部CSSは使用せず、<style>タグ内に全て記述
- 外部JSライブラリは最小限に（アイコンにLucideを使う場合のみ許可: https://unpkg.com/lucide@latest）
- 完全なHTMLを出力してください
"""

    try:
        model = genai.GenerativeModel(
            model_name=MODEL_NAME
        )
        response = model.generate_content(design_prompt)
        gen_time = round(time.time() - gen_start, 2)
        
        html_output = response.text
        
        # マークダウンのコードブロックを除去
        if html_output.startswith("```html"):
            html_output = html_output[7:]
        if html_output.startswith("```"):
            html_output = html_output[3:]
        if html_output.endswith("```"):
            html_output = html_output[:-3]
        html_output = html_output.strip()
        
        # プレースホルダーを置換
        design_tokens = f"入力={response.usage_metadata.prompt_token_count}, 出力={response.usage_metadata.candidates_token_count}, 合計={response.usage_metadata.total_token_count}"
        html_output = html_output.replace("{{ DESIGN_TOKENS }}", design_tokens)
        html_output = html_output.replace("{{DESIGN_TOKENS}}", design_tokens)
        html_output = html_output.replace("{DESIGN_TOKENS}", design_tokens)
        
        html_output = html_output.replace("{{ DESIGN_TIME }}", str(gen_time))
        html_output = html_output.replace("{{DESIGN_TIME}}", str(gen_time))
        html_output = html_output.replace("{DESIGN_TIME}", str(gen_time))
        
        # DESIGN_PROMPTは長いのでエスケープして置換
        escaped_prompt = html_module.escape(design_prompt[:3000] + "...")
        html_output = html_output.replace("{{ DESIGN_PROMPT }}", escaped_prompt)
        html_output = html_output.replace("{{DESIGN_PROMPT}}", escaped_prompt)
        html_output = html_output.replace("{DESIGN_PROMPT}", escaped_prompt)
        
        print(f"  ✓ Full evolve HTML generated ({gen_time}s)")
        print(f"    Design tokens: {response.usage_metadata.total_token_count}")
        
        return html_output, {
            'design_tokens': response.usage_metadata.total_token_count,
            'design_time': gen_time,
            'design_prompt': design_prompt
        }
        
    except Exception as e:
        import traceback
        print(f"  ⚠ Full evolve generation failed: {e}")
        traceback.print_exc()
        return None, None


# =============================================================================
# 4. HTML生成
# =============================================================================

def generate_archive_html(news_data, current_id, prev_link, generation_count, new_feature=None, new_style=None, new_layout=None):
    """テンプレートからアーカイブHTMLを生成"""
    print("Step 3: Generating archive HTML...")
    
    # テンプレートを読み込み
    template_path = os.path.join(ARCHIVE_DIR, 'TEMPLATE.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    display_date = news_data['meta']['display_date']
    mood_keyword = news_data.get('mood_keyword', 'neutral')
    
    # 新しいスタイルがあればそれを使用、なければdefault
    theme_id = new_style['id'] if new_style else 'default'
    
    # 新しいレイアウトがあればそれを使用、なければdefault
    layout_id = new_layout['id'] if new_layout else 'default'
    
    # プレースホルダーを置換
    html = html_template
    html = html.replace('{ARTICLE_ID}', current_id)
    html = html.replace('{DISPLAY_DATE}', html_module.escape(display_date))
    html = html.replace('{GENERATION_NUMBER}', str(generation_count))
    html = html.replace('{MOOD_KEYWORD}', html_module.escape(mood_keyword))
    html = html.replace('{THEME_ID}', html_module.escape(theme_id))
    html = html.replace('{LAYOUT_ID}', html_module.escape(layout_id))
    html = html.replace('{DAILY_SUMMARY}', html_module.escape(news_data.get('daily_summary', '')))
    
    # ニュースカードの静的生成
    news_cards_html = ""
    for index, news in enumerate(news_data.get('top_news', [])):
        news_cards_html += f'''
        <article class="news-card" data-index="{index}">
          <div class="news-number">{str(index + 1).zfill(2)}</div>
          <div class="news-content">
            <h3 class="news-title">
              <a href="{html_module.escape(news.get('link', '#'))}" target="_blank" rel="noopener noreferrer">
                {html_module.escape(news.get('title', ''))}
              </a>
            </h3>
            <p class="news-description">{html_module.escape(news.get('description', ''))}</p>
          </div>
        </article>
        '''
    html = html.replace('{NEWS_CARDS}', news_cards_html)
    
    # Previous link
    if prev_link and prev_link != '#':
        prev_id = prev_link.split('/')[-1].replace('.html', '')
        if prev_id.replace('-', '').replace('_', '').isalnum():
            prev_link_html = f'''<a href="./{prev_id}.html" class="nav-link">
                <i data-lucide="chevron-left" style="width: 18px; height: 18px;"></i>
                前のニュース
            </a>'''
        else:
            prev_link_html = ''
    else:
        prev_link_html = ''
    html = html.replace('{PREV_ARTICLE_LINK}', prev_link_html)
    html = html.replace('{PREV_LINK}', prev_link if prev_link else '#')
    
    # メタ情報
    meta = news_data['meta']
    html = html.replace('{FETCH_TIME_JST}', html_module.escape(meta.get('fetch_time_jst', '')))
    html = html.replace('{ARTICLE_COUNT}', str(meta.get('article_count', 0)))
    html = html.replace('{MODEL_NAME}', html_module.escape(meta.get('model_name', '')))
    
    summary_tokens = meta.get('summary_tokens', {})
    html = html.replace('{SUMMARY_TOKENS}', 
        f"入力={summary_tokens.get('input', 0)}, 出力={summary_tokens.get('output', 0)}, 合計={summary_tokens.get('total', 0)}")
    html = html.replace('{SUMMARY_TIME}', str(meta.get('summary_generation_time_sec', 0)))
    html = html.replace('{TOTAL_PROCESSING_TIME}', str(meta.get('total_processing_time_sec', 0)))
    
    # プロンプト
    html = html.replace('{SUMMARY_PROMPT}', html_module.escape(meta.get('summary_prompt', '')))
    
    # 拡張プロンプト
    feature_meta = f"【新機能プロンプト】\n{meta.get('feature_prompt', 'N/A')}\n\n【トークン】{meta.get('feature_tokens', 'N/A')}"
    style_meta = f"【新スタイルプロンプト】\n{meta.get('style_prompt', 'N/A')}\n\n【トークン】{meta.get('style_tokens', 'N/A')}"
    layout_meta = f"【新レイアウトプロンプト】\n{meta.get('layout_prompt', 'N/A')}\n\n【トークン】{meta.get('layout_tokens', 'N/A')}"
    
    html = html.replace('{FEATURE_PROMPT}', html_module.escape(feature_meta))
    html = html.replace('{STYLE_PROMPT}', html_module.escape(style_meta))
    html = html.replace('{LAYOUT_PROMPT}', html_module.escape(layout_meta))
    
    # 進化ログ
    new_feature_name = new_feature['name'] if new_feature else 'なし（既存機能を使用）'
    new_style_name = new_style['name'] if new_style else 'デフォルト'
    new_layout_name = new_layout['name'] if new_layout else 'クラシック'
    html = html.replace('{NEW_FEATURE_NAME}', html_module.escape(new_feature_name))
    html = html.replace('{NEW_STYLE_NAME}', html_module.escape(new_style_name))
    html = html.replace('{NEW_LAYOUT_NAME}', html_module.escape(new_layout_name))
    
    print(f"  ✓ Archive HTML generated")
    return html


# =============================================================================
# 5. 履歴ページ生成
# =============================================================================

def generate_history_page(history):
    """履歴一覧HTMLを生成"""
    print("Step 4: Generating history page...")
    
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
    <link rel="stylesheet" href="./styles/base.css">
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        .history-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 1.5rem;
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }}
        .history-card {{
            background: var(--morpho-bg-card);
            border: 1px solid var(--morpho-border-color);
            border-radius: 16px;
            padding: 1.5rem;
            transition: all 0.2s ease;
        }}
        .history-card:hover {{
            transform: translateY(-4px);
            box-shadow: var(--morpho-shadow-lg);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
        }}
        .card-date {{
            font-family: var(--morpho-font-mono);
            font-size: 0.85rem;
            color: var(--morpho-text-secondary);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .card-mood {{
            background: var(--morpho-accent-gradient);
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        .card-summary {{
            color: var(--morpho-text-secondary);
            font-size: 0.9rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }}
        .card-meta {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1rem;
            font-size: 0.8rem;
            color: var(--morpho-text-secondary);
        }}
        .meta-item {{
            display: flex;
            align-items: center;
            gap: 0.25rem;
        }}
        .card-actions {{
            display: flex;
            gap: 0.5rem;
        }}
        .btn-view, .btn-data {{
            flex: 1;
            padding: 0.5rem;
            border-radius: 8px;
            text-align: center;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            transition: all 0.2s ease;
        }}
        .btn-view {{
            background: var(--morpho-accent-gradient);
            color: white;
        }}
        .btn-view:hover {{
            transform: scale(1.02);
        }}
        .btn-data {{
            background: var(--morpho-bg-primary);
            color: var(--morpho-text-primary);
            border: 1px solid var(--morpho-border-color);
        }}
        .btn-data:hover {{
            border-color: var(--morpho-accent-primary);
        }}
        .page-header {{
            text-align: center;
            padding: 2rem;
        }}
        .page-header h1 {{
            font-size: 2rem;
            background: var(--morpho-accent-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        .stats {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 1rem;
        }}
        .stat {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--morpho-accent-primary);
        }}
        .stat-label {{
            font-size: 0.8rem;
            color: var(--morpho-text-secondary);
        }}
    </style>
</head>
<body>
    <header class="morpho-header">
        <div class="morpho-header-content">
            <div class="morpho-logo">
                <h1>🦋 MorphoNews</h1>
                <span>Archive</span>
            </div>
            <nav class="morpho-nav">
                <a href="./index.html">
                    <i data-lucide="home" style="width: 18px; height: 18px;"></i>
                    最新
                </a>
                <a href="./settings.html">
                    <i data-lucide="settings" style="width: 18px; height: 18px;"></i>
                    設定
                </a>
            </nav>
        </div>
    </header>
    
    <div class="page-header">
        <h1>📚 ニュースアーカイブ</h1>
        <p style="color: var(--morpho-text-secondary); margin-top: 0.5rem;">
            AIが進化させてきたニュースの記録
        </p>
        <div class="stats">
            <div class="stat">
                <div class="stat-value">{len(sorted_entries)}</div>
                <div class="stat-label">アーカイブ数</div>
            </div>
        </div>
    </div>
    
    <main class="history-grid">
        {entries_html}
    </main>
    
    <script>
        document.addEventListener('DOMContentLoaded', () => {{
            if (typeof lucide !== 'undefined') {{
                lucide.createIcons();
            }}
        }});
    </script>
</body>
</html>"""

    history_path = os.path.join(PUBLIC_DIR, "history.html")
    with open(history_path, 'w', encoding='utf-8') as f:
        f.write(history_html)
    
    print(f"  ✓ History page generated")


# =============================================================================
# メイン処理
# =============================================================================

if __name__ == "__main__":
    try:
        print(f"=== MorphoNews Generator ===")
        print(f"Mode: {GENERATION_MODE}")
        print(f"Model: {MODEL_NAME}")
        print()
        
        # タイムスタンプID
        timestamp_id = datetime.now(JST).strftime("%Y-%m-%d_%H%M")
        
        # 1. 履歴のロードと前のリンク取得
        history = load_history()
        prev_link = get_prev_link(timestamp_id, history)
        generation_count = len(history.get('entries', [])) + 1
        
        # 2. ニュース取得
        daily_content = fetch_and_summarize_news(timestamp_id)
        mood_keyword = daily_content.get('mood_keyword', 'neutral')
        
        # 3. モードに応じた生成処理
        new_feature = None
        new_style = None
        new_layout = None
        design_meta = None
        html_output = None
        
        if GENERATION_MODE == "full-evolve":
            # 完全自律型進化モード：HTML全体をAIで生成
            print("\n🧬 FULL EVOLVE MODE: AI-driven complete redesign")
            html_output, design_meta = generate_full_evolve_html(
                daily_content, 
                timestamp_id, 
                prev_link, 
                generation_count
            )
            
            if html_output is None:
                print("⚠ Full evolve failed, falling back to template mode")
                html_output = generate_archive_html(
                    daily_content, timestamp_id, prev_link, generation_count
                )
            else:
                # TOTAL_TIMEプレースホルダーを置換
                total_time = round(
                    daily_content['meta']['total_fetch_time_sec'] + 
                    daily_content['meta']['summary_generation_time_sec'] +
                    (design_meta.get('design_time', 0) if design_meta else 0), 2
                )
                html_output = html_output.replace("{{ TOTAL_TIME }}", str(total_time))
                html_output = html_output.replace("{{TOTAL_TIME}}", str(total_time))
                html_output = html_output.replace("{TOTAL_TIME}", str(total_time))
        
        elif GENERATION_MODE == "ai":
            # AIモード：機能・スタイル・レイアウトを個別生成
            new_feature = generate_new_feature(mood_keyword, timestamp_id)
            new_style = generate_new_style(mood_keyword, timestamp_id)
            new_layout = generate_new_layout(mood_keyword, timestamp_id, prev_link, generation_count)
            
            # アーカイブHTML生成前にメタデータを追加
            if new_feature:
                daily_content['meta']['feature_prompt'] = new_feature.get('prompt', '')
                daily_content['meta']['feature_tokens'] = f"入力={new_feature['tokens']['input']}, 出力={new_feature['tokens']['output']}, 合計={new_feature['tokens']['total']}"
            if new_style:
                daily_content['meta']['style_prompt'] = new_style.get('prompt', '')
                daily_content['meta']['style_tokens'] = f"入力={new_style['tokens']['input']}, 出力={new_style['tokens']['output']}, 合計={new_style['tokens']['total']}"
            if new_layout:
                daily_content['meta']['layout_prompt'] = new_layout.get('prompt', '')
                daily_content['meta']['layout_tokens'] = f"入力={new_layout['tokens']['input']}, 出力={new_layout['tokens']['output']}, 合計={new_layout['tokens']['total']}"

            html_output = generate_archive_html(
                daily_content, 
                timestamp_id, 
                prev_link, 
                generation_count,
                new_feature,
                new_style,
                new_layout
            )
        
        elif GENERATION_MODE != "news-only":
            # モジュラーモード：テンプレートベース
            html_output = generate_archive_html(
                daily_content, 
                timestamp_id, 
                prev_link, 
                generation_count
            )
        
        # 4. HTML保存
        if html_output:
            # アーカイブ保存
            os.makedirs(ARCHIVE_DIR, exist_ok=True)
            archive_filename = f"{timestamp_id}.html"
            archive_path = os.path.join(ARCHIVE_DIR, archive_filename)
            with open(archive_path, "w", encoding="utf-8") as f:
                f.write(html_output)
            
            # index.html リダイレクト
            index_path = os.path.join(PUBLIC_DIR, "index.html")
            redirect_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Redirecting to MorphoNews...</title>
    <meta http-equiv="refresh" content="0; url=./archives/{archive_filename}">
    <style>body{{background:#f8fafc;color:#6366f1;font-family:system-ui;display:flex;justify-content:center;align-items:center;height:100vh;margin:0;flex-direction:column;gap:1rem;}}</style>
</head>
<body>
    <p>🦋 Loading MorphoNews ({timestamp_id})...</p>
    <p><a href="./archives/{archive_filename}" style="color:#8b5cf6;">Click here if not redirected.</a></p>
</body>
</html>"""
            with open(index_path, "w", encoding="utf-8") as f:
                f.write(redirect_html)
            
            print(f"\n✅ Success! Archived to {archive_path}")
        else:
            print(f"\n✅ Success! News data saved (news-only mode)")
        
        # 5. 履歴更新
        if GENERATION_MODE != "news-only":
            # メタデータを更新
            base_time = daily_content['meta']['total_fetch_time_sec'] + daily_content['meta']['summary_generation_time_sec']
            if design_meta:
                base_time += design_meta.get('design_time', 0)
            daily_content['meta']['total_processing_time_sec'] = round(base_time, 2)
            
            base_tokens = daily_content['meta']['summary_tokens']['total']
            if design_meta:
                base_tokens += design_meta.get('design_tokens', 0)
            daily_content['meta']['total_tokens'] = base_tokens
            
            entry_data = {
                'id': timestamp_id,
                'fetch_time_jst': daily_content['meta']['fetch_time_jst'],
                'mood_keyword': daily_content.get('mood_keyword', 'Unknown'),
                'daily_summary': daily_content.get('daily_summary', ''),
                'model_name': daily_content['meta']['model_name'],
                'total_tokens': daily_content['meta']['total_tokens'],
                'total_processing_time_sec': daily_content['meta']['total_processing_time_sec'],
                'generation_mode': GENERATION_MODE,
                'new_feature': new_feature['id'] if new_feature else None,
                'new_style': new_style['id'] if new_style else None,
                'new_layout': new_layout['id'] if new_layout else None
            }
            
            # full-evolveモードの場合、design_metaを追加
            if design_meta:
                entry_data['design_tokens'] = design_meta.get('design_tokens', 0)
                entry_data['design_time'] = design_meta.get('design_time', 0)
            
            history = add_history_entry(history, entry_data)
            save_history(history)
            
            # 履歴ページ生成
            generate_history_page(history)
            
            # JSONデータを更新
            if design_meta:
                daily_content['meta']['design_tokens'] = design_meta.get('design_tokens', 0)
                daily_content['meta']['design_time'] = design_meta.get('design_time', 0)
                daily_content['design_prompt'] = design_meta.get('design_prompt', '')
            save_json(os.path.join(DATA_DIR, f"{timestamp_id}.json"), daily_content)
        
        print(f"\n📊 Summary:")
        print(f"  - Mode: {GENERATION_MODE}")
        print(f"  - Total tokens: {daily_content['meta'].get('total_tokens', 'N/A')}")
        print(f"  - Processing time: {daily_content['meta'].get('total_processing_time_sec', 'N/A')}s")
        if new_feature:
            print(f"  - New feature: {new_feature['name']}")
        if new_style:
            print(f"  - New style: {new_style['name']}")
        if new_layout:
            print(f"  - New layout: {new_layout['name']}")
        if design_meta:
            print(f"  - Design tokens: {design_meta.get('design_tokens', 'N/A')}")
            print(f"  - Design time: {design_meta.get('design_time', 'N/A')}s")

    except Exception as e:
        import traceback
        print(f"Fatal Error: {e}")
        traceback.print_exc()
        exit(1)
