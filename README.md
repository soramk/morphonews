# 🦋 MorphoNews

An AI-driven, self-evolving web page powered by GitHub Actions. MorphoNews automatically aggregates global IT news, summarizes it into Japanese, and continuously redesigns its own UI/UX by rewriting its HTML/CSS code daily. A living experiment in autonomous frontend evolution.

GitHub Actionsで駆動する、AI主導の自己進化型Webページ。MorphoNewsは世界のITニュースを自動収集して日本語に要約し、さらにHTML/CSSコードを毎日書き換えることで自身のUI/UXを継続的に再設計します。自律的なフロントエンド進化の実験プロジェクトです。

## ✨ 特徴

- **📰 自動ニュース収集**: ITmedia、Qiita、TechCrunch、The Hacker Newsから最新ニュースを自動取得
- **🤖 AI要約**: Gemini AIが日本語でトレンドを要約し、注目ニュースを3選ピックアップ
- **🎨 自己進化UI**: 毎回異なるムードに合わせてHTML/CSSを完全自動生成
- **📚 アーカイブ機能**: 過去の全ニュースを履歴一覧ページから閲覧可能
- **📊 透明性**: AIプロンプト、トークン使用量、処理時間を全て公開

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
│       └── daily_update.yml    # GitHub Actions自動実行設定
├── public/
│   ├── index.html              # リダイレクト用（最新版へ転送）
│   ├── history.html            # 履歴一覧ページ
│   ├── history.json            # 履歴データ（詳細メタデータ含む）
│   ├── archives/               # 生成されたHTMLアーカイブ
│   │   └── YYYY-MM-DD_HHMM.html
│   └── data/                   # ニュースデータJSON
│       └── YYYY-MM-DD_HHMM.json
├── scripts/
│   ├── generator.py            # メイン生成スクリプト
│   └── requirements.txt        # Python依存関係
└── README.md
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

1. リポジトリのSettings → Secrets and variables → Actions
2. `OPENAI_API_KEY` にGemini APIキーを設定
3. GitHub Pagesを有効化（Source: GitHub Actions）

## 📅 更新スケジュール

毎日 日本時間 8:00 (UTC 23:00) に自動実行されます。
手動実行も可能（Actions → Run workflow）。

## 📜 ライセンス

MIT License
