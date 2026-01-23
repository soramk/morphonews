/**
 * MorphoNews Feature: エージェンティック・メタモルフィック・トランジション・ポータル
 * Generated: 2026-01-23_0946
 * Description: コンテンツの階層移動やカテゴリーの切り替え時に、有機的な形状変化（モーフィング）を伴う視覚的なポータルを生成。情報の断絶を防ぎ、空間的な連続性を提供します。
 */
(function() {
    const id = 'agentic-metamorphic-transition-portal';
    if (document.getElementById(id)) return;

    const style = document.createElement('style');
    style.id = id + '-style';
    style.textContent = `
        .morph-portal-overlay {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            pointer-events: none;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .morph-portal-blob {
            width: 0vmax;
            height: 0vmax;
            background: var(--accent-color, #3498db);
            border-radius: 50%;
            filter: url('#morph-goo');
            opacity: 0;
            transition: width 0.8s cubic-bezier(0.77, 0, 0.175, 1), 
                        height 0.8s cubic-bezier(0.77, 0, 0.175, 1), 
                        opacity 0.4s ease;
        }
        .morph-portal-blob.active {
            width: 250vmax;
            height: 250vmax;
            opacity: 1;
        }
        .morph-content-mask {
            transition: opacity 0.5s ease, filter 0.5s ease;
        }
        .morph-content-mask.transitioning {
            opacity: 0.3;
            filter: blur(10px);
        }
    `;
    document.head.appendChild(style);

    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.style.display = 'none';
    svg.innerHTML = `
        <defs>
            <filter id="morph-goo">
                <feGaussianBlur in="SourceGraphic" stdDeviation="10" result="blur" />
                <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 19 -9" result="goo" />
                <feComposite in="SourceGraphic" in2="goo" operator="atop" />
            </filter>
        </defs>`;
    document.body.appendChild(svg);

    const overlay = document.createElement('div');
    overlay.className = 'morph-portal-overlay';
    const blob = document.createElement('div');
    blob.className = 'morph-portal-blob';
    overlay.appendChild(blob);
    document.body.appendChild(overlay);

    const triggerPortal = (callback) => {
        const root = document.querySelector('main') || document.body;
        root.classList.add('morph-content-mask', 'transitioning');
        
        blob.classList.add('active');
        
        setTimeout(() => {
            if (typeof callback === 'function') callback();
            setTimeout(() => {
                blob.classList.remove('active');
                root.classList.remove('transitioning');
            }, 200);
        }, 800);
    };

    // 既存のナビゲーションや特定のインタラクションをフック
    document.addEventListener('click', (e) => {
        const target = e.target.closest('a, button, .category-tag');
        if (target) {
            // 内部リンクやカテゴリ変更を想定したデモ的なトリガー
            if (target.tagName === 'A' && target.getAttribute('href').startsWith('#')) {
                e.preventDefault();
                triggerPortal(() => {
                    window.location.hash = target.getAttribute('href');
                });
            } else if (target.classList.contains('category-tag')) {
                triggerPortal();
            }
        }
    }, true);

    // 開発者用グローバルアクセス
    window.MorphoNews = window.MorphoNews || {};
    window.MorphoNews.triggerPortal = triggerPortal;

    console.log("Metamorphic Transition Portal initialized.");
})();
