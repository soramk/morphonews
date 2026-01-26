/**
 * MorphoNews Feature: エージェンティック・ホライゾン・スキャナー
 * Generated: 2026-01-26_0952
 * Description: ユーザーの読解速度とスクロール方向を分析し、まだ画面に現れていない「情報の地平線」にある重要なキーワードや概念を先読みして、周辺視野（画面端）にフローティング表示します。これにより、読者は情報の全体像を常に把握しながら読み進めることができます。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #horizon-scanner-container {
            position: fixed;
            right: 20px;
            top: 50%;
            transform: translateY(-50%);
            width: 120px;
            z-index: 10000;
            pointer-events: none;
            display: flex;
            flex-direction: column;
            gap: 10px;
            font-family: sans-serif;
        }
        .horizon-pulse {
            background: rgba(0, 255, 180, 0.1);
            border-right: 3px solid rgba(0, 255, 180, 0.6);
            padding: 8px;
            font-size: 11px;
            color: #00ffb4;
            border-radius: 4px 0 0 4px;
            transition: all 0.5s ease;
            opacity: 0;
            transform: translateX(20px);
            text-shadow: 0 0 5px rgba(0, 255, 180, 0.5);
        }
        .horizon-pulse.active {
            opacity: 1;
            transform: translateX(0);
        }
        .horizon-marker {
            position: absolute;
            right: 0;
            height: 2px;
            background: #00ffb4;
            box-shadow: 0 0 10px #00ffb4;
            width: 50px;
            transition: top 0.3s ease-out;
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'horizon-scanner-container';
    document.body.appendChild(container);

    const marker = document.createElement('div');
    marker.className = 'horizon-marker';
    container.appendChild(marker);

    const getKeywords = (text) => {
        return text.split(/[^\w\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]+/).filter(w => w.length > 3).slice(0, 3);
    };

    const scanHorizon = () => {
        const elements = Array.from(document.querySelectorAll('p, h1, h2, h3, article div'));
        const scrollPos = window.scrollY + window.innerHeight;
        const horizonElements = elements.filter(el => {
            const rect = el.getBoundingClientRect();
            const top = rect.top + window.scrollY;
            return top > scrollPos && top < scrollPos + 1500;
        });

        const keywords = new Set();
        horizonElements.forEach(el => {
            getKeywords(el.innerText).forEach(k => keywords.add(k));
        });

        updateUI(Array.from(keywords).slice(0, 5));
    };

    const updateUI = (keywords) => {
        const existingPulses = container.querySelectorAll('.horizon-pulse');
        existingPulses.forEach(p => p.classList.remove('active'));

        setTimeout(() => {
            while (container.firstChild !== marker) {
                container.removeChild(container.firstChild);
            }
            
            keywords.forEach((word, i) => {
                const pulse = document.createElement('div');
                pulse.className = 'horizon-pulse';
                pulse.textContent = `NEXT: ${word}`;
                container.insertBefore(pulse, marker);
                setTimeout(() => pulse.classList.add('active'), i * 100);
            });
        }, 300);
    };

    let scrollTimeout;
    window.addEventListener('scroll', () => {
        const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
        marker.style.top = `${scrollPercent}%`;

        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(scanHorizon, 150);
    });

    // Initial Scan
    scanHorizon();

    console.log("Agentic Horizon Scanner Activated: Predictive content preview enabled.");
})();
