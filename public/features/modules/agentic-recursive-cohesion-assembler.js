/**
 * MorphoNews Feature: エージェンティック・再帰的結束アセンブラ
 * Generated: 2026-02-25_1002
 * Description: 構造的に断片化した情報をエージェントが再帰的にスキャンし、最も重要なコンテキストの断片を物理的に中心点へ収束・再構築する、視覚的情報収束エンジンです。
 */
(function() {
    const style = document.createElement('style');
    style.textContent = `
        .agentic-assembly-portal {
            position: fixed;
            bottom: 30px;
            right: 30px;
            z-index: 10001;
        }
        .assembly-trigger-btn {
            background: #0a0a0a;
            color: #00ffd5;
            border: 1px solid #00ffd5;
            padding: 12px 18px;
            font-family: 'Share Tech Mono', monospace;
            font-size: 13px;
            cursor: pointer;
            letter-spacing: 1px;
            box-shadow: 0 0 15px rgba(0, 255, 213, 0.3);
            transition: all 0.4s cubic-bezier(0.23, 1, 0.32, 1);
            text-transform: uppercase;
        }
        .assembly-trigger-btn:hover {
            background: #00ffd5;
            color: #0a0a0a;
            box-shadow: 0 0 30px rgba(0, 255, 213, 0.6);
        }
        .cohesion-fragment {
            position: fixed;
            padding: 8px 14px;
            background: rgba(0, 255, 213, 0.05);
            border-left: 3px solid #00ffd5;
            color: #e0e0e0;
            font-size: 11px;
            pointer-events: none;
            z-index: 10000;
            transition: transform 2s cubic-bezier(0.19, 1, 0.22, 1), opacity 1.8s ease-out;
            white-space: nowrap;
            backdrop-filter: blur(4px);
        }
        .cohesion-vortex {
            position: fixed;
            top: 50%;
            left: 50%;
            width: 4px;
            height: 4px;
            background: #00ffd5;
            border-radius: 50%;
            transform: translate(-50%, -50%);
            opacity: 0;
            box-shadow: 0 0 60px 20px rgba(0, 255, 213, 0.9);
            pointer-events: none;
            z-index: 9999;
            transition: opacity 0.5s ease;
        }
        .cohesion-status {
            position: fixed;
            top: 55%;
            left: 50%;
            transform: translateX(-50%);
            color: #00ffd5;
            font-family: monospace;
            font-size: 10px;
            letter-spacing: 2px;
            opacity: 0;
            pointer-events: none;
            z-index: 10002;
        }
    `;
    document.head.appendChild(style);

    const container = document.createElement('div');
    container.className = 'agentic-assembly-portal';
    const btn = document.createElement('button');
    btn.className = 'assembly-trigger-btn';
    btn.innerText = 'Run Cohesion Assembler';
    container.appendChild(btn);
    document.body.appendChild(container);

    const vortex = document.createElement('div');
    vortex.className = 'cohesion-vortex';
    document.body.appendChild(vortex);

    const status = document.createElement('div');
    status.className = 'cohesion-status';
    document.body.appendChild(status);

    let isAssembling = false;

    btn.addEventListener('click', () => {
        if (isAssembling) return;
        isAssembling = true;
        
        vortex.style.opacity = '1';
        status.innerText = 'SCANNING SEMANTIC FRAGMENTS...';
        status.style.opacity = '1';

        const elements = Array.from(document.querySelectorAll('p, h2, li')).filter(el => el.innerText.length > 20).slice(0, 25);
        const fragments = [];

        elements.forEach((el, index) => {
            const rect = el.getBoundingClientRect();
            const frag = document.createElement('div');
            frag.className = 'cohesion-fragment';
            frag.innerText = el.innerText.substring(0, 50) + '...';
            frag.style.left = `${rect.left}px`;
            frag.style.top = `${rect.top}px`;
            document.body.appendChild(frag);
            fragments.push(frag);

            setTimeout(() => {
                const centerX = window.innerWidth / 2;
                const centerY = window.innerHeight / 2;
                const moveX = centerX - rect.left - (frag.offsetWidth / 2);
                const moveY = centerY - rect.top - (frag.offsetHeight / 2);
                
                frag.style.transform = `translate(${moveX}px, ${moveY}px) scale(0.2) rotate(${Math.random() * 720}deg)`;
                frag.style.opacity = '0';
            }, 200 + (index * 80));
        });

        setTimeout(() => {
            status.innerText = 'ASSEMBLING CONTEXTUAL CORE...';
        }, 1500);

        setTimeout(() => {
            vortex.style.opacity = '0';
            status.innerText = 'COHESION COMPLETE: PERSPECTIVE SYNTHESIZED';
            setTimeout(() => {
                status.style.opacity = '0';
                fragments.forEach(f => f.remove());
                isAssembling = false;
            }, 2000);
        }, 4000);
    });
})();
