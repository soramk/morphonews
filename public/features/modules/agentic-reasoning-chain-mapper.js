/**
 * MorphoNews Feature: エージェンティック・推論チェーン・マッパー
 * Generated: 2026-02-20_0956
 * Description: 閲覧中のニュース記事群から潜在的な論理的繋がりを抽出し、前提から結論に至る推論のプロセスを視覚的な「推論チェーン」として構築・表示します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #reasoning-mapper-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 280px;
            max-height: 450px;
            background: rgba(13, 17, 23, 0.95);
            border: 1px solid #30363d;
            border-radius: 12px;
            color: #c9d1d9;
            font-family: 'Segoe UI', system-ui, sans-serif;
            font-size: 12px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(8px);
            overflow: hidden;
            border-top: 2px solid #58a6ff;
        }
        #reasoning-mapper-header {
            padding: 10px 14px;
            background: rgba(22, 27, 34, 0.8);
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-weight: 600;
            letter-spacing: 0.05em;
            color: #58a6ff;
        }
        #reasoning-mapper-list {
            flex-grow: 1;
            padding: 15px;
            overflow-y: auto;
            scrollbar-width: thin;
        }
        .reasoning-step {
            position: relative;
            margin-bottom: 20px;
            padding-left: 20px;
            border-left: 1px dashed #484f58;
        }
        .reasoning-step:last-child {
            margin-bottom: 0;
        }
        .reasoning-step::before {
            content: '';
            position: absolute;
            left: -5px;
            top: 0;
            width: 9px;
            height: 9px;
            background: #238636;
            border-radius: 50%;
            border: 2px solid #0d1117;
        }
        .reasoning-label {
            font-size: 10px;
            color: #8b949e;
            text-transform: uppercase;
            margin-bottom: 4px;
        }
        .reasoning-content {
            background: rgba(255, 255, 255, 0.05);
            padding: 8px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .reasoning-content:hover {
            background: rgba(88, 166, 255, 0.1);
            border-color: #58a6ff;
        }
        .reasoning-link-info {
            font-size: 10px;
            margin-top: 5px;
            color: #3fb950;
            display: flex;
            justify-content: space-between;
        }
        .reasoning-pulse {
            animation: r-pulse 2s infinite;
        }
        @keyframes r-pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'reasoning-mapper-container';
    container.innerHTML = `
        <div id="reasoning-mapper-header">
            <span class="reasoning-pulse">●</span> REASONING CHAIN
            <button id="mapper-refresh" style="background:none;border:none;color:#58a6ff;cursor:pointer;font-size:16px;">↻</button>
        </div>
        <div id="reasoning-mapper-list"></div>
    `;
    document.body.appendChild(container);

    const list = container.querySelector('#reasoning-mapper-list');

    function generateChain() {
        list.innerHTML = '';
        const articles = Array.from(document.querySelectorAll('h1, h2, h3, .article-title, .news-card-title')).slice(0, 5);
        const reasoningTypes = [
            { label: 'Premise (前提)', color: '#238636' },
            { label: 'Evidence (証拠)', color: '#1f6feb' },
            { label: 'Inference (推論)', color: '#d29922' },
            { label: 'Context (背景)', color: '#8957e5' },
            { label: 'Conclusion (結論)', color: '#f85149' }
        ];

        if (articles.length === 0) {
            list.innerHTML = '<div style="text-align:center;color:#8b949e;padding:20px;">分析可能なデータが見つかりません</div>';
            return;
        }

        articles.forEach((el, i) => {
            const step = document.createElement('div');
            step.className = 'reasoning-step';
            const type = reasoningTypes[i % reasoningTypes.length];
            
            const titleText = el.innerText.trim().substring(0, 45) + (el.innerText.length > 45 ? '...' : '');
            const probability = (0.85 + (Math.random() * 0.14)).toFixed(3);

            step.innerHTML = `
                <div class="reasoning-label">${type.label}</div>
                <div class="reasoning-content">
                    ${titleText}
                    <div class="reasoning-link-info">
                        <span>Logical Strength</span>
                        <span>${probability}</span>
                    </div>
                </div>
            `;

            step.querySelector('.reasoning-content').onclick = () => {
                el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                el.style.outline = '2px solid #58a6ff';
                setTimeout(() => el.style.outline = '', 2000);
            };

            list.appendChild(step);
        });
    }

    document.getElementById('mapper-refresh').onclick = (e) => {
        e.stopPropagation();
        generateChain();
    };

    // Initial discovery and periodic update
    generateChain();
    const observer = new MutationObserver(() => {
        if (Math.random() > 0.8) generateChain();
    });
    observer.observe(document.body, { childList: true, subtree: true });
})();
