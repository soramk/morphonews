/**
 * MorphoNews Feature: エージェンティック・キュリオシティ・スカウト
 * Generated: 2026-01-13_1719
 * Description: ユーザーの読了状況とスクロール速度を自律的に監視し、次に興味を持つであろう関連セクションを動的に予測・提案するエージェントを配置します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #curiosity-scout-root {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 99999;
            font-family: sans-serif;
        }
        .scout-sphere {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 10px 25px rgba(99, 102, 241, 0.5);
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            position: relative;
        }
        .scout-sphere:hover { transform: scale(1.1) rotate(15deg); }
        .scout-sphere::before {
            content: '✨';
            font-size: 24px;
        }
        .scout-pulse {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            background: #6366f1;
            opacity: 0.6;
            animation: scout-ping 2s infinite;
        }
        @keyframes scout-ping {
            0% { transform: scale(1); opacity: 0.6; }
            100% { transform: scale(1.8); opacity: 0; }
        }
        .scout-panel {
            position: absolute;
            bottom: 70px;
            right: 0;
            width: 260px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 16px;
            padding: 16px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
            transform: translateY(20px);
            opacity: 0;
            pointer-events: none;
            transition: all 0.3s ease;
        }
        .scout-panel.visible {
            transform: translateY(0);
            opacity: 1;
            pointer-events: auto;
        }
        .scout-title {
            font-size: 11px;
            font-weight: bold;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 8px;
        }
        .scout-prediction {
            font-size: 13px;
            color: #1e293b;
            line-height: 1.5;
            margin-bottom: 12px;
            padding: 8px;
            background: #f8fafc;
            border-radius: 8px;
            border-left: 3px solid #a855f7;
        }
        .scout-action {
            display: block;
            width: 100%;
            padding: 8px;
            background: #6366f1;
            color: white;
            text-align: center;
            border-radius: 6px;
            font-size: 12px;
            text-decoration: none;
            font-weight: 600;
            transition: background 0.2s;
        }
        .scout-action:hover { background: #4f46e5; }
    `;
    document.head.appendChild(style);

    const root = document.createElement('div');
    root.id = 'curiosity-scout-root';
    root.innerHTML = `
        <div class="scout-panel" id="scout-panel">
            <div class="scout-title">Agentic Prediction</div>
            <div class="scout-prediction" id="scout-prediction">Analyzing your curiosity...</div>
            <a href="#" class="scout-action" id="scout-jump">Jump to insight</a>
        </div>
        <div class="scout-sphere" id="scout-trigger">
            <div class="scout-pulse"></div>
        </div>
    `;
    document.body.appendChild(root);

    const panel = document.getElementById('scout-panel');
    const trigger = document.getElementById('scout-trigger');
    const predictionText = document.getElementById('scout-prediction');
    const jumpBtn = document.getElementById('scout-jump');

    let targets = [];
    const refreshTargets = () => {
        targets = Array.from(document.querySelectorAll('h2, h3, article section, .news-item')).map(el => ({
            el: el,
            text: el.innerText.substring(0, 40).replace(/\n/g, '') + '...',
            top: el.offsetTop
        }));
    };

    const updatePrediction = () => {
        const currentScroll = window.scrollY + (window.innerHeight / 2);
        const futureTargets = targets.filter(t => t.top > currentScroll + 200);

        if (futureTargets.length > 0) {
            const next = futureTargets[0];
            predictionText.textContent = `次にあなたが興味を持つのは「${next.text}」のセクションだと予測しました。`;
            jumpBtn.onclick = (e) => {
                e.preventDefault();
                window.scrollTo({ top: next.el.offsetTop - 80, behavior: 'smooth' });
                panel.classList.remove('visible');
            };
        } else {
            predictionText.textContent = '現在のコンテキストを全て把握しました。素晴らしい読解力です。';
            jumpBtn.style.display = 'none';
        }
    };

    trigger.addEventListener('click', () => {
        refreshTargets();
        updatePrediction();
        panel.classList.toggle('visible');
    });

    // Autonomous scout behavior: Pings when user stops scrolling
    let scrollTimer;
    window.addEventListener('scroll', () => {
        clearTimeout(scrollTimer);
        scrollTimer = setTimeout(() => {
            if (Math.random() > 0.7) {
                refreshTargets();
                updatePrediction();
                panel.classList.add('visible');
                setTimeout(() => panel.classList.remove('visible'), 6000);
            }
        }, 3000);
    });
})();
