# 🦋 MorphoNews

**自己進化するAI駆動ニュースサイト**

[![GitHub Actions](https://img.shields.io/badge/Powered%20by-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini%202.0-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

MorphoNewsは、AIが毎回の実行で**新しい機能**と**新しいスタイル**を自動生成する、進化型Webアプリケーションです。世界のテックニュースを収集・要約し、自律的にUI/UXを進化させていきます。

## ✨ コンセプト：進化するWebサイト

```
┌─────────────────────────────────────────────────────────────┐
│                    🦋 Evolution Cycle                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📰 ニュース取得    →    🤖 AI要約                          │
│         ↓                                                   │
│   🆕 新機能生成     →    🎨 新スタイル生成                    │
│   (JavaScript)           (CSS Theme)                        │
│         ↓                                                   │
│   📄 HTML生成       →    🚀 デプロイ                          │
│                                                             │
│   ユーザーは過去のスタイルを自由に選択可能                      │
│   機能も個別にON/OFF可能                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 主な機能

### 📰 自動ニュース収集

- 日本・海外の主要テックニュースソースからRSS取得
- ITmedia, Qiita, TechCrunch, The Hacker News, Zenn など20+ソース
- Gemini AIによる日本語要約と注目ニュース選定

### 🧬 自己進化システム

- **新機能の自動生成**: AIが毎回新しいJSモジュールを提案・実装
- **新スタイルの自動生成**: その日のムードに合わせたCSSテーマを生成
- **モジュラー設計**: 機能とスタイルは独立したファイルで管理

### ⚙️ ユーザーカスタマイズ

- **設定ページ**: 機能のON/OFF切り替え
- **テーマ選択**: 6+のテーマから自由に選択
- **設定の永続化**: localStorageに保存

### モバイル対応

- レスポンシブデザイン
- ハンバーガーメニュー
- タッチフレンドリーなUI

## 📁 ディレクトリ構造

```text
morphonews/
├── README.md
├── docs/                         # ドキュメント
│   ├── ARCHITECTURE.md
│   ├── EVOLUTION_ARCHITECTURE.md
│   ├── FEATURES.md
│   └── ...
│
├── public/                       # 公開ファイル
│   ├── index.html               # 最新版へリダイレクト
│   ├── history.html             # 履歴一覧（検索・ソート付き）
│   ├── settings.html            # 設定ページ
│   │
│   ├── features/                # 機能モジュール
│   │   ├── features.json        # 機能メタデータ
│   │   ├── core/               # 必須機能
│   │   │   ├── loader.js       # モジュールローダー
│   │   │   └── news-renderer.js
│   │   └── modules/            # オプション機能
│   │       ├── reading-progress.js
│   │       ├── font-resize.js
│   │       ├── keyboard-nav.js
│   │       ├── style-switcher.js
│   │       └── [AI生成の機能].js
│   │
│   ├── styles/                  # スタイルモジュール
│   │   ├── styles.json          # テーマメタデータ
│   │   ├── base.css             # 共通ベーススタイル
│   │   └── themes/              # テーマ別CSS
│   │       ├── default.css
│   │       ├── ocean.css
│   │       ├── forest.css
│   │       ├── sunset.css
│   │       ├── midnight.css
│   │       ├── cherry.css
│   │       └── [AI生成のテーマ].css
│   │
│   ├── archives/                # 生成されたHTMLアーカイブ
│   │   ├── TEMPLATE.html
│   │   └── YYYY-MM-DD_HHMM.html
│   │
│   └── data/                    # ニュースデータ（JSON）
│       └── YYYY-MM-DD_HHMM.json
│
├── scripts/
│   ├── generator.py             # メイン生成スクリプト
│   └── requirements.txt
│
└── .github/
    └── workflows/
        └── daily_update.yml     # GitHub Actions設定
```

## 🔄 生成モード

MorphoNewsは3つの生成モードをサポートしています。

| 機能 | `ai` モード | `modular` モード | `news-only` モード |
|------|:-----------:|:----------------:|:------------------:|
| ニュース取得（RSS） | ✅ | ✅ | ✅ |
| AI要約生成 | ✅ | ✅ | ✅ |
| JSONデータ保存 | ✅ | ✅ | ✅ |
| 新機能生成（JS） | ✅ AI生成 | ❌ | ❌ |
| 新スタイル生成（CSS） | ✅ AI生成 | ❌ | ❌ |
| HTML生成 | ✅ | ✅ テンプレート | ❌ |
| 処理速度 | 遅い（30-60秒） | 速い（5-10秒） | 最速（数秒） |

### 🤖 `ai` モード（デフォルト）

毎回の実行で：

1. Gemini AIがニュースを分析・要約
2. **新しい機能**のアイデアを生成し、JSファイルとして保存
3. **新しいスタイル**を生成し、CSSファイルとして保存
4. テンプレートを元にHTMLを生成

```bash
export GENERATION_MODE="ai"
python scripts/generator.py
```

### 📦 `modular` モード

テンプレートベースで高速生成。新機能・新スタイルの生成はスキップ。

```bash
export GENERATION_MODE="modular"
python scripts/generator.py
```

### 📰 `news-only` モード

ニュースデータ（JSON）のみを取得・保存。HTML生成なし。

```bash
export GENERATION_MODE="news-only"
python scripts/generator.py
```

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

# 実行
python scripts/generator.py
```

### GitHub Actions設定

1. リポジトリの **Settings** → **Secrets and variables** → **Actions**
2. `OPENAI_API_KEY` にGemini APIキーを設定
3. **Settings** → **Pages** → Source: **GitHub Actions**

## � 自動実行スケジュール

GitHub Actionsにより1日3回自動実行されます：

| 時刻（JST） | 時刻（UTC） |
|-------------|-------------|
| 09:00 | 00:00 |
| 17:00 | 08:00 |
| 01:00 | 16:00 |

手動実行も可能：**Actions** → **Evolve MorphoNews** → **Run workflow**

## 📊 システム情報の透明性

各ページには以下の情報が表示されます：

- 取得日時（JST）
- 収集記事数
- 使用モデル（Gemini 2.0 Flash）
- トークン使用量
- 処理時間
- AIプロンプト全文

## 🎨 プリセットテーマ

| テーマ | 説明 |
|--------|------|
| **Default** | インディゴ＆パープルのモダンデザイン |
| **Ocean** | 深い海のブルー |
| **Forest** | 自然の緑 |
| **Sunset** | 夕焼けのオレンジ＆ピンク |
| **Midnight** | ダークモード |
| **Cherry** | 桜をイメージしたピンク |

AIモードでは、これらに加えて新しいテーマが自動生成されます。

## 📖 ドキュメント

詳細なドキュメントは [`docs/`](./docs/) フォルダを参照してください：

- [EVOLUTION_ARCHITECTURE.md](./docs/EVOLUTION_ARCHITECTURE.md) - 進化型アーキテクチャの詳細
- [FEATURES.md](./docs/FEATURES.md) - 機能一覧
- [ARCHITECTURE.md](./docs/ARCHITECTURE.md) - システム設計
- [CHANGELOG.md](./docs/CHANGELOG.md) - 変更履歴

## 🛠️ 技術スタック

- **Backend**: Python 3.10+
- **AI**: Google Gemini 2.0 Flash
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Icons**: Lucide Icons
- **Fonts**: Noto Sans JP, Fira Code
- **CI/CD**: GitHub Actions
- **Hosting**: GitHub Pages

## 📜 ライセンス

MIT License
