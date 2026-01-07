import feedparser
import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# 1. RSSから記事を取得
feeds = [
    "https://techcrunch.com/feed/",
    "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml"
]

new_articles = []
for url in feeds:
    feed = feedparser.parse(url)
    for entry in feed.entries[:3]: # 各フィードから最新3件のみ
        # AIによる要約・翻訳処理
        prompt = f"""
        以下のITニュース記事を読み、日本のエンジニア向けに日本語で要約してください。
        制約：
        - 400文字程度
        - 専門用語はなるべくそのままカタカナか英語で
        - タイトルと本文を出力
        
        Title: {entry.title}
        Link: {entry.link}
        Summary: {entry.description}
        """
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        content = response.choices[0].message.content
        new_articles.append({"content": content, "link": entry.link})

# データを保存（既存データに追加する処理などは省略）
with open('public/news_data.json', 'w', encoding='utf-8') as f:
    json.dump(new_articles, f, ensure_ascii=False, indent=2)
