/**
 * MorphoNews Feature: エージェンティック・構造的エントロピー加速器
 * Generated: 2026-02-23_0958
 * Description: 既存の静的なニュース構造を意図的に破壊し、情報を動的な断片へと分解。情報の秩序を一度リセットすることで、予期せぬ接続や新たな解釈の可能性を視覚化する破壊的インターフェース。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .entropy-active .news-item, .entropy-active article, .entropy-active .card {
            transition: transform 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55), opacity 0.5s !important;
            position: relative !important;
            z-index: 1000;
        }
        #entropy-controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            background: #ff3e00;
            color: white;
            padding: 15px;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            font-weight: bold;
            font-size: 10px;
            text-align: center;
            user-select: none;
            border: 2px solid white;
            animation: pulse-red 2s infinite;
        }
        @keyframes pulse-red {
            0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 62, 0, 0.7); }
            70% { transform: scale(1.1); box-shadow: 0 0 0 15px rgba(255, 62, 0, 0); }
            100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 62, 0, 0); }
        }
        .entropy-fragment {
            pointer-events: none;
            filter: blur(1px) contrast(1.2);
        }
    `;
    document.head.appendChild(style);

    const controls = document.createElement('div');
    controls.id = 'entropy-controls';
    controls.innerText = 'SHATTER';
    document.body.appendChild(controls);

    let isShattered = false;

    const accelerateEntropy = () => {
        const elements = document.querySelectorAll('article, .news-item, .card, h1, h2, p');
        document.body.classList.add('entropy-active');

        elements.forEach((el, index) => {
            if (isShattered) {
                el.style.transform = 'none';
                el.style.opacity = '1';
                el.classList.remove('entropy-fragment');
            } else {
                const randomX = (Math.random() - 0.5) * 400;
                const randomY = (Math.random() - 0.5) * 400;
                const randomRotate = (Math.random() - 0.5) * 90;
                const randomScale = 0.5 + Math.random();
                
                el.style.transform = `translate(${randomX}px, ${randomY}px) rotate(${randomRotate}deg) scale(${randomScale})`;
                el.style.opacity = (0.3 + Math.random() * 0.7).toString();
                el.classList.add('entropy-fragment');
            }
        });

        isShattered = !isShattered;
        controls.innerText = isShattered ? 'RESTORE' : 'SHATTER';
        controls.style.background = isShattered ? '#007bff' : '#ff3e00';
    };

    controls.addEventListener('click', accelerateEntropy);

    // Disruptive background noise effect on movement
    document.addEventListener('mousemove', (e) => {
        if (isShattered) {
            const elements = document.querySelectorAll('.entropy-fragment');
            const limit = 10;
            elements.forEach((el, i) => {
                if (i > limit) return;
                const rect = el.getBoundingClientRect();
                const dx = e.clientX - rect.left;
                const dy = e.clientY - rect.top;
                const dist = Math.sqrt(dx*dx + dy*dy);
                if (dist < 200) {
                    el.style.transform += ` translate(${(dx/dist)*5}px, ${(dy/dist)*5}px)`;
                }
            });
        }
    });
})();
