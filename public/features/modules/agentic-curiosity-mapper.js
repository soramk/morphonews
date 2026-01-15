/**
 * MorphoNews Feature: エージェンティック・キュリオシティ・マッパー
 * Generated: 2026-01-15_1000
 * Description: 閲覧中のコンテンツから「未知の探求点」を自律的に抽出し、読者の思考を深めるための問いや関連トピックを地図状に視覚化します。ユーザーの滞留時間に応じて、エージェントが次に学ぶべきルートを提案します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #curiosity-mapper-container {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            width: 200px;
            background: rgba(15, 23, 42, 0.9);
            border: 1px solid #3b82f6;
            border-radius: 12px;
            padding: 15px;
            color: #e2e8f0;
            font-family: sans-serif;
            font-size: 12px;
            z-index: 9999;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            backdrop-filter: blur(8px);
            transition: all 0.3s ease;
        }
        .curiosity-node {
            margin-bottom: 12px;
            padding: 8px;
            border-left: 2px solid #3b82f6;
            background: rgba(59, 130, 246, 0.1);
            cursor: pointer;
            transition: transform 0.2s;
        }
        .curiosity-node:hover {
            transform: translateX(-5px);
            background: rgba(59, 130, 246, 0.2);
        }
        .curiosity-label {
            font-weight: bold;
            color: #60a5fa;
            display: block;
            margin-bottom: 4px;
        }
        .curiosity-agent-status {
            font-size: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #94a3b8;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
        }
        .curiosity-agent-status::before {
            content: '';
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #10b981;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'curiosity-mapper-container';
    container.innerHTML = `
        <div class="curiosity-agent-status">Agent Analyzing...</div>
        <div id="curiosity-nodes-list"></div>
    `;
    document.body.appendChild(container);

    const analyzeContent = () => {
        const texts = Array.from(document.querySelectorAll('h1, h2, h3, p'))
            .map(el => el.innerText)
            .join(' ');
        
        const commonTerms = ['です', 'ます', 'こと', 'という', 'から'];
        const words = texts.split(/[\s、。！？]/)
            .filter(w => w.length > 3 && !commonTerms.some(c => w.includes(c)))
            .slice(0, 20);

        const uniqueWords = [...new Set(words)];
        const nodesList = document.getElementById('curiosity-nodes-list');
        nodesList.innerHTML = '';

        uniqueWords.slice(0, 4).forEach(word => {
            const node = document.createElement('div');
            node.className = 'curiosity-node';
            const questions = [
                `「${word}」の背景にある原理は？`,
                `なぜ今「${word}」が重要なのか？`,
                `「${word}」がもたらす次の変化は？`
            ];
            const randomQuestion = questions[Math.floor(Math.random() * questions.length)];
            
            node.innerHTML = `
                <span class="curiosity-label">Perspective: ${word}</span>
                <span>${randomQuestion}</span>
            `;
            node.onclick = () => {
                window.scrollTo({
                    top: Array.from(document.querySelectorAll('*')).find(el => el.innerText && el.innerText.includes(word))?.offsetTop - 100 || 0,
                    behavior: 'smooth'
                });
            };
            nodesList.appendChild(node);
        });
    };

    let debounceTimer;
    window.addEventListener('scroll', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(analyzeContent, 1500);
    });

    // Initial analysis
    setTimeout(analyzeContent, 1000);
})();
