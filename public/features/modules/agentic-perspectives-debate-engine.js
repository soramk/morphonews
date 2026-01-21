/**
 * MorphoNews Feature: エージェンティック・視点討論エンジン
 * Generated: 2026-01-21_0947
 * Description: ニュース記事に対して、複数の仮想エージェント（楽観主義者、批判家、現実主義者）が独自の視点で議論を交わすシミュレーションを表示し、読者に多角的な考察を促します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .apde-container {
            margin: 20px 0;
            padding: 15px;
            background: #1e1e1e;
            color: #eee;
            border-radius: 8px;
            font-family: sans-serif;
            border-left: 4px solid #007acc;
            display: none;
        }
        .apde-active { display: block; animation: apdeFadeIn 0.5s ease; }
        @keyframes apdeFadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .apde-header { font-weight: bold; margin-bottom: 10px; color: #4db8ff; font-size: 0.9em; text-transform: uppercase; letter-spacing: 1px; }
        .apde-chat { display: flex; flex-direction: column; gap: 10px; }
        .apde-bubble {
            padding: 8px 12px;
            border-radius: 12px;
            max-width: 85%;
            font-size: 0.85em;
            line-height: 1.4;
            position: relative;
        }
        .apde-bubble-optimist { align-self: flex-start; background: #2d4a2d; border: 1px solid #4caf50; }
        .apde-bubble-critic { align-self: flex-end; background: #4a2d2d; border: 1px solid #f44336; }
        .apde-bubble-realist { align-self: center; background: #2d3e4a; border: 1px solid #2196f3; }
        .apde-label { font-size: 0.7em; margin-bottom: 3px; font-weight: bold; opacity: 0.8; }
        .apde-trigger-btn {
            margin-top: 10px;
            padding: 5px 12px;
            background: #007acc;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
            transition: background 0.3s;
        }
        .apde-trigger-btn:hover { background: #005f99; }
    `;
    document.head.appendChild(style);

    const personas = [
        { id: 'optimist', name: '楽観主義エージェント', style: 'apde-bubble-optimist', templates: ['この技術革新は、人類の可能性を根本から広げる素晴らしい一歩ですね。', '効率化が進むことで、私たちはより創造的な活動に時間を割けるようになるはずです。', '未来は明るいと確信しています。この変化を歓迎しましょう！'] },
        { id: 'critic', name: '批判的エージェント', style: 'apde-bubble-critic', templates: ['プライバシーの懸念や、倫理的なコストが見過ごされているのではないでしょうか？', '短期的な利益に目がくらみ、長期的な依存リスクを軽視しているように見えます。', '誰がこのシステムを監視するのですか？透明性が決定的に欠けています。'] },
        { id: 'realist', name: '現実主義エージェント', style: 'apde-bubble-realist', templates: ['理想と懸念のバランスをとる必要があります。実装コストが現実的かが鍵ですね。', '既存のインフラとの互換性を考えると、移行には少なくとも数年はかかるでしょう。', 'データの精度次第ですが、段階的な導入が最も賢明な判断と言えます。'] }
    ];

    function startDebate(container) {
        const chat = container.querySelector('.apde-chat');
        chat.innerHTML = '';
        let step = 0;
        const maxSteps = 4;

        const interval = setInterval(() => {
            if (step >= maxSteps) {
                clearInterval(interval);
                return;
            }
            const persona = personas[Math.floor(Math.random() * personas.length)];
            const bubble = document.createElement('div');
            bubble.className = `apde-bubble ${persona.style}`;
            bubble.innerHTML = `<div class="apde-label">${persona.name}</div>${persona.templates[Math.floor(Math.random() * persona.templates.length)]}`;
            chat.appendChild(bubble);
            container.scrollTop = container.scrollHeight;
            step++;
        }, 1500);
    }

    function init() {
        const articles = document.querySelectorAll('article, .news-item, .content-section');
        articles.forEach(article => {
            if (article.querySelector('.apde-container')) return;

            const btn = document.createElement('button');
            btn.className = 'apde-trigger-btn';
            btn.textContent = '⚡ エージェント討論を開始';
            
            const container = document.createElement('div');
            container.className = 'apde-container';
            container.innerHTML = `<div class="apde-header">Perspective Analysis Debate</div><div class="apde-chat"></div>`;
            
            btn.onclick = () => {
                container.classList.add('apde-active');
                startDebate(container);
                btn.style.display = 'none';
            };

            article.appendChild(btn);
            article.appendChild(container);
        });
    }

    // 初期実行と動的追加への対応（簡易版）
    init();
    const observer = new MutationObserver(init);
    observer.observe(document.body, { childList: true, subtree: true });
})();
