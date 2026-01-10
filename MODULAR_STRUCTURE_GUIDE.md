# MorphoNews: Modular Structure Implementation Guide

## 概要 (Overview)

このガイドは、MorphoNewsのアーカイブページをモジュラー構造に移行するための実装ガイドです。

## 実装済みの内容 (Completed Implementation)

### 1. 外部CSS/JSファイルの作成

以下のファイルを作成し、スタイルとスクリプトを外部化しました：

#### History Page用
- `public/styles/history.css` - history.html専用のスタイルシート
- `public/js/history.js` - history.html専用のJavaScript

#### Archive Pages用
- `public/styles/archive-base.css` - 全アーカイブページ共通の基本スタイル
- `public/js/archive-base.js` - 全アーカイブページ共通のユーティリティ関数

### 2. テンプレートファイル

新規アーカイブページ用のテンプレートを作成：
- `public/archives/TEMPLATE.html` - 外部CSS/JSを参照する雛形

### 3. ディレクトリ構造

```
public/
├── styles/              # CSSファイル
│   ├── history.css     # History page専用
│   ├── archive-base.css # Archives共通
│   └── archives/       # Archive個別スタイル（オプション）
├── js/                 # JavaScriptファイル
│   ├── history.js      # History page専用
│   ├── archive-base.js # Archives共通
│   └── archives/       # Archive個別スクリプト（オプション）
├── archives/
│   └── TEMPLATE.html   # 新規ページ用テンプレート
├── data/               # メタデータ（プロンプト・トークン情報含む）
└── history.html        # 外部CSS/JS使用に更新済み
```

## 利点 (Benefits)

1. **ファイルサイズの削減**: history.htmlが大幅に軽量化
2. **再利用性**: 共通スタイルを全アーカイブで共有可能
3. **メンテナンス性**: スタイル更新時に1ファイルを編集するだけ
4. **拡張性**: 新しい機能やスタイルを容易に追加可能
5. **分離**: コンテンツ（HTML）と見た目（CSS）、動作（JS）の分離

## 今後の実装方針 (Future Implementation)

### オプション1: Generator.pyを更新（推奨）

`scripts/generator.py`を更新して、新規アーカイブページ生成時に以下を実現：

1. **テンプレートベース生成**:
   ```python
   import json
   import html
   
   # TEMPLATE.htmlを読み込んでプレースホルダーを置換
   with open('public/archives/TEMPLATE.html', 'r', encoding='utf-8') as f:
       template = f.read()
   
   # データを埋め込み（HTMLエスケープ処理）
   output = template.replace('{MOOD_KEYWORD}', html.escape(news_data['mood_keyword']))
   output = output.replace('{DAILY_SUMMARY}', html.escape(news_data['daily_summary']))
   
   # ARTICLE_IDを埋め込み（外部JSONから読み込むため）
   output = output.replace('{ARTICLE_ID}', current_id)
   
   # 注意: JSONデータを直接スクリプトに埋め込むのは非推奨
   # テンプレートではfetch()を使用して外部JSONファイルから読み込む方式を採用
   ```

2. **デザインAIの役割変更**:
   - 完全なHTMLを生成する代わりに、カスタムCSSのみを生成
   - 生成されたCSSは `styles/archives/YYYY-MM-DD_HHMM.css` に保存
   - 基本デザインは `archive-base.css` を使用

3. **セキュリティベストプラクティス**:
   - ✅ ユーザー入力や外部データは必ずエスケープ処理
   - ✅ JSONデータはスクリプトに直接埋め込まず、fetch()で外部ファイルから読み込む
   - ✅ 必要な場合のみPythonの`json.dumps()`を使用（手動での文字列構築は避ける）
   - ✅ Content Security Policyの設定を検討

4. **メリット**:
   - AIの出力が安定（HTMLよりCSSのみの方が予測可能）
   - 共通構造を保ちつつ、各ページの個性を維持
   - トークン使用量の削減
   - セキュリティリスクの大幅な低減
   - データとプレゼンテーションの完全な分離

### オプション2: 過去アーカイブの移行スクリプト

既存のアーカイブを新構造に移行するスクリプトを作成：

```python
# scripts/migrate_archives.py

def extract_styles_from_html(html_content):
    """HTMLから<style>タグの内容を抽出"""
    # BeautifulSoupなどで解析
    pass

def extract_scripts_from_html(html_content):
    """HTMLから<script>タグの内容を抽出"""
    pass

def convert_to_template(html_content):
    """既存HTMLをテンプレート構造に変換"""
    pass

for archive_file in archives:
    # 各アーカイブファイルを変換
    pass
```

### オプション3: ハイブリッドアプローチ（最も柔軟）

1. **新規生成**: `generator.py`で新しいテンプレートベース生成を使用
2. **既存保持**: 過去のアーカイブはそのまま維持（レガシーサポート）
3. **段階的移行**: 必要に応じて個別に移行

## 実装例 (Implementation Examples)

### Generator.pyの更新例

```python
def generate_archive_html_modular(news_data, current_id, prev_link, display_date, generation_count):
    """モジュラー構造でアーカイブHTMLを生成（セキュアなアプローチ）"""
    
    # テンプレートを読み込み
    template_path = os.path.join('public', 'archives', 'TEMPLATE.html')
    with open(template_path, 'r', encoding='utf-8') as f:
        html_template = f.read()
    
    # HTMLエスケープが必要な値を処理
    import html as html_module
    
    # プレースホルダーを置換
    html = html_template
    html = html.replace('{MOOD_KEYWORD}', html_module.escape(news_data['mood_keyword']))
    html = html.replace('{GENERATION_NUMBER}', str(generation_count))
    html = html.replace('{DISPLAY_DATE}', html_module.escape(display_date))
    html = html.replace('{PREV_ARTICLE_ID}', prev_link.split('/')[-1].replace('.html', '') if prev_link != '#' else '')
    html = html.replace('{FETCH_TIME_JST}', html_module.escape(news_data['meta']['fetch_time_jst']))
    html = html.replace('{ARTICLE_COUNT}', str(news_data['meta']['article_count']))
    html = html.replace('{MODEL_NAME}', html_module.escape(news_data['meta']['model_name']))
    html = html.replace('{DAILY_SUMMARY}', html_module.escape(news_data['daily_summary']))
    
    # ARTICLE_IDを埋め込み（fetch()でJSONを読み込むため）
    html = html.replace('{ARTICLE_ID}', current_id)
    
    # トークン情報
    html = html.replace('{SUMMARY_INPUT_TOKENS}', str(news_data['meta']['summary_tokens']['input']))
    html = html.replace('{SUMMARY_OUTPUT_TOKENS}', str(news_data['meta']['summary_tokens']['output']))
    html = html.replace('{SUMMARY_TOTAL_TOKENS}', str(news_data['meta']['summary_tokens']['total']))
    html = html.replace('{SUMMARY_TIME}', str(news_data['meta']['summary_generation_time_sec']))
    
    # プロンプトをエスケープして埋め込み
    html = html.replace('{SUMMARY_PROMPT}', html_module.escape(news_data['meta']['summary_prompt']))
    html = html.replace('{DESIGN_PROMPT}', html_module.escape(news_data['meta'].get('design_prompt', '')))
    
    # 注意: JSONデータはdata/{current_id}.jsonに保存されており、
    # テンプレート内のfetch()で読み込まれます
    
    return html
```

### カスタムスタイル生成（オプション）

各アーカイブページに個別のスタイルが必要な場合：

```python
def generate_archive_styles(news_data, generation_count):
    """ムードに応じたカスタムCSSを生成"""
    
    mood = news_data['mood_keyword'].lower()
    
    # AIにCSSのみを生成させる
    style_prompt = f"""
    Generate CSS custom properties and mood-specific styles for a news archive page.
    Mood: {mood}
    
    Requirements:
    - Override CSS variables for colors based on mood
    - Keep the base structure from archive-base.css
    - Output only the CSS content, no HTML
    
    Example output:
    :root {{
        --accent-primary: #...;
        --accent-secondary: #...;
    }}
    
    /* Mood-specific enhancements */
    .hero h2 {{
        /* Custom styles */
    }}
    """
    
    # Gemini APIで生成
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(style_prompt)
    
    css_content = response.text.strip()
    
    # ファイルに保存
    css_path = os.path.join('public', 'styles', 'archives', f'{current_id}.css')
    with open(css_path, 'w', encoding='utf-8') as f:
        f.write(css_content)
    
    return css_path
```

## 推奨する次のステップ (Recommended Next Steps)

1. **テストページ作成**: TEMPLATE.htmlに実際のデータを埋め込んで動作確認
2. **Generator.py更新**: 上記の`generate_archive_html_modular()`を実装
3. **段階的移行**: 次回のニュース生成時に新構造を使用
4. **ドキュメント更新**: READMEに使用方法を追記

## 注意事項 (Notes)

- **既存アーカイブの保持**: 過去のアーカイブはそのまま機能し続けます
- **互換性**: 新旧両方の構造をサポート可能
- **AI生成の継続**: デザインの多様性を保つため、カスタムCSSの生成は継続推奨
- **メタデータ**: プロンプトとトークン情報は既に`data/*.json`に保存済み

## まとめ (Summary)

この実装により：
✅ history.htmlのファイルサイズが削減
✅ 共通スタイル・機能の再利用が可能に
✅ メンテナンス性と拡張性が向上
✅ 将来的な機能追加が容易に

必要に応じて`scripts/generator.py`を更新することで、新規アーカイブページも新構造で生成できます。
