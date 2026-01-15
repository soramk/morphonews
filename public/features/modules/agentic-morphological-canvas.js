/**
 * MorphoNews Feature: アジェンティック・モーフォロジカル・キャンバス
 * Generated: 2026-01-16_0124
 * Description: ニュース記事を単なるリストから脱却させ、ユーザーの意図や「トランスフォーメーション」のムードに合わせて幾何学的（円形、螺旋、波状）な空間配置へと再構成します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .morpho-canvas-container {
            position: relative;
            width: 100%;
            min-height: 80vh;
            transition: all 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            perspective: 1000px;
            margin-top: 50px;
        }
        .morpho-node {
            position: absolute;
            width: 200px;
            padding: 15px;
            background: var(--bg-card, #ffffff);
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: all 1s ease-in-out;
            cursor: pointer;
            overflow: hidden;
            z-index: 10;
        }
        .morpho-node:hover {
            z-index: 100;
            transform: scale(1.1) !important;
            border-color: #3498db;
        }
        .morpho-controls {
            position: fixed;
            bottom: 20px;
            right: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
            background: rgba(255,255,255,0.8);
            padding: 10px;
            border-radius: 30px;
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        }
        .morpho-btn {
            padding: 8px 15px;
            border: none;
            border-radius: 20px;
            background: #2c3e50;
            color: white;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.3s;
        }
        .morpho-btn:hover { background: #34495e; }
        .morpho-node h4 { margin: 0 0 8px 0; font-size: 14px; color: #2c3e50; }
        .morpho-node p { margin: 0; font-size: 11px; color: #7f8c8d; line-height: 1.4; }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.className = 'morpho-canvas-container';
    const mainContent = document.querySelector('main') || document.body;
    mainContent.appendChild(container);

    const articles = Array.from({length: 12}).map((_, i) => ({
        title: `News Transform ${i + 1}`,
        summary: `最新の進化型ニュースフィード。トランスフォーメーション・モードにより情報の形が変化します。 (#${i + 1})`
    }));

    const nodes = articles.map(data => {
        const div = document.createElement('div');
        div.className = 'morpho-node';
        div.innerHTML = `<h4>${data.title}</h4><p>${data.summary}</p>`;
        container.appendChild(div);
        return div;
    });

    function transform(type) {
        const width = container.offsetWidth;
        const height = container.offsetHeight || 600;
        const centerX = width / 2 - 100;
        const centerY = height / 2 - 50;

        nodes.forEach((node, i) => {
            let x, y, rotate = 0;
            const t = i / nodes.length;

            switch(type) {
                case 'circle':
                    const radius = Math.min(width, height) * 0.35;
                    x = centerX + radius * Math.cos(t * 2 * Math.PI);
                    y = centerY + radius * Math.sin(t * 2 * Math.PI);
                    rotate = t * 360;
                    break;
                case 'spiral':
                    const spiralRadius = t * Math.min(width, height) * 0.45;
                    x = centerX + spiralRadius * Math.cos(t * 4 * Math.PI);
                    y = centerY + spiralRadius * Math.sin(t * 4 * Math.PI);
                    rotate = t * 720;
                    break;
                case 'wave':
                    x = (width * 0.8) * t + (width * 0.1) - 100;
                    y = centerY + Math.sin(t * 10) * 150;
                    rotate = Math.cos(t * 10) * 20;
                    break;
                default: // grid
                    const cols = 4;
                    x = (i % cols) * 220 + (width - cols * 220) / 2;
                    y = Math.floor(i / cols) * 120 + 50;
                    rotate = 0;
            }
            node.style.transform = `translate3d(${x}px, ${y}px, 0) rotate(${rotate}deg)`;
        });
    }

    const controls = document.createElement('div');
    controls.className = 'morpho-controls';
    ['Grid', 'Circle', 'Spiral', 'Wave'].forEach(mode => {
        const btn = document.createElement('button');
        btn.className = 'morpho-btn';
        btn.innerText = mode;
        btn.onclick = () => transform(mode.toLowerCase());
        controls.appendChild(btn);
    });
    document.body.appendChild(controls);

    // Initial transformation
    setTimeout(() => transform('grid'), 100);

    window.addEventListener('resize', () => transform('grid'));
})();
