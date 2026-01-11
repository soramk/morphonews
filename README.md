# 🦋 MorphoNews

An AI-driven, self-evolving web page powered by GitHub Actions. MorphoNews automatically aggregates global IT news, summarizes it into Japanese, and continuously redesigns its own UI/UX by rewriting its HTML/CSS code daily. A living experiment in autonomous frontend evolution.

GitHub Actionsで駆動する、AI主導の自己進化型Webページ。MorphoNewsは世界のITニュースを自動収集して日本語に要約し、さらにHTML/CSSコードを毎日書き換えることで自身のUI/UXを継続的に再設計します。自律的なフロントエンド進化の実験プロジェクトです。

## ✨ 特徴

- **📰 自動ニュース収集**: ITmedia、Qiita、TechCrunch、The Hacker Newsから最新ニュースを自動取得
- **🤖 AI要約**: Gemini AIが日本語でトレンドを要約し、注目ニュースを3選ピックアップ
- **🎨 自己進化UI**: 毎回異なるムードに合わせてHTML/CSSを完全自動生成
- **📚 アーカイブ機能**: 過去の全ニュースを履歴一覧ページから閲覧可能
- **📊 透明性**: AIプロンプト、トークン使用量、処理時間を全て公開

## 🆕 新機能 (2026-01-11)

### 設定ページとカスタマイズ機能

MorphoNewsは単なる「変化」ではなく、**明確な「進化」**とユーザー制御を目指します：

#### ⚙️ 設定ページ (NEW!)
- **機能の有効化/無効化**: 各機能を個別にオン/オフ可能
- **スタイル選択**: 6つのテーマから好みのスタイルを選択
- **設定の永続化**: すべての設定をlocalStorageに保存
- **リアルタイムプレビュー**: 設定変更をすぐに確認可能

#### 🚀 機能の進化 (Feature Evolution)
- **🎨 スタイル選択**: 6つのテーマから選べる（デフォルト、オーシャン、フォレスト、サンセット、ミッドナイト、チェリーブロッサム）
- **📊 読書進捗バー**: ページ上部に進捗を表示（設定で無効化可能）
- **🔤 文字サイズ調整**: A+/A-ボタンで70%〜150%まで調整可能（設定で無効化可能）
- **💾 設定の保存**: 選択したスタイルと文字サイズを自動保存
- **🖼️ スタイルギャラリー**: 全スタイルをプレビュー付きで一覧表示
- **📱 完全モバイル対応**: すべてのページがモバイルデバイスに最適化

#### 🎭 スタイルの変化 (Style Variation)
- 生成されたスタイルは保存され、いつでも選択可能
- ユーザーが好みのスタイルを自由に選択できる
- 過去のスタイルも利用可能

#### 🔄 実行モード
- **AIモード (デフォルト)**: 新規機能とスタイルをAIが生成
- **モジュラーモード**: テンプレートベースで高速生成
- **ニュースのみモード**: 機能/スタイル生成をスキップしてニュースのみ取得

#### ⏰ 自動実行
- GitHub Actionsが1日3回自動実行（JST 9:00, 17:00, 1:00）

詳細は [FEATURES.md](./FEATURES.md) を参照してください。

## 🔍 表示される情報

各ページには以下の詳細情報が表示されます：

| 項目 | 説明 |
|------|------|
| 取得日時 (JST) | ニュースを取得した日本時間 |
| 収集記事数 | RSSフィードから取得した記事の総数 |
| 使用モデル | 生成に使用したGemini AIモデル |
| 要約AIトークン | 要約生成に使用した入力/出力/合計トークン数 |
| デザインAIトークン | UI生成に使用した入力/出力/合計トークン数 |
| 要約生成時間 | 要約AIの処理時間（秒） |
| デザイン生成時間 | デザインAIの処理時間（秒） |
| 全体処理時間 | 全ステップの合計処理時間（秒） |
| AIプロンプト | 要約・デザイン生成に使用したプロンプト全文 |

## 📁 ディレクトリ構造

```
morphonews/
├── .github/
│   └── workflows/
│       └── daily_update.yml      # GitHub Actions自動実行設定（1日3回）
├── public/
│   ├── index.html                # リダイレクト用（最新版へ転送）
│   ├── history.html              # 履歴一覧ページ（外部CSS/JS使用）
│   ├── settings.html             # 設定ページ（NEW!）
│   ├── style-gallery.html        # スタイルギャラリーページ
│   ├── history.json              # 履歴データ（詳細メタデータ含む）
│   ├── features.json             # 機能一覧とメタデータ（NEW!）
│   ├── styles/                   # CSSファイル
│   │   ├── history.css          # history.html専用スタイル
│   │   ├── archive-base.css     # アーカイブページ共通スタイル
│   │   ├── styles.json          # スタイルメタデータ（NEW!）
│   │   └── archives/            # テーマ別CSSファイル
│   │       ├── default.css
│   │       ├── ocean.css
│   │       ├── forest.css
│   │       ├── sunset.css
│   │       ├── midnight.css
│   │       └── cherry.css
│   ├── js/                       # JavaScriptファイル
│   │   ├── history.js           # history.html専用スクリプト
│   │   └── archive-base.js      # アーカイブページ共通スクリプト（機能制御含む）
│   ├── archives/                 # 生成されたHTMLアーカイブ
│   │   ├── TEMPLATE.html        # 新規アーカイブ用テンプレート
│   │   └── YYYY-MM-DD_HHMM.html # 各日のニュースページ
│   ├── data/                     # ニュースデータJSON
│   │   └── YYYY-MM-DD_HHMM.json # プロンプト・トークン情報含む
│   └── assets/                   # 画像などのアセット
│       └── icons/
├── scripts/
│   ├── generator.py              # メイン生成スクリプト（3モード対応）
│   ├── migrate_history.py        # 履歴移行スクリプト
│   └── requirements.txt          # Python依存関係
└── README.md
```

### 🆕 新しいモジュラー構造

最近のアップデートで、CSS と JavaScript が外部ファイルに分離されました：

- **共通スタイル**: `styles/archive-base.css` - 全アーカイブページで共有
- **共通スクリプト**: `js/archive-base.js` - ユーティリティ関数とLucideアイコン初期化
- **個別カスタマイズ**: 必要に応じて `styles/archives/` と `js/archives/` に個別ファイルを配置可能
- **メタデータ**: プロンプトとトークン情報は `data/` の JSON ファイルに保存
- **テンプレート**: `archives/TEMPLATE.html` に新規ページ作成用の雛形を用意

この構造により：
- `history.html` のファイルサイズが大幅に削減
- スタイルと機能の再利用が容易に
- 過去のアーカイブに新しいスタイルを適用しやすく
- メンテナンス性と拡張性が向上

## 🚀 セットアップ

### 必要な環境

- Python 3.10+
- Gemini API キー

### ローカルでの実行

```bash
# 依存関係インストール
pip install -r scripts/requirements.txt

# 環境変数設定
export OPENAI_API_KEY="your-gemini-api-key"

# 実行（デフォルトはAIモード）
python scripts/generator.py

# 実行モード指定
export GENERATION_MODE="ai"          # AIモード（新機能とスタイル生成）
export GENERATION_MODE="modular"     # モジュラーモード（テンプレートベース）
export GENERATION_MODE="news-only"   # ニュースのみモード
```

### GitHub Actions設定

1. リポジトリのSettings → Secrets and variables → Actions
2. `OPENAI_API_KEY` にGemini APIキーを設定
3. GitHub Pagesを有効化（Source: GitHub Actions）

## 💡 使い方

### 設定ページの使用

1. ナビゲーションから「設定」をクリック
2. **機能の有効化/無効化**: トグルスイッチで各機能をオン/オフ
   - 読書進捗バー
   - 文字サイズ調整
   - スタイル選択機能
   - など
3. **スタイル選択**: お好みのテーマを選択
   - デフォルト、オーシャン、フォレスト、サンセット、ミッドナイト、チェリーブロッサム
4. 「設定を保存」ボタンをクリック

設定はブラウザのlocalStorageに保存され、次回訪問時も適用されます。

### 手動実行（GitHub Actions）

1. リポジトリの「Actions」タブを開く
2. 「Evolve MorphoNews」ワークフローを選択
3. 「Run workflow」をクリック
4. 生成モードを選択:
   - **ai**: 新機能とスタイルをAI生成（デフォルト）
   - **modular**: テンプレートベースで高速生成
   - **news-only**: ニュースのみ取得（機能/スタイル生成なし）

## 📅 更新スケジュール

1日3回、日本時間 9:00、17:00、1:00 (UTC 0:00、8:00、16:00) に自動実行されます。
手動実行も可能（Actions → Run workflow）。

## 📜 ライセンス

MIT License
