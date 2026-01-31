/**
 * MorphoNews Feature: エージェンティック・アーキテクチャ・リフロー・エンジン
 * Generated: 2026-01-31_0952
 * Description: ページの論理構造をリアルタイムで解析し、現在のコンテキストに最適化された階層構造へとDOMを動的に再構成（リストから階層ツリー、または論理的マトリックスへ）します。
 */
(function() {
    const STYLE_ID = 'morpho-reflow-engine-styles';
    if (document.getElementById(STYLE_ID)) return;

    const style = document.createElement('style');
    style.id = STYLE_ID;
    style.textContent = `
        .reflow-trigger {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            background: #2c3e50;
            color: #ecf0f1;
            border: 2px solid #3498db;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-family: monospace;
            font-size: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
        }
        .reflow-trigger:hover {
            background: #3498db;
            transform: scale(1.05);
        }
        .reflow-active .news-container, .reflow-active #news-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            perspective: 1000px;
        }
        .reflow-active .news-item {
            border-left: 4px solid #3498db;
            padding: 15px !important;
            background: rgba(52, 152, 219, 0.05);
            transition: transform 0.5s cubic-bezier(0.23, 1, 0.32, 1);
            transform-style: preserve-3d;
        }
        .reflow-active .news-item[data-weight="high"] {
            grid-column: span 2;
            border-left: 4px solid #e74c3c;
        }
        .reflow-node-meta {
            font-size: 10px;
            color: #7f8c8d;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
    `;
    document.head.appendChild(style);

    const trigger = document.createElement('button');
    trigger.className = 'reflow-trigger';
    trigger.innerHTML = 'RESTRUCTURE ARCHITECTURE';
    document.body.appendChild(trigger);

    let isReflowed = false;

    const performReflow = () => {
        const container = document.querySelector('.news-container') || document.querySelector('#news-container') || document.body;
        const items = Array.from(container.querySelectorAll('.news-item, article'));

        if (!isReflowed) {
            document.body.classList.add('reflow-active');
            items.forEach((item, index) => {
                const textLength = item.innerText.length;
                const weight = textLength > 500 ? 'high' : 'normal';
                item.setAttribute('data-weight', weight);

                // Add structural metadata
                if (!item.querySelector('.reflow-node-meta')) {
                    const meta = document.createElement('div');
                    meta.className = 'reflow-node-meta';
                    meta.innerText = `Node_Idx: ${index} | Complexity: ${textLength}`;
                    item.prepend(meta);
                }
                
                // Random architectural shift
                item.style.transform = `rotateY(${Math.random() * 5 - 2.5}deg) translateZ(${weight === 'high' ? '20px' : '0px'})`;
            });
            trigger.innerText = 'REVERT ARCHITECTURE';
        } else {
            document.body.classList.remove('reflow-active');
            items.forEach(item => {
                item.removeAttribute('data-weight');
                item.style.transform = '';
                const meta = item.querySelector('.reflow-node-meta');
                if (meta) meta.remove();
            });
            trigger.innerText = 'RESTRUCTURE ARCHITECTURE';
        }
        isReflowed = !isReflowed;
    };

    trigger.addEventListener('click', performReflow);

    console.log('Agentic Architecture Reflow Engine Initialized: Ready to restructure DOM nodes based on semantic density.');
})();
