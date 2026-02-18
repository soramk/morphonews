/**
 * MorphoNews Feature: エージェンティック・仮説生成エンジン
 * Generated: 2026-02-18_1000
 * Description: 閲覧中のニュースコンテンツから重要なキーワードを自律的に抽出し、既存の事実に基づいた「もしも」の仮説シナリオを生成・提示することで、読者の批判的思考と想像力を刺激します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #agentic-hypothesis-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 300px;
            background: rgba(15, 23, 42, 0.95);
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 15px;
            color: #e2e8f0;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3), 0 0 15px rgba(59, 130, 246, 0.5);
            z-index: 10000;
            transition: all 0.5s cubic-bezier(0.4, 0, 0.2, 1);
            backdrop-filter: blur(8px);
            font-size: 13px;
            overflow: hidden;
        }
        .hypothesis-header {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
            font-weight: bold;
            color: #60a5fa;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .hypothesis-header .pulse {
            width: 8px;
            height: 8px;
            background: #60a5fa;
            border-radius: 50%;
            margin-right: 8px;
            animation: agentic-pulse 2s infinite;
        }
        .hypothesis-content {
            line-height: 1.6;
            border-left: 2px solid #334155;
            padding-left: 12px;
            margin-top: 10px;
            font-style: italic;
            color: #94a3b8;
        }
        .hypothesis-footer {
            margin-top: 12px;
            font-size: 10px;
            text-align: right;
            color: #475569;
        }
        @keyframes agentic-pulse {
            0% { transform: scale(0.8); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; }
            100% { transform: scale(0.8); opacity: 0.5; }
        }
        .hypothesis-loading {
            height: 4px;
            width: 100%;
            background: #1e293b;
            border-radius: 2px;
            overflow: hidden;
            margin-top: 10px;
        }
        .hypothesis-loading-bar {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            animation: loading-progress 10s linear infinite;
        }
        @keyframes loading-progress {
            0% { width: 0%; }
            100% { width: 100%; }
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'agentic-hypothesis-container';
    container.innerHTML = `
        <div class="hypothesis-header">
            <div class="pulse"></div>
            Hypothesis Engine
        </div>
        <div id="hypothesis-text">情報を分析中...</div>
        <div class="hypothesis-loading"><div class="hypothesis-loading-bar"></div></div>
        <div class="hypothesis-footer">AGENTIC-SHIFT ACTIVE</div>
    `;
    document.body.appendChild(container);

    const extractKeywords = () => {
        const bodyText = document.body.innerText;
        const words = bodyText.match(/[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]{3,}/g) || [];
        const freq = {};
        words.forEach(w => freq[w] = (freq[w] || 0) + 1);
        return Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 15).map(e => e[0]);
    };

    const templates = [
        "もし『{k1}』が『{k2}』と完全に統合されたら、この業界の勢力図はどう変わるでしょうか？",
        "『{k1}』の影響で『{k2}』が消失するというシナリオを想定した場合、最も恩恵を受けるのは誰か？",
        "現在語られている『{k1}』のトレンドが実は『{k2}』の隠れ蓑だとしたら、真の目的は何でしょうか？",
        "『{k1}』が加速することで、逆に『{k2}』の価値が再評価される未来はあり得るでしょうか？",
        "『{k1}』と『{k2}』の間に存在する目に見えない依存関係が断ち切られた時、何が崩壊するか？"
    ];

    const generateHypothesis = () => {
        const keywords = extractKeywords();
        if (keywords.length < 2) return;
        
        const k1 = keywords[Math.floor(Math.random() * keywords.length)];
        let k2 = keywords[Math.floor(Math.random() * keywords.length)];
        while (k1 === k2) k2 = keywords[Math.floor(Math.random() * keywords.length)];

        const template = templates[Math.floor(Math.random() * templates.length)];
        const result = template.replace('{k1}', k1).replace('{k2}', k2);

        const textElement = document.getElementById('hypothesis-text');
        textElement.style.opacity = 0;
        
        setTimeout(() => {
            textElement.innerHTML = `<div class="hypothesis-content">"${result}"</div>`;
            textElement.style.opacity = 1;
        }, 500);
    };

    // Initial run and cycle
    setTimeout(generateHypothesis, 2000);
    setInterval(generateHypothesis, 10000);

    // Interaction: Hover to freeze
    container.addEventListener('mouseenter', () => {
        document.querySelector('.hypothesis-loading-bar').style.animationPlayState = 'paused';
    });
    container.addEventListener('mouseleave', () => {
        document.querySelector('.hypothesis-loading-bar').style.animationPlayState = 'running';
    });
})();
