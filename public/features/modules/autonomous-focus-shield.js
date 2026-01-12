/**
 * MorphoNews Feature: 自律型フォーカス・シールド
 * Generated: 2026-01-12_1417
 * Description: 閲覧中のコンテンツを自律的に検知し、周囲のノイズを減光・ぼかし処理することで、現在のニュースへの没入感を最大化します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .morpho-focus-target {
            transition: opacity 0.5s ease, filter 0.5s ease, transform 0.5s ease;
            position: relative;
            z-index: 10;
        }
        .morpho-focus-dimmed {
            opacity: 0.2 !important;
            filter: blur(4px) grayscale(100%);
            transform: scale(0.98);
            pointer-events: none;
            user-select: none;
        }
        #morpho-focus-ctrl {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10001;
            background: #1a1a1a;
            color: #00ff41;
            border: 1px solid #00ff41;
            padding: 10px 15px;
            border-radius: 20px;
            font-family: monospace;
            font-size: 12px;
            cursor: pointer;
            box-shadow: 0 0 15px rgba(0,255,65,0.3);
            display: flex;
            align-items: center;
            gap: 8px;
            transition: all 0.3s ease;
        }
        #morpho-focus-ctrl:hover {
            background: #00ff41;
            color: #1a1a1a;
        }
        #morpho-focus-ctrl.active {
            background: #00ff41;
            color: #1a1a1a;
            box-shadow: 0 0 20px #00ff41;
        }
    `;
    document.head.appendChild(style);

    let isEnabled = false;
    const btn = document.createElement('button');
    btn.id = 'morpho-focus-ctrl';
    btn.innerHTML = '<span>◉</span> FOCUS SHIELD OFF';
    document.body.appendChild(btn);

    const getArticles = () => document.querySelectorAll('article, section, .news-item, .content-block');

    const updateFocus = () => {
        if (!isEnabled) return;
        
        const viewportHeight = window.innerHeight;
        const centerLine = viewportHeight / 2;
        let closestElement = null;
        let minDistance = Infinity;

        const targets = getArticles();
        if (targets.length === 0) return;

        targets.forEach(el => {
            const rect = el.getBoundingClientRect();
            const elementCenter = rect.top + rect.height / 2;
            const distance = Math.abs(centerLine - elementCenter);
            
            el.classList.add('morpho-focus-target');
            
            if (distance < minDistance) {
                minDistance = distance;
                closestElement = el;
            }
        });

        targets.forEach(el => {
            if (el === closestElement) {
                el.classList.remove('morpho-focus-dimmed');
            } else {
                el.classList.add('morpho-focus-dimmed');
            }
        });
    };

    const toggleShield = () => {
        isEnabled = !isEnabled;
        btn.classList.toggle('active');
        btn.innerHTML = isEnabled ? '<span>◉</span> FOCUS SHIELD ON' : '<span>◉</span> FOCUS SHIELD OFF';
        
        if (!isEnabled) {
            getArticles().forEach(el => {
                el.classList.remove('morpho-focus-dimmed');
            });
        } else {
            updateFocus();
        }
    };

    btn.addEventListener('click', toggleShield);
    window.addEventListener('scroll', () => {
        if (isEnabled) {
            requestAnimationFrame(updateFocus);
        }
    }, { passive: true });

    // Autonomous check every 2 seconds to handle dynamic content
    setInterval(() => {
        if (isEnabled) updateFocus();
    }, 2000);
})();
