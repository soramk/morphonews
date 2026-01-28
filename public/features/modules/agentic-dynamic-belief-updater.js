/**
 * MorphoNews Feature: エージェンティック・ダイナミック・ビリーフ・アップデーター
 * Generated: 2026-01-28_0946
 * Description: 記事の内容がユーザーの既存知識や予測にどのような影響を与えるかを、確率的な「ビリーフ（確信度）モデル」として可視化し、情報の受容プロセスをエージェントが支援します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #belief-updater-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 300px;
            background: rgba(15, 23, 42, 0.95);
            color: #f1f5f9;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 16px;
            font-family: 'Inter', sans-serif;
            box-shadow: 0 10px 25px rgba(0,0,0,0.3);
            z-index: 10000;
            backdrop-filter: blur(8px);
            transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
        }
        #belief-updater-container:hover { transform: scale(1.02); }
        .belief-header {
            font-size: 0.85rem;
            font-weight: bold;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            color: #38bdf8;
        }
        .belief-header::before {
            content: '●';
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }
        .belief-track {
            height: 8px;
            background: #1e293b;
            border-radius: 4px;
            margin: 15px 0;
            position: relative;
            overflow: hidden;
        }
        .belief-bar {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #818cf8);
            width: 50%;
            transition: width 0.8s ease-out;
        }
        .belief-labels {
            display: flex;
            justify-content: space-between;
            font-size: 0.7rem;
            color: #94a3b8;
        }
        .belief-controls {
            margin-top: 15px;
            border-top: 1px solid #334155;
            padding-top: 10px;
        }
        .belief-control-group {
            margin-bottom: 10px;
        }
        .belief-control-group label {
            display: block;
            font-size: 0.7rem;
            margin-bottom: 4px;
            color: #cbd5e1;
        }
        input[type="range"] {
            width: 100%;
            cursor: pointer;
        }
        .belief-insight {
            font-size: 0.75rem;
            font-style: italic;
            color: #94a3b8;
            margin-top: 10px;
            line-height: 1.4;
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'belief-updater-container';
    container.innerHTML = `
        <div class="belief-header">BELIEF UPDATE AGENT</div>
        <div class="belief-labels">
            <span>懐疑的</span>
            <span>確信</span>
        </div>
        <div class="belief-track">
            <div id="belief-bar" class="belief-bar"></div>
        </div>
        <div class="belief-insight" id="belief-insight">
            記事のコンテキストを解析中... 確率モデルを初期化しています。
        </div>
        <div class="belief-controls">
            <div class="belief-control-group">
                <label>あなたの初期信頼度</label>
                <input type="range" id="prior-belief" min="0" max="100" value="50">
            </div>
            <div class="belief-control-group">
                <label>情報の証拠強度 (エージェント推定)</label>
                <input type="range" id="evidence-strength" min="0" max="100" value="70">
            </div>
        </div>
    `;
    document.body.appendChild(container);

    const priorInput = document.getElementById('prior-belief');
    const evidenceInput = document.getElementById('evidence-strength');
    const beliefBar = document.getElementById('belief-bar');
    const insightText = document.getElementById('belief-insight');

    const updateBelief = () => {
        const prior = parseInt(priorInput.value) / 100;
        const strength = parseInt(evidenceInput.value) / 100;
        
        // Simplified Bayesian-like update simulation
        // Posterior = (Prior * Strength) / (Prior * Strength + (1-Prior)*(1-Strength))
        const denominator = (prior * strength) + ((1 - prior) * (1 - strength));
        const posterior = denominator === 0 ? 0.5 : (prior * strength) / denominator;
        
        const percentage = Math.round(posterior * 100);
        beliefBar.style.width = `${percentage}%`;

        let insight = "";
        if (percentage > 80) insight = "この情報はあなたの認識を強力に裏付けています。知識の固定化が進んでいます。";
        else if (percentage > 50) insight = "緩やかな確信が得られています。追加の多角的な情報を探す価値があります。";
        else if (percentage > 20) insight = "既存の知見と対立する可能性があります。批判的思考を維持してください。";
        else insight = "情報の信憑性または既知事実との乖離が著しいです。エージェントは再検証を推奨します。";

        insightText.textContent = insight;
    };

    priorInput.addEventListener('input', updateBelief);
    evidenceInput.addEventListener('input', updateBelief);

    // Initial analysis simulation
    setTimeout(() => {
        const textContent = document.body.innerText;
        const complexity = Math.min(100, textContent.length / 100);
        evidenceInput.value = Math.max(30, 100 - complexity); // Simple heuristic
        updateBelief();
    }, 1500);
})();
