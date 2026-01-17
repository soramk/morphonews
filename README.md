# 🦋 MorphoNews

**自己進化するAI駆動ニュースサイト**

[![GitHub Actions](https://img.shields.io/badge/Powered%20by-GitHub%20Actions-2088FF?logo=github-actions&logoColor=white)](https://github.com/features/actions)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini%202.0-4285F4?logo=google&logoColor=white)](https://ai.google.dev/)

MorphoNewsは、AIが毎回の実行で**新しい機能**、**新しいスタイル**、そして**新しいレイアウト**を自動生成する、進化型Webアプリケーションです。世界のテックニュースを収集・要約し、自律的にUI/UXを進化させていきます。

## ✨ コンセプト：進化するWebサイト

```
┌─────────────────────────────────────────────────────────────┐
│                    🦋 Evolution Cycle                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   📰 ニュース取得    →    🤖 AI要約                          │
│         ↓                                                   │
│   🆕 新機能生成     →    🎨 新スタイル生成 → 📐 新レイアウト生成  │
│   (JavaScript)           (CSS Theme)         (CSS Layout)   │
│         ↓                                                   │
│   📄 HTML生成       →    🚀 デプロイ                          │
│                                                             │
│   ユーザーは過去のスタイルやレイアウトを自由に選択可能            │
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

- **新機能の自動生成**: AI가 毎回新しいJSモジュールを提案・実装
- **新スタイルの自動生成**: その日のムードに合わせた配色テーマを生成
- **新レイアウトの自動生成**: グリッド構造やアニメーションを含むページ構造を生成
- **モジュラー設計**: 機能・スタイル・レイアウトは独立したファイルとして蓄積

### ⚙️ ユーザーカスタマイズ（設定ページ）

- **機能の管理**: 生成された各機能のON/OFF切り替え
- **スタイル選択**: AIが生成した多彩なテーマから選択
- **レイアウト選択**: グリッド、スタック、ニュースペーパーなど、AIが描いた構造を選択
- **設定の永続化**: ユーザーの好みをブラウザ（localStorage）に保存

### 📊 進化の透明性

- 各アーカイブページに**詳細なシステム情報**を掲載
- 要約だけでなく、**機能・スタイル・レイアウト生成に使用された全プロンプト**とトークン量を公開
- AIがどのような意図でデザインを進化させたかの「進化前ログ」を確認可能

## 📁 ディレクトリ構造

```text
morphonews/
├── public/                       # 公開ファイル
│   ├── history.html             # 履歴一覧（進化の軌跡）
│   ├── settings.html            # 設定ページ（機能・テーマ・レイアウト変更）
│   │
│   ├── features/                # 機能モジュール
│   │   ├── features.json        # 機能メタデータ
│   │   └── modules/            # AI生成のJSプラグイン
│   │
│   ├── styles/                  # スタイルモジュール
│   │   ├── styles.json          # テーマメタデータ
│   │   └── themes/              # AI生成のCSSテーマ
│   │
│   ├── layouts/                 # レイアウトモジュール
│   │   ├── layouts.json         # レイアウトメタデータ
│   │   └── [AI生成のレイアウト].css
│   │
│   ├── archives/                # 生成されたHTMLアーカイブ
│   └── data/                    # ニュースデータ（JSON）
│
├── scripts/
│   └── generator.py             # メイン生成スクリプト（AI進化エンジン）
│
└── .github/
    └── workflows/
        └── daily_update.yml     # 定期更新スケジュール
```

## 🔄 生成モード

| 機能 | `full-evolve` | `ai` モード | `modular` | `news-only` |
|------|:-----------:|:-----------:|:-----------:|:-----------:|
| ニュース取得・要約 | ✅ | ✅ | ✅ | ✅ |
| 新機能生成（JS） | ❌ | ✅ | ❌ | ❌ |
| 新スタイル生成（CSS） | ❌ | ✅ | ❌ | ❌ |
| 新レイアウト生成（CSS） | ❌ | ✅ | ❌ | ❌ |
| HTML全体再構築 | ✅ AI生成 | ❌ | ❌ | ❌ |
| HTML出力（固定テンプレート） | ❌ | ✅ | ✅ | ❌ |

### 🧬 `full-evolve` モード（完全自律進化）

テンプレートを一切使用せず、AIがその日のニュースとムードに合わせて**HTML全体構造をゼロから設計・出力**します。最も予測不能で劇的な進化を遂げるモードです。

### 🤖 `ai` モード（パーツ単位の進化 - デフォルト）

既存のテンプレート構造を維持しつつ、AIが新しい「機能(JS)」「スタイル(CSS)」「レイアウト(CSS)」を独立して生成・蓄積します。安定性と進化を両立させたモードです。

### 📦 `modular` モード

進化を停止し、蓄積された既存の機能・テーマ・レイアウトを使用して高速にニュースを生成します。

### 📰 `news-only` モード

ニュースデータ（JSON）のみを取得・保存し、Webページの生成は行いません。

## 🚀 セットアップ

- Python 3.10+
- Gemini API キー (`OPENAI_API_KEY` 環境変数として設定)

```bash
pip install -r scripts/requirements.txt
python scripts/generator.py
```

## 📅 更新スケジュール

GitHub Actionsにより1日1回自動実行されます（日本時間 9:00）。
設定により1日2回、3回、6回への切り替えも可能です。

## 🛠️ 技術スタック

- **AI**: Google Gemini 2.0 Flash (Preview)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Icons**: Lucide Icons
- **CI/CD**: GitHub Actions
- **Hosting**: GitHub Pages

## 📜 ライセンス

MIT License
