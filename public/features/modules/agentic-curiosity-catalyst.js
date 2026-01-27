/**
 * MorphoNews Feature: エージェンティック・キュリオシティ・カタリスト
 * Generated: 2026-01-27_0950
 * Description: ユーザーが注目しているテキストに対し、自律型エージェントが「もし〜なら？」という仮説的問いや批判的視点を生成し、受動的な情報摂取を能動的な探求へと変容させます。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #curiosity-catalyst-container {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 99999;
            pointer-events: none;
            font-family: 'Segoe UI', Roboto, sans-serif;
        }
        .catalyst-bubble {
            background: rgba(10, 15, 25, 0.95);
            color: #00f3ff;
            border: 1px solid rgba(0, 243, 255, 0.4);
            padding: 16px;
            border-radius: 12px;
            max-width: 300px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 243, 255, 0.2);
            opacity: 0;
            transform: translateY(30px) scale(0.9);
            transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
            pointer-events: auto;
            font-size: 0.9rem;
            line-height: 1.5;
            backdrop-filter: blur(8px);
            position: relative;
            overflow: hidden;
        }
        .catalyst-bubble::before {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 4px; height: 100%;
            background: #00f3ff;
            box-shadow: 0 0 10px #00f3ff;
        }
        .catalyst-bubble.active {
            opacity: 1;
            transform: translateY(0) scale(1);
        }
        .catalyst-header {
            font-size: 0.65rem;
            text-transform: uppercase;
            color: #fff;
            opacity: 0.6;
            margin-bottom: 8px;
            display: flex;
            justify-content: space-between;
            letter-spacing: 1px;
        }
        .catalyst-typing-indicator {
            display: inline-block;
            width: 8px; height: 8px;
            background: #00f3ff;
            border-radius: 50%;
            animation: catalyst-pulse 1s infinite ease-in-out;
        }
        @keyframes catalyst-pulse {
            0%, 100% { opacity: 0.3; transform: scale(0.8); }
            50% { opacity: 1; transform: scale(1.1); }
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'curiosity-catalyst-container';
    document.body.appendChild(container);

    const bubble = document.createElement('div');
    bubble.className = 'catalyst-bubble';
    bubble.innerHTML = `
        <div class="catalyst-header">
            <span>Agentic Catalyst</span>
            <span class="catalyst-typing-indicator"></span>
        </div>
        <div id="catalyst-body">...Analyzing context...</div>
    `;
    container.appendChild(bubble);

    const prompts = [
        "この事象の『10年後の派生効果』を想像すると、どのような産業が生まれているでしょうか？",
        "この記事の結論を逆転させた場合、どのような論理的根拠が考えられますか？",
        "この記事が『隠している情報』があるとしたら、それは誰にとって都合の悪いことでしょうか？",
        "このトレンドが過激化した場合、社会の最小単位である『家庭』にはどのような変化が起きますか？",
        "あなたがこのニュースの当事者だとしたら、最初に行う『防御的アクション』は何ですか？",
        "この情報を別の文化圏（例えば北欧や東南アジア）に移植したとき、全く異なる解釈は可能ですか？",
        "この記事の背景にある『テクノロジーの限界』は何だと思いますか？",
        "もしあなたがこの問題を解決するAIエージェントなら、どのデータセットを最優先で参照しますか？"
    ];

    let activeTimer = null;
    let currentTarget = null;

    const showCatalyst = (e) => {
        const target = e.target.closest('p, h1, h2, li, blockquote');
        if (!target || target === currentTarget) return;
        
        currentTarget = target;
        clearTimeout(activeTimer);
        bubble.classList.remove('active');

        activeTimer = setTimeout(() => {
            const textContent = target.innerText.trim();
            if (textContent.length < 20) return;

            const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];
            const body = document.getElementById('catalyst-body');
            body.textContent = randomPrompt;
            bubble.classList.add('active');
        }, 1500);
    };

    const hideCatalyst = () => {
        bubble.classList.remove('active');
        currentTarget = null;
        clearTimeout(activeTimer);
    };

    document.addEventListener('mouseover', showCatalyst);
    document.addEventListener('scroll', () => {
        if (bubble.classList.contains('active')) hideCatalyst();
    }, { passive: true });

    console.log("MorphoNews: Agentic Curiosity Catalyst initialized.");
})();
