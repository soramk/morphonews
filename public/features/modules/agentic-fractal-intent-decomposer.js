/**
 * MorphoNews Feature: エージェンティック・フラクタル意志分解マップ
 * Generated: 2026-02-26_0955
 * Description: 記事の内容からエージェントの「思考の深層」をフラクタル構造で動的に分解・可視化します。各ノードは記事から抽出された意図の階層を表します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #fractal-intent-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 400px;
            background: rgba(10, 15, 25, 0.9);
            border: 1px solid #00f3ff;
            border-radius: 12px;
            z-index: 9999;
            color: #fff;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.3);
            backdrop-filter: blur(8px);
            transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        #fractal-intent-container.minimized {
            transform: translateY(360px);
        }
        .fractal-header {
            padding: 10px;
            background: rgba(0, 243, 255, 0.1);
            border-bottom: 1px solid rgba(0, 243, 255, 0.3);
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .fractal-title {
            font-size: 0.85rem;
            font-weight: bold;
            color: #00f3ff;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        #fractal-canvas-mount {
            flex-grow: 1;
            position: relative;
        }
        .intent-node {
            position: absolute;
            background: rgba(0, 243, 255, 0.1);
            border: 1px solid rgba(0, 243, 255, 0.4);
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 0.7rem;
            pointer-events: none;
            white-space: nowrap;
            animation: fractal-fade-in 0.5s ease-out forwards;
        }
        @keyframes fractal-fade-in {
            from { opacity: 0; transform: scale(0.8); }
            to { opacity: 1; transform: scale(1); }
        }
        .fractal-line {
            position: absolute;
            background: linear-gradient(90deg, #00f3ff, transparent);
            height: 1px;
            transform-origin: left center;
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'fractal-intent-container';
    container.innerHTML = `
        <div class="fractal-header" onclick="this.parentElement.classList.toggle('minimized')">
            <span class="fractal-title">Intent Decomposition Map</span>
            <span style="font-size: 10px">▼</span>
        </div>
        <div id="fractal-canvas-mount"></div>
    `;
    document.body.appendChild(container);

    const mount = container.querySelector('#fractal-canvas-mount');

    const keywords = ['構造的分析', '因果律の特定', '隠れた文脈の抽出', '潜在的リスク', '経済的共鳴', '社会的インパクト', '技術的特異点', '倫理的境界', '行動パターンの予測', '情報エントロピー'];

    function generateFractal(x, y, angle, depth, parentNode) {
        if (depth > 3) return;

        const node = document.createElement('div');
        node.className = 'intent-node';
        node.textContent = keywords[Math.floor(Math.random() * keywords.length)];
        node.style.left = `${x}px`;
        node.style.top = `${y}px`;
        mount.appendChild(node);

        const childrenCount = 2 + Math.floor(Math.random() * 2);
        for (let i = 0; i < childrenCount; i++) {
            const newAngle = angle + (Math.random() - 0.5) * 1.5;
            const length = 70 / (depth + 1);
            const nx = x + Math.cos(newAngle) * length * 1.5;
            const ny = y + Math.sin(newAngle) * length * 1.5;

            const line = document.createElement('div');
            line.className = 'fractal-line';
            line.style.width = `${length * 1.5}px`;
            line.style.left = `${x}px`;
            line.style.top = `${y}px`;
            line.style.transform = `rotate(${newAngle}rad)`;
            mount.appendChild(line);

            setTimeout(() => {
                generateFractal(nx, ny, newAngle, depth + 1, node);
            }, depth * 200 + i * 100);
        }
    }

    function updateMap() {
        mount.innerHTML = '';
        generateFractal(20, 150, 0, 0, null);
    }

    let lastText = '';
    setInterval(() => {
        const currentArticle = document.querySelector('article') || document.body;
        const text = currentArticle.innerText.substring(0, 100);
        if (text !== lastText) {
            lastText = text;
            updateMap();
        }
    }, 5000);

    updateMap();
})();
