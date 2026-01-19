/**
 * MorphoNews Feature: 統合収束レンズ
 * Generated: 2026-01-19_0950
 * Description: 今日のムード『Convergence（収束）』に基づき、ページ内に点在する関連性の高いニュース情報を一つの視点に集約する機能。ユーザーが特定の記事に注目した際、ページ全体の関連情報を中心点へ視覚的に引き寄せ、文脈の統合を促します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .convergence-lens-overlay {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            pointer-events: none; z-index: 9999;
            transition: opacity 0.5s ease;
        }
        .convergence-node-line {
            stroke: rgba(100, 200, 255, 0.4);
            stroke-width: 2;
            stroke-dasharray: 5, 5;
            animation: dash 1s linear infinite;
        }
        @keyframes dash {
            to { stroke-dashoffset: -10; }
        }
        .news-card.converging {
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0, 150, 255, 0.5);
            z-index: 10000 !important;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .news-card.converging-source {
            filter: brightness(0.7) blur(1px);
            transform: scale(0.95);
            opacity: 0.6;
        }
        #convergence-toggle {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1a1a2e;
            color: #00d2ff;
            border: 1px solid #00d2ff;
            padding: 10px 15px;
            border-radius: 20px;
            cursor: pointer;
            z-index: 10001;
            font-family: monospace;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
    `;
    document.head.appendChild(style);

    const svgContainer = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svgContainer.classList.add('convergence-lens-overlay');
    document.body.appendChild(svgContainer);

    const toggleBtn = document.createElement('button');
    toggleBtn.id = 'convergence-toggle';
    toggleBtn.textContent = 'CONVERGENCE: OFF';
    document.body.appendChild(toggleBtn);

    let isActive = false;

    toggleBtn.addEventListener('click', () => {
        isActive = !isActive;
        toggleBtn.textContent = `CONVERGENCE: ${isActive ? 'ON' : 'OFF'}`;
        if (!isActive) clearConvergence();
    });

    function getRelatedItems(target) {
        const cards = Array.from(document.querySelectorAll('.news-card'));
        const targetText = target.innerText.toLowerCase();
        // シンプルなキーワード抽出（4文字以上の共通単語）
        const words = targetText.match(/\w{4,}/g) || [];
        
        return cards.filter(card => {
            if (card === target) return false;
            const cardText = card.innerText.toLowerCase();
            return words.some(word => cardText.includes(word));
        });
    }

    function clearConvergence() {
        document.querySelectorAll('.news-card').forEach(c => {
            c.classList.remove('converging', 'converging-source');
        });
        while (svgContainer.firstChild) svgContainer.removeChild(svgContainer.firstChild);
    }

    document.addEventListener('mouseover', (e) => {
        if (!isActive) return;
        const card = e.target.closest('.news-card');
        if (!card) return;

        clearConvergence();
        card.classList.add('converging');

        const related = getRelatedItems(card);
        const targetRect = card.getBoundingClientRect();
        const targetX = targetRect.left + targetRect.width / 2;
        const targetY = targetRect.top + targetRect.height / 2;

        related.forEach(item => {
            item.classList.add('converging-source');
            const rect = item.getBoundingClientRect();
            const sourceX = rect.left + rect.width / 2;
            const sourceY = rect.top + rect.height / 2;

            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', sourceX);
            line.setAttribute('y1', sourceY);
            line.setAttribute('x2', targetX);
            line.setAttribute('y2', targetY);
            line.classList.add('convergence-node-line');
            svgContainer.appendChild(line);
        });
    });

    document.addEventListener('scroll', () => {
        if (isActive) clearConvergence();
    });
})();
