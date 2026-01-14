/**
 * MorphoNews Feature: 実用的データ抽出パネル
 * Generated: 2026-01-14_1003
 * Description: 記事内の数値、日付、固有名詞を自動抽出し、クイックリファレンスとしてサイドパネルに一覧表示します。ニュースの内容を定量的に素早く把握することを助けます。
 */
(function() {
    const styles = `
        #morpho-data-extractor {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            width: 240px;
            max-height: 80vh;
            background: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 9999;
            font-family: sans-serif;
            display: flex;
            flex-direction: column;
            transition: transform 0.3s ease;
        }
        #morpho-data-extractor.collapsed {
            transform: translateY(-50%) translateX(210px);
        }
        #morpho-data-header {
            background: #f8f9fa;
            padding: 10px;
            font-weight: bold;
            font-size: 12px;
            border-bottom: 1px solid #eee;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        #morpho-data-content {
            padding: 10px;
            overflow-y: auto;
            font-size: 11px;
            color: #333;
        }
        .data-group {
            margin-bottom: 12px;
        }
        .data-label {
            color: #666;
            font-weight: bold;
            margin-bottom: 4px;
            text-transform: uppercase;
            font-size: 10px;
            border-left: 3px solid #007bff;
            padding-left: 5px;
        }
        .data-item {
            padding: 2px 0;
            border-bottom: 1px dotted #eee;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .data-item:hover {
            background: #f0f7ff;
            cursor: help;
        }
    `;

    const styleTag = document.createElement('style');
    styleTag.textContent = styles;
    document.head.appendChild(styleTag);

    const container = document.createElement('div');
    container.id = 'morpho-data-extractor';
    container.className = 'collapsed';

    const header = document.createElement('div');
    header.id = 'morpho-data-header';
    header.innerHTML = '<span>📊 Data Insights</span><span id="toggle-arrow">◀</span>';
    header.onclick = () => {
        container.classList.toggle('collapsed');
        document.getElementById('toggle-arrow').textContent = container.classList.contains('collapsed') ? '◀' : '▶';
    };

    const content = document.createElement('div');
    content.id = 'morpho-data-content';
    
    container.appendChild(header);
    container.appendChild(content);
    document.body.appendChild(container);

    const extractData = () => {
        const text = document.body.innerText;
        
        // Regex patterns
        const patterns = {
            "数値・統計": /\d+(?:\.\d+)?(?:%|万人|億円|ドル|km|kg)/g,
            "日付・時間": /(?:20\d{2}年|\d{1,2}月\d{1,2}日|\d{1,2}:\d{2})/g,
            "固有名詞候補": /[A-Z][a-z]{3,}|[\u4E00-\u9FFF]{2,4}(?:氏|社|市|国)/g
        };

        content.innerHTML = '';

        for (const [label, regex] of Object.entries(patterns)) {
            const matches = [...new Set(text.match(regex) || [])].slice(0, 8);
            if (matches.length > 0) {
                const group = document.createElement('div');
                group.className = 'data-group';
                group.innerHTML = `<div class="data-label">${label}</div>`;
                matches.forEach(m => {
                    const item = document.createElement('div');
                    item.className = 'data-item';
                    item.textContent = m;
                    item.title = `本文中の "${m}"`;
                    group.appendChild(item);
                });
                content.appendChild(group);
            }
        }

        if (content.innerHTML === '') {
            content.innerHTML = '<div style="color:#999">データを抽出中...</div>';
        }
    };

    // Initial extraction and update on content changes
    extractData();
    const observer = new MutationObserver(extractData);
    observer.observe(document.body, { childList: true, subtree: true, characterData: true });

    console.log("MorphoNews: Agentic-Data-Extractor initialized.");
})();
