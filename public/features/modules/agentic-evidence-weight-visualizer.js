/**
 * MorphoNews Feature: 実証的証拠ウェイト・ビジュアライザー
 * Generated: 2026-01-18_0951
 * Description: ニュース記事内の数値、統計、固有名詞、引用文の密度を動的に解析し、客観的情報量が多いセクションを強調・ナビゲートします。効率的な情報収集（Pragmatism）を支援します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .morpho-evidence-high { border-left: 4px solid #3b82f6 !important; padding-left: 12px !important; background-color: rgba(59, 130, 246, 0.05) !important; transition: all 0.3s ease; }
        .morpho-data-tag { font-size: 0.7rem; color: #3b82f6; font-weight: bold; background: #dbeafe; padding: 2px 6px; border-radius: 4px; margin-right: 8px; vertical-align: middle; }
        #morpho-pragmatic-dock {
            position: fixed; right: 20px; top: 50%; transform: translateY(-50%);
            display: flex; flex-direction: column; gap: 6px; z-index: 10000; background: rgba(255,255,255,0.9); padding: 10px; border-radius: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 1px solid #eee;
        }
        .morpho-nav-dot {
            width: 10px; height: 10px; border-radius: 50%; background: #cbd5e1; cursor: pointer; border: none; transition: 0.2s;
        }
        .morpho-nav-dot:hover { background: #3b82f6; transform: scale(1.3); }
        .morpho-nav-dot.active { background: #3b82f6; box-shadow: 0 0 8px rgba(59, 130, 246, 0.6); }
    `;
    document.head.appendChild(style);

    const analyzePragmatism = () => {
        const targets = document.querySelectorAll('p, article div, .news-content');
        const dock = document.createElement('div');
        dock.id = 'morpho-pragmatic-dock';
        let foundHighDensity = false;

        targets.forEach((el, index) => {
            if (el.textContent.length < 30) return;

            // Evidence signals: numbers, dates, currency, percentages, proper nouns (quotes), symbols
            const matches = el.textContent.match(/(\d+|%|％|円|ドル|兆|億|万|社|「|」|『|』|:)/g) || [];
            const density = matches.length / (el.textContent.length / 50);

            if (density > 1.5) {
                foundHighDensity = true;
                el.classList.add('morpho-evidence-high');
                
                // Add small indicator tag
                const tag = document.createElement('span');
                tag.className = 'morpho-data-tag';
                tag.innerText = 'DATA DENSE';
                el.prepend(tag);

                // Add navigation dot
                const dot = document.createElement('button');
                dot.className = 'morpho-nav-dot';
                dot.title = `Jump to Evidence Section ${index}`;
                dot.onclick = () => {
                    el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    document.querySelectorAll('.morpho-nav-dot').forEach(d => d.classList.remove('active'));
                    dot.classList.add('active');
                };
                dock.appendChild(dot);
            }
        });

        if (foundHighDensity) {
            document.body.appendChild(dock);
        }
    };

    // Execute analysis when content is ready
    if (document.readyState === 'complete') {
        analyzePragmatism();
    } else {
        window.addEventListener('load', analyzePragmatism);
    }
})();
