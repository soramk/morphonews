import os
import json
import html as html_module

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'data')
ARCHIVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'public', 'archives')

files_to_fix = [
    '2026-01-11_1632',
    '2026-01-11_1716',
    '2026-01-12_0114',
    '2026-01-12_1004'
]

for timestamp_id in files_to_fix:
    # Load JSON
    json_path = os.path.join(DATA_DIR, f'{timestamp_id}.json')
    html_path = os.path.join(ARCHIVE_DIR, f'{timestamp_id}.html')
    
    if not os.path.exists(json_path):
        print(f'SKIP: {timestamp_id} - JSON not found')
        continue
    if not os.path.exists(html_path):
        print(f'SKIP: {timestamp_id} - HTML not found')
        continue
    
    with open(json_path, 'r', encoding='utf-8') as f:
        news_data = json.load(f)
    
    with open(html_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Build news cards HTML
    news_cards_html = ''
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
    
    # Fix absolute paths to relative paths
    html = html.replace('href="/styles/', 'href="../styles/')
    html = html.replace('src="/features/', 'src="../features/')
    html = html.replace("themeLink.href = `/styles/themes/", "themeLink.href = `../styles/themes/")
    
    # Replace empty news-container
    if '<!-- news-renderer.js が動的に挿入 -->' in html:
        html = html.replace('<!-- news-renderer.js が動的に挿入 -->', news_cards_html.strip())
        print(f'OK: {timestamp_id} - fixed paths and added news cards')
    else:
        print(f'OK: {timestamp_id} - fixed paths (news cards already present or different format)')
    
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html)

print('Done!')
