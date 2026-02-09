/**
 * MorphoNews Feature: エージェンティック・戦略意図ビジュアライザー
 * Generated: 2026-02-09_1000
 * Description: ニュース内の主要な主体（組織、人物、概念）の潜在的な戦略的意図をエージェントが推論し、それらの力学的関係をタクティカル・マップとして動的に生成・可視化します。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        #agentic-intent-map {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 320px;
            height: 320px;
            background: rgba(10, 15, 25, 0.95);
            border: 1px solid #00f2ff;
            border-radius: 50%;
            z-index: 9999;
            box-shadow: 0 0 20px rgba(0, 242, 255, 0.3);
            overflow: hidden;
            font-family: 'Courier New', Courier, monospace;
            color: #00f2ff;
            transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            display: flex;
            align-items: center;
            justify-content: center;
            pointer-events: none;
        }
        #agentic-intent-map.active {
            pointer-events: all;
            border-radius: 12px;
            width: 400px;
            height: 400px;
            bottom: 40px;
            right: 40px;
        }
        .intent-node {
            position: absolute;
            width: 10px;
            height: 10px;
            background: #ff00ea;
            border-radius: 50%;
            box-shadow: 0 0 10px #ff00ea;
        }
        .intent-label {
            position: absolute;
            font-size: 10px;
            white-space: nowrap;
            pointer-events: none;
            text-shadow: 1px 1px 2px #000;
        }
        .intent-line {
            position: absolute;
            height: 1px;
            background: linear-gradient(90deg, transparent, #00f2ff, transparent);
            transform-origin: left center;
            opacity: 0.6;
        }
        #intent-trigger {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: #111;
            border: 2px solid #00f2ff;
            border-radius: 50%;
            cursor: pointer;
            z-index: 10000;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #00f2ff;
            animation: pulse-intent 2s infinite;
        }
        @keyframes pulse-intent {
            0% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.7); }
            70% { box-shadow: 0 0 0 15px rgba(0, 242, 255, 0); }
            100% { box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); }
        }
        .intent-scanner {
            position: absolute;
            width: 100%;
            height: 2px;
            background: rgba(0, 242, 255, 0.5);
            box-shadow: 0 0 10px #00f2ff;
            top: 0;
            animation: scan-intent 4s linear infinite;
        }
        @keyframes scan-intent {
            0% { top: 0%; }
            100% { top: 100%; }
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.id = 'agentic-intent-map';
    container.innerHTML = '<div class="intent-scanner"></div><div id="intent-content" style="position:relative;width:100%;height:100%"></div>';
    document.body.appendChild(container);

    const trigger = document.createElement('div');
    trigger.id = 'intent-trigger';
    trigger.innerHTML = 'INTENT';
    trigger.onclick = () => container.classList.toggle('active');
    document.body.appendChild(trigger);

    const intentions = [
        "Market Dominance", "Resource Acquisition", "Public Sentiment Shift",
        "Systemic Stability", "Structural Disruption", "Information Hegemony",
        "Competitive Neutralization", "Alliance Synthesis", "Paradigm Advancement"
    ];

    function extractEntities() {
        const text = document.body.innerText;
        const words = text.match(/[A-Z][a-z]{4,}/g) || [];
        const uniqueEntities = [...new Set(words)].slice(0, 8);
        return uniqueEntities.length > 2 ? uniqueEntities : ["Stakeholder-A", "Regulator-X", "Innovator-Alpha", "Legacy-Core"];
    }

    function updateMap() {
        const content = document.getElementById('intent-content');
        content.innerHTML = '';
        const entities = extractEntities();
        const centerX = 200;
        const centerY = 200;
        const radius = 120;

        const positions = entities.map((name, i) => {
            const angle = (i / entities.length) * Math.PI * 2;
            return {
                name,
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                intent: intentions[Math.floor(Math.random() * intentions.length)]
            };
        });

        positions.forEach((pos, i) => {
            const node = document.createElement('div');
            node.className = 'intent-node';
            node.style.left = `${pos.x}px`;
            node.style.top = `${pos.y}px`;
            
            const label = document.createElement('div');
            label.className = 'intent-label';
            label.style.left = `${pos.x + 15}px`;
            label.style.top = `${pos.y - 10}px`;
            label.innerHTML = `<strong>${pos.name}</strong><br><span style="color:#ff00ea">${pos.intent}</span>`;
            
            content.appendChild(node);
            content.appendChild(label);

            // Draw lines to next node for flow
            const nextPos = positions[(i + 1) % positions.length];
            const dx = nextPos.x - pos.x;
            const dy = nextPos.y - pos.y;
            const dist = Math.sqrt(dx*dx + dy*dy);
            const angle = Math.atan2(dy, dx);

            const line = document.createElement('div');
            line.className = 'intent-line';
            line.style.width = `${dist}px`;
            line.style.left = `${pos.x + 5}px`;
            line.style.top = `${pos.y + 5}px`;
            line.style.transform = `rotate(${angle}rad)`;
            content.appendChild(line);
        });

        // Add random cross-connections
        for(let j=0; j<3; j++) {
            const start = positions[Math.floor(Math.random() * positions.length)];
            const end = positions[Math.floor(Math.random() * positions.length)];
            if (start !== end) {
                const dx = end.x - start.x;
                const dy = end.y - start.y;
                const dist = Math.sqrt(dx*dx + dy*dy);
                const angle = Math.atan2(dy, dx);
                const line = document.createElement('div');
                line.className = 'intent-line';
                line.style.width = `${dist}px`;
                line.style.left = `${start.x + 5}px`;
                line.style.top = `${start.y + 5}px`;
                line.style.transform = `rotate(${angle}rad)`;
                line.style.opacity = '0.3';
                content.appendChild(line);
            }
        }
    }

    // Initial draw and update on resize/content change simulation
    setInterval(() => {
        if (container.classList.contains('active')) {
            updateMap();
        }
    }, 10000);
    
    updateMap();
})();
