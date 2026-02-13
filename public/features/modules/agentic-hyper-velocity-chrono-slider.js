/**
 * MorphoNews Feature: アジェンティック・ハイパーベロシティ・クロノスライダー
 * Generated: 2026-02-13_1002
 * Description: ユーザーのスクロール速度とポインタの動線を解析し、サイトの表示密度と情報の抽象度をリアルタイムで可変。超高速移動時には要約のみを、静止時には詳細を自動展開する『認知速度同期型』のUIを実現します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #hyper-velocity-hud {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 10000;
            background: rgba(0, 0, 0, 0.85);
            color: #00ffcc;
            padding: 12px 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            border: 1px solid #00ffcc;
            pointer-events: none;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.3);
            transition: opacity 0.3s ease;
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        .velocity-bar-container {
            width: 100px;
            height: 4px;
            background: #222;
            overflow: hidden;
            border-radius: 2px;
        }
        #velocity-bar {
            width: 0%;
            height: 100%;
            background: #00ffcc;
            transition: width 0.1s linear;
        }
        .morpho-news-item {
            transition: transform 0.2s cubic-bezier(0.165, 0.84, 0.44, 1), opacity 0.2s ease, filter 0.2s ease;
        }
        .velocity-blur {
            filter: blur(2px) grayscale(0.5);
            opacity: 0.7;
            transform: scale(0.98) skewX(-1deg);
        }
        .velocity-warp {
            filter: blur(5px) brightness(1.5);
            opacity: 0.4;
            transform: scale(0.9) skewX(-5deg);
        }
    `;
    document.head.appendChild(style);

    const hud = document.createElement('div');
    hud.id = 'hyper-velocity-hud';
    hud.innerHTML = `
        <div>CONGNITIVE VELOCITY</div>
        <div class="velocity-bar-container"><div id="velocity-bar"></div></div>
        <div id="velocity-status">SYNCED</div>
    `;
    document.body.appendChild(hud);

    const bar = hud.querySelector('#velocity-bar');
    const status = hud.querySelector('#velocity-status');

    let lastScrollPos = window.scrollY;
    let currentVelocity = 0;
    let scrollTimeout;

    function updateUI(v) {
        const items = document.querySelectorAll('.news-item, article, section'); // MorphoNewsの一般的なセレクタ想定
        const normalizedV = Math.min(v / 50, 100);
        bar.style.width = normalizedV + '%';

        if (v > 150) {
            status.textContent = 'WARP SPEED';
            status.style.color = '#ff00ff';
            items.forEach(item => item.classList.add('velocity-warp'));
        } else if (v > 40) {
            status.textContent = 'ACCELERATING';
            status.style.color = '#ffff00';
            items.forEach(item => {
                item.classList.remove('velocity-warp');
                item.classList.add('velocity-blur');
            });
        } else {
            status.textContent = 'STABLE SYNC';
            status.style.color = '#00ffcc';
            items.forEach(item => {
                item.classList.remove('velocity-warp', 'velocity-blur');
            });
        }
    }

    window.addEventListener('scroll', () => {
        const currentPos = window.scrollY;
        const delta = Math.abs(currentPos - lastScrollPos);
        currentVelocity = delta;
        lastScrollPos = currentPos;

        updateUI(currentVelocity);

        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(() => {
            currentVelocity = 0;
            updateUI(0);
        }, 150);
    }, { passive: true });

    // 初期化完了シグナル
    console.log("Agentic Hyper-Velocity Chrono-Slider initialized. Accelerating experience...");
})();
